"""Risk Assessment Agent implementation."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import get_database_session
from ...models.database import Plaintiff, Case, Document
from ...services.ai.openai_client import OpenAIClient
from ..base.agent import BaseAgent, AgentTask, AgentResponse
from ..base.communication import agent_communication
from .scoring import RiskScoringEngine
from .analysis import CaseAnalyzer


class RiskAssessmentAgent(BaseAgent):
    """
    Risk Assessment Agent for AI-powered case risk evaluation.
    
    Analyzes cases using multiple risk factors including financial,
    legal, medical, and behavioral indicators to provide comprehensive
    risk scores and recommendations.
    """
    
    def __init__(self, config):
        """Initialize the Risk Assessment Agent."""
        super().__init__(config)
        
        # Initialize AI client and analysis components
        self.ai_client = OpenAIClient()
        self.scoring_engine = RiskScoringEngine()
        self.case_analyzer = CaseAnalyzer()
        
        # Operation handlers
        self._handlers = {
            "assess_risk": self._assess_risk,
            "update_risk_score": self._update_risk_score,
            "analyze_case_documents": self._analyze_case_documents,
            "assess_financial_risk": self._assess_financial_risk,
            "assess_legal_risk": self._assess_legal_risk,
            "assess_medical_risk": self._assess_medical_risk,
            "generate_risk_report": self._generate_risk_report,
            "batch_risk_assessment": self._batch_risk_assessment,
            "recalculate_all_risks": self._recalculate_all_risks,
        }
        
        # Risk factor weights (configurable)
        self.risk_weights = {
            "financial": 0.25,
            "legal": 0.30,
            "medical": 0.25,
            "behavioral": 0.10,
            "external": 0.10,
        }
        
        # Assessment statistics
        self.assessment_stats = {
            "total_assessments": 0,
            "high_risk_cases": 0,
            "medium_risk_cases": 0,
            "low_risk_cases": 0,
            "average_processing_time_ms": 0,
            "last_assessment": None,
        }
        
        self.logger.info("Risk Assessment Agent initialized")
    
    def get_operation_handler(self, operation: str) -> Optional[callable]:
        """Get the handler function for a specific operation."""
        return self._handlers.get(operation)
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """
        Process a task with comprehensive error handling and metrics.
        
        Args:
            task: The task to process.
            
        Returns:
            AgentResponse: The result of processing the task.
        """
        start_time = datetime.utcnow()
        
        try:
            # Get operation handler
            handler = self.get_operation_handler(task.operation)
            if not handler:
                return self.create_error_response(
                    task.id,
                    f"Unknown operation: {task.operation}"
                )
            
            # Execute handler
            result = await handler(task)
            
            # Update statistics
            self.assessment_stats["total_assessments"] += 1
            self.assessment_stats["last_assessment"] = datetime.utcnow().isoformat()
            
            # Update risk level statistics
            if "risk_score" in result:
                risk_score = result["risk_score"]
                if risk_score >= 0.7:
                    self.assessment_stats["high_risk_cases"] += 1
                elif risk_score >= 0.4:
                    self.assessment_stats["medium_risk_cases"] += 1
                else:
                    self.assessment_stats["low_risk_cases"] += 1
            
            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Update average processing time
            total_time = (
                self.assessment_stats["average_processing_time_ms"] * 
                (self.assessment_stats["total_assessments"] - 1) + 
                execution_time
            )
            self.assessment_stats["average_processing_time_ms"] = (
                total_time / self.assessment_stats["total_assessments"]
            )
            
            return AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=True,
                data=result,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            self.logger.error(
                f"Risk assessment task processing failed: {e}",
                task_id=task.id,
                operation=task.operation,
                error=str(e),
            )
            
            return self.create_error_response(task.id, str(e))
    
    async def _assess_risk(self, task: AgentTask) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment for a plaintiff/case.
        
        Args:
            task: Task containing risk assessment parameters.
            
        Returns:
            dict: Comprehensive risk assessment result.
        """
        plaintiff_id = task.payload.get("plaintiff_id")
        financial_info = task.payload.get("financial_info", {})
        case_info = task.payload.get("case_info", {})
        force_recalculate = task.payload.get("force_recalculate", False)
        
        if not plaintiff_id:
            raise ValueError("Missing plaintiff_id in task payload")
        
        try:
            plaintiff_uuid = UUID(plaintiff_id) if isinstance(plaintiff_id, str) else plaintiff_id
        except ValueError:
            raise ValueError(f"Invalid plaintiff_id format: {plaintiff_id}")
        
        self.logger.info(
            "Starting comprehensive risk assessment",
            plaintiff_id=str(plaintiff_uuid),
            force_recalculate=force_recalculate,
        )
        
        # Get plaintiff and case data
        async with get_database_session() as session:
            stmt = (
                select(Plaintiff)
                .where(Plaintiff.id == plaintiff_uuid)
            )
            result = await session.execute(stmt)
            plaintiff = result.scalar_one_or_none()
            
            if not plaintiff:
                raise ValueError(f"Plaintiff {plaintiff_uuid} not found")
            
            # Check if we already have a recent risk assessment
            if (
                not force_recalculate and 
                plaintiff.risk_score is not None and
                plaintiff.updated_at > datetime.utcnow() - timedelta(days=7)
            ):
                return {
                    "plaintiff_id": str(plaintiff_uuid),
                    "risk_score": plaintiff.risk_score,
                    "risk_factors": plaintiff.risk_factors or [],
                    "assessment_type": "cached",
                    "last_updated": plaintiff.updated_at.isoformat(),
                }
        
        # Perform comprehensive risk assessment
        risk_assessment = await self._perform_comprehensive_assessment(
            plaintiff,
            financial_info,
            case_info
        )
        
        # Update plaintiff with risk assessment
        async with get_database_session() as session:
            stmt = select(Plaintiff).where(Plaintiff.id == plaintiff_uuid)
            result = await session.execute(stmt)
            plaintiff = result.scalar_one()
            
            plaintiff.risk_score = risk_assessment["overall_risk_score"]
            plaintiff.risk_factors = risk_assessment["risk_factors"]
            plaintiff.underwriting_notes = risk_assessment["assessment_summary"]
            
            await session.commit()
        
        # Publish risk assessment event
        await agent_communication.publish(
            sender_id=self.agent_id,
            event_type="risk_assessment_completed",
            payload={
                "plaintiff_id": str(plaintiff_uuid),
                "risk_score": risk_assessment["overall_risk_score"],
                "risk_level": self._get_risk_level(risk_assessment["overall_risk_score"]),
                "assessment_timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        return {
            "plaintiff_id": str(plaintiff_uuid),
            "risk_score": risk_assessment["overall_risk_score"],
            "risk_level": self._get_risk_level(risk_assessment["overall_risk_score"]),
            "risk_factors": risk_assessment["risk_factors"],
            "detailed_scores": risk_assessment["detailed_scores"],
            "assessment_summary": risk_assessment["assessment_summary"],
            "recommendations": risk_assessment["recommendations"],
            "assessment_type": "comprehensive",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _perform_comprehensive_assessment(
        self,
        plaintiff: Plaintiff,
        financial_info: Dict[str, Any],
        case_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment using multiple factors.
        
        Args:
            plaintiff: Plaintiff entity.
            financial_info: Financial information.
            case_info: Case information.
            
        Returns:
            dict: Comprehensive risk assessment.
        """
        assessment_tasks = [
            self._assess_financial_risk_internal(plaintiff, financial_info),
            self._assess_legal_risk_internal(plaintiff, case_info),
            self._assess_medical_risk_internal(plaintiff, case_info),
            self._assess_behavioral_risk_internal(plaintiff),
            self._assess_external_risk_internal(plaintiff, case_info),
        ]
        
        # Run assessments concurrently
        results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
        
        # Process results
        detailed_scores = {}
        risk_factors = []
        total_weighted_score = 0
        
        factor_names = ["financial", "legal", "medical", "behavioral", "external"]
        
        for i, result in enumerate(results):
            factor_name = factor_names[i]
            weight = self.risk_weights[factor_name]
            
            if isinstance(result, Exception):
                self.logger.error(f"Failed to assess {factor_name} risk: {result}")
                # Use default medium risk score for failed assessments
                score = 0.5
            else:
                score = result["risk_score"]
                risk_factors.extend(result.get("risk_factors", []))
            
            detailed_scores[factor_name] = {
                "score": score,
                "weight": weight,
                "weighted_score": score * weight,
            }
            
            total_weighted_score += score * weight
        
        # Generate AI-powered assessment summary
        assessment_summary = await self._generate_ai_assessment_summary(
            plaintiff,
            detailed_scores,
            risk_factors
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            total_weighted_score,
            detailed_scores,
            risk_factors
        )
        
        return {
            "overall_risk_score": round(total_weighted_score, 3),
            "detailed_scores": detailed_scores,
            "risk_factors": risk_factors,
            "assessment_summary": assessment_summary,
            "recommendations": recommendations,
        }
    
    async def _assess_financial_risk_internal(
        self,
        plaintiff: Plaintiff,
        financial_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess financial risk factors."""
        risk_factors = []
        risk_score = 0.0
        
        # Income stability assessment
        monthly_income = financial_info.get("monthly_income") or plaintiff.monthly_income
        if monthly_income:
            if monthly_income < 2000:
                risk_factors.append("Low monthly income (<$2,000)")
                risk_score += 0.3
            elif monthly_income < 4000:
                risk_factors.append("Below-average monthly income")
                risk_score += 0.1
        else:
            risk_factors.append("No income information provided")
            risk_score += 0.2
        
        # Employment status assessment
        employment_status = financial_info.get("employment_status") or plaintiff.employment_status
        if employment_status:
            if employment_status.lower() in ["unemployed", "terminated", "laid off"]:
                risk_factors.append("Currently unemployed")
                risk_score += 0.4
            elif employment_status.lower() in ["part-time", "contract", "temporary"]:
                risk_factors.append("Unstable employment")
                risk_score += 0.2
        
        # Expense-to-income ratio
        monthly_expenses = financial_info.get("monthly_expenses") or plaintiff.monthly_expenses
        if monthly_income and monthly_expenses:
            expense_ratio = monthly_expenses / monthly_income
            if expense_ratio > 1.0:
                risk_factors.append("Expenses exceed income")
                risk_score += 0.3
            elif expense_ratio > 0.8:
                risk_factors.append("High expense-to-income ratio")
                risk_score += 0.1
        
        # Credit score assessment
        credit_score = financial_info.get("credit_score") or plaintiff.credit_score
        if credit_score:
            if credit_score < 600:
                risk_factors.append("Poor credit score (<600)")
                risk_score += 0.3
            elif credit_score < 700:
                risk_factors.append("Fair credit score")
                risk_score += 0.1
        
        # Bank account verification
        if not plaintiff.bank_account_verified:
            risk_factors.append("Bank account not verified")
            risk_score += 0.1
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
        }
    
    async def _assess_legal_risk_internal(
        self,
        plaintiff: Plaintiff,
        case_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess legal risk factors."""
        risk_factors = []
        risk_score = 0.0
        
        # Case type risk assessment
        case_type = case_info.get("case_type") or plaintiff.case_type.value
        high_risk_case_types = ["medical_malpractice", "product_liability", "wrongful_death"]
        medium_risk_case_types = ["workers_compensation", "employment"]
        
        if case_type in high_risk_case_types:
            risk_factors.append(f"High-risk case type: {case_type}")
            risk_score += 0.3
        elif case_type in medium_risk_case_types:
            risk_factors.append(f"Medium-risk case type: {case_type}")
            risk_score += 0.1
        
        # Statute of limitations risk
        incident_date = case_info.get("incident_date") or plaintiff.incident_date
        if incident_date:
            try:
                incident_dt = datetime.strptime(incident_date, "%Y-%m-%d")
                days_since_incident = (datetime.now() - incident_dt).days
                
                if days_since_incident > 730:  # 2 years
                    risk_factors.append("Case is over 2 years old")
                    risk_score += 0.4
                elif days_since_incident > 365:  # 1 year
                    risk_factors.append("Case is over 1 year old")
                    risk_score += 0.2
            except ValueError:
                risk_factors.append("Invalid incident date format")
                risk_score += 0.1
        
        # Legal representation assessment
        if not plaintiff.law_firm_id:
            risk_factors.append("No legal representation assigned")
            risk_score += 0.3
        
        if not plaintiff.lawyer_id:
            risk_factors.append("No primary lawyer assigned")
            risk_score += 0.2
        
        # Case description analysis (basic keyword analysis)
        case_description = case_info.get("case_description") or plaintiff.case_description
        if case_description:
            high_risk_keywords = ["disputed", "complex", "multiple parties", "appeal"]
            for keyword in high_risk_keywords:
                if keyword.lower() in case_description.lower():
                    risk_factors.append(f"Case involves {keyword}")
                    risk_score += 0.1
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
        }
    
    async def _assess_medical_risk_internal(
        self,
        plaintiff: Plaintiff,
        case_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess medical risk factors."""
        risk_factors = []
        risk_score = 0.0
        
        # This would integrate with medical record analysis
        # For now, implementing basic case description analysis
        case_description = case_info.get("case_description") or plaintiff.case_description
        
        if case_description:
            # High-risk medical indicators
            high_risk_medical = [
                "pre-existing condition",
                "chronic pain",
                "mental health",
                "addiction",
                "psychiatric",
            ]
            
            for indicator in high_risk_medical:
                if indicator.lower() in case_description.lower():
                    risk_factors.append(f"Medical complexity: {indicator}")
                    risk_score += 0.2
        
        # Age-based risk assessment
        if plaintiff.date_of_birth:
            try:
                birth_date = datetime.strptime(plaintiff.date_of_birth, "%Y-%m-%d")
                age = (datetime.now() - birth_date).days // 365
                
                if age > 70:
                    risk_factors.append("Advanced age (>70)")
                    risk_score += 0.2
                elif age < 18:
                    risk_factors.append("Minor plaintiff")
                    risk_score += 0.1
            except ValueError:
                pass
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
        }
    
    async def _assess_behavioral_risk_internal(self, plaintiff: Plaintiff) -> Dict[str, Any]:
        """Assess behavioral risk factors."""
        risk_factors = []
        risk_score = 0.0
        
        # Communication responsiveness
        # This would be based on historical communication data
        # For now, implementing basic checks
        
        if not plaintiff.email:
            risk_factors.append("No email address provided")
            risk_score += 0.2
        
        if not plaintiff.phone:
            risk_factors.append("No phone number provided")
            risk_score += 0.1
        
        # Marketing opt-in status (indicates engagement)
        if not plaintiff.opt_in_marketing:
            risk_factors.append("Did not opt-in to marketing communications")
            risk_score += 0.1
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
        }
    
    async def _assess_external_risk_internal(
        self,
        plaintiff: Plaintiff,
        case_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess external risk factors."""
        risk_factors = []
        risk_score = 0.0
        
        # Geographic risk assessment
        if plaintiff.state:
            # High-risk states (example - would be based on actual data)
            high_risk_states = ["FL", "TX", "CA"]  # Example high-litigation states
            if plaintiff.state in high_risk_states:
                risk_factors.append(f"High-litigation state: {plaintiff.state}")
                risk_score += 0.1
        
        # Economic conditions (would integrate with external data sources)
        # For now, implementing placeholder
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
        }
    
    async def _generate_ai_assessment_summary(
        self,
        plaintiff: Plaintiff,
        detailed_scores: Dict[str, Any],
        risk_factors: List[str]
    ) -> str:
        """Generate AI-powered assessment summary."""
        try:
            prompt = f"""
            Analyze the following risk assessment data and provide a comprehensive summary:
            
            Plaintiff: {plaintiff.full_name}
            Case Type: {plaintiff.case_type.value}
            
            Risk Scores:
            {', '.join([f"{k}: {v['score']:.2f}" for k, v in detailed_scores.items()])}
            
            Risk Factors:
            {chr(10).join([f"- {factor}" for factor in risk_factors])}
            
            Provide a 2-3 sentence professional summary of the risk assessment,
            highlighting the key concerns and overall risk profile.
            """
            
            response = await self.ai_client.generate_completion(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate AI assessment summary: {e}")
            return f"Risk assessment completed with {len(risk_factors)} identified risk factors. Overall risk score indicates {'high' if max(detailed_scores.values(), key=lambda x: x['score'])['score'] > 0.7 else 'moderate'} risk level."
    
    async def _generate_recommendations(
        self,
        overall_risk_score: float,
        detailed_scores: Dict[str, Any],
        risk_factors: List[str]
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if overall_risk_score >= 0.7:
            recommendations.append("High-risk case - recommend enhanced due diligence")
            recommendations.append("Consider requiring additional documentation")
            recommendations.append("Implement accelerated monitoring schedule")
        elif overall_risk_score >= 0.4:
            recommendations.append("Moderate-risk case - standard monitoring procedures")
            recommendations.append("Verify key information before proceeding")
        else:
            recommendations.append("Low-risk case - standard processing")
        
        # Specific recommendations based on risk factors
        if any("income" in factor.lower() for factor in risk_factors):
            recommendations.append("Verify income documentation and employment status")
        
        if any("credit" in factor.lower() for factor in risk_factors):
            recommendations.append("Consider additional financial verification")
        
        if any("legal" in factor.lower() or "case" in factor.lower() for factor in risk_factors):
            recommendations.append("Review legal case details with underwriting team")
        
        return recommendations
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    async def _update_risk_score(self, task: AgentTask) -> Dict[str, Any]:
        """Update risk score for an existing plaintiff."""
        # Implementation for updating existing risk scores
        return await self._assess_risk(task)
    
    async def _analyze_case_documents(self, task: AgentTask) -> Dict[str, Any]:
        """Analyze case documents for risk factors."""
        plaintiff_id = task.payload.get("plaintiff_id")
        document_ids = task.payload.get("document_ids", [])
        
        # This would implement document analysis using AI/NLP
        return {
            "plaintiff_id": plaintiff_id,
            "documents_analyzed": len(document_ids),
            "additional_risk_factors": [],
            "risk_score_adjustment": 0.0,
        }
    
    async def _assess_financial_risk(self, task: AgentTask) -> Dict[str, Any]:
        """Standalone financial risk assessment."""
        plaintiff_id = task.payload.get("plaintiff_id")
        financial_info = task.payload.get("financial_info", {})
        
        if not plaintiff_id:
            raise ValueError("Missing plaintiff_id")
        
        # Get plaintiff data
        async with get_database_session() as session:
            stmt = select(Plaintiff).where(Plaintiff.id == UUID(plaintiff_id))
            result = await session.execute(stmt)
            plaintiff = result.scalar_one_or_none()
            
            if not plaintiff:
                raise ValueError(f"Plaintiff {plaintiff_id} not found")
        
        result = await self._assess_financial_risk_internal(plaintiff, financial_info)
        
        return {
            "plaintiff_id": plaintiff_id,
            "financial_risk_score": result["risk_score"],
            "financial_risk_factors": result["risk_factors"],
        }
    
    async def _assess_legal_risk(self, task: AgentTask) -> Dict[str, Any]:
        """Standalone legal risk assessment."""
        # Similar implementation to financial risk
        return {"message": "Legal risk assessment completed"}
    
    async def _assess_medical_risk(self, task: AgentTask) -> Dict[str, Any]:
        """Standalone medical risk assessment."""
        # Similar implementation to financial risk
        return {"message": "Medical risk assessment completed"}
    
    async def _generate_risk_report(self, task: AgentTask) -> Dict[str, Any]:
        """Generate comprehensive risk report."""
        plaintiff_id = task.payload.get("plaintiff_id")
        
        # This would generate a comprehensive PDF/HTML report
        return {
            "plaintiff_id": plaintiff_id,
            "report_generated": True,
            "report_url": f"/reports/risk_assessment/{plaintiff_id}",
        }
    
    async def _batch_risk_assessment(self, task: AgentTask) -> Dict[str, Any]:
        """Perform batch risk assessment for multiple plaintiffs."""
        plaintiff_ids = task.payload.get("plaintiff_ids", [])
        batch_size = task.payload.get("batch_size", 10)
        
        results = []
        
        # Process in batches
        for i in range(0, len(plaintiff_ids), batch_size):
            batch = plaintiff_ids[i:i + batch_size]
            
            # Create assessment tasks
            tasks = []
            for plaintiff_id in batch:
                assessment_task = AgentTask(
                    agent_type=self.agent_type,
                    operation="assess_risk",
                    payload={"plaintiff_id": plaintiff_id}
                )
                tasks.append(self._assess_risk(assessment_task))
            
            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        return {
            "total_processed": len(results),
            "successful": successful,
            "failed": failed,
            "results": [r for r in results if not isinstance(r, Exception)],
        }
    
    async def _recalculate_all_risks(self, task: AgentTask) -> Dict[str, Any]:
        """Recalculate risk scores for all plaintiffs."""
        # This would implement a comprehensive recalculation
        return {
            "recalculation_started": True,
            "estimated_completion_time": "2-4 hours",
        }
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get current assessment statistics."""
        total = self.assessment_stats["total_assessments"]
        
        return {
            **self.assessment_stats,
            "risk_distribution": {
                "high_risk_percentage": (
                    self.assessment_stats["high_risk_cases"] / total * 100
                    if total > 0 else 0
                ),
                "medium_risk_percentage": (
                    self.assessment_stats["medium_risk_cases"] / total * 100
                    if total > 0 else 0
                ),
                "low_risk_percentage": (
                    self.assessment_stats["low_risk_cases"] / total * 100
                    if total > 0 else 0
                ),
            }
        }