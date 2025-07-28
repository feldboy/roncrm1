"""Risk scoring engine for comprehensive risk calculations."""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import math


class RiskScoringEngine:
    """
    Advanced risk scoring engine for case risk assessment.
    
    Implements multiple scoring algorithms and provides
    configurable risk calculation methodologies.
    """
    
    def __init__(self):
        """Initialize the risk scoring engine."""
        self.scoring_models = {
            "financial": self._score_financial_risk,
            "legal": self._score_legal_risk,
            "medical": self._score_medical_risk,
            "behavioral": self._score_behavioral_risk,
            "external": self._score_external_risk,
        }
        
        # Risk factor impact weights
        self.risk_factor_weights = {
            "critical": 0.4,
            "high": 0.3,
            "medium": 0.2,
            "low": 0.1,
        }
    
    def calculate_composite_risk_score(
        self,
        factor_scores: Dict[str, float],
        factor_weights: Dict[str, float]
    ) -> float:
        """
        Calculate composite risk score using weighted average.
        
        Args:
            factor_scores: Individual factor risk scores.
            factor_weights: Weights for each factor.
            
        Returns:
            float: Composite risk score (0.0 to 1.0).
        """
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for factor, score in factor_scores.items():
            weight = factor_weights.get(factor, 0.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.5  # Default medium risk if no weights
        
        return min(max(total_weighted_score / total_weight, 0.0), 1.0)
    
    def _score_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score financial risk factors.
        
        Args:
            financial_data: Financial information.
            
        Returns:
            dict: Financial risk assessment.
        """
        risk_score = 0.0
        risk_factors = []
        
        # Income assessment
        monthly_income = financial_data.get("monthly_income", 0)
        if monthly_income < 1500:
            risk_score += 0.4
            risk_factors.append(("Very low income", "critical"))
        elif monthly_income < 3000:
            risk_score += 0.2
            risk_factors.append(("Low income", "medium"))
        
        # Debt-to-income ratio
        monthly_expenses = financial_data.get("monthly_expenses", 0)
        if monthly_income > 0:
            debt_ratio = monthly_expenses / monthly_income
            if debt_ratio > 1.2:
                risk_score += 0.3
                risk_factors.append(("Expenses exceed income significantly", "critical"))
            elif debt_ratio > 0.9:
                risk_score += 0.2
                risk_factors.append(("High expense-to-income ratio", "high"))
        
        # Credit score assessment
        credit_score = financial_data.get("credit_score")
        if credit_score:
            if credit_score < 550:
                risk_score += 0.3
                risk_factors.append(("Poor credit score", "high"))
            elif credit_score < 650:
                risk_score += 0.1
                risk_factors.append(("Fair credit score", "medium"))
        
        # Employment stability
        employment_status = financial_data.get("employment_status", "").lower()
        unstable_employment = [
            "unemployed", "terminated", "laid off", "part-time", "contract"
        ]
        if any(status in employment_status for status in unstable_employment):
            risk_score += 0.2
            risk_factors.append(("Unstable employment", "high"))
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_details": {
                "income_level": self._categorize_income(monthly_income),
                "debt_ratio": monthly_expenses / monthly_income if monthly_income > 0 else 0,
                "credit_tier": self._categorize_credit_score(credit_score),
            }
        }
    
    def _score_legal_risk(self, legal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score legal risk factors."""
        risk_score = 0.0
        risk_factors = []
        
        # Case type risk
        case_type = legal_data.get("case_type", "").lower()
        high_risk_cases = [
            "medical_malpractice", "product_liability", "wrongful_death", 
            "class_action", "mass_tort"
        ]
        
        if case_type in high_risk_cases:
            risk_score += 0.3
            risk_factors.append((f"High-risk case type: {case_type}", "high"))
        
        # Case complexity indicators
        case_description = legal_data.get("case_description", "").lower()
        complexity_indicators = [
            ("multiple defendants", 0.2, "medium"),
            ("federal court", 0.1, "medium"),
            ("class action", 0.3, "high"),
            ("appeals process", 0.2, "high"),
            ("expert testimony required", 0.1, "low"),
        ]
        
        for indicator, weight, severity in complexity_indicators:
            if indicator in case_description:
                risk_score += weight
                risk_factors.append((f"Case complexity: {indicator}", severity))
        
        # Statute of limitations risk
        incident_date = legal_data.get("incident_date")
        if incident_date:
            try:
                incident_dt = datetime.strptime(incident_date, "%Y-%m-%d")
                days_since = (datetime.now() - incident_dt).days
                
                if days_since > 1095:  # 3 years
                    risk_score += 0.4
                    risk_factors.append(("Case very old (>3 years)", "critical"))
                elif days_since > 730:  # 2 years
                    risk_score += 0.2
                    risk_factors.append(("Case moderately old (>2 years)", "high"))
            except ValueError:
                risk_score += 0.1
                risk_factors.append(("Invalid incident date", "low"))
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_details": {
                "case_type_risk_level": self._get_case_type_risk_level(case_type),
                "complexity_score": self._calculate_complexity_score(case_description),
                "time_sensitivity": self._assess_time_sensitivity(incident_date),
            }
        }
    
    def _score_medical_risk(self, medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score medical risk factors."""
        risk_score = 0.0
        risk_factors = []
        
        # Age-based risk
        age = medical_data.get("age")
        if age:
            if age > 75:
                risk_score += 0.2
                risk_factors.append(("Advanced age (>75)", "medium"))
            elif age < 18:
                risk_score += 0.1
                risk_factors.append(("Minor plaintiff", "low"))
        
        # Pre-existing conditions
        medical_history = medical_data.get("medical_history", [])
        high_risk_conditions = [
            "diabetes", "heart disease", "mental health", "chronic pain",
            "addiction", "psychiatric disorder", "disability"
        ]
        
        for condition in high_risk_conditions:
            if any(condition.lower() in hist.lower() for hist in medical_history):
                risk_score += 0.15
                risk_factors.append((f"Pre-existing condition: {condition}", "medium"))
        
        # Injury severity indicators
        injury_description = medical_data.get("injury_description", "").lower()
        severity_indicators = [
            ("traumatic brain injury", 0.3, "high"),
            ("spinal cord injury", 0.3, "high"),
            ("permanent disability", 0.25, "high"),
            ("surgery required", 0.15, "medium"),
            ("chronic pain", 0.1, "medium"),
        ]
        
        for indicator, weight, severity in severity_indicators:
            if indicator in injury_description:
                risk_score += weight
                risk_factors.append((f"Injury severity: {indicator}", severity))
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_details": {
                "age_risk_category": self._categorize_age_risk(age),
                "medical_complexity": len(medical_history),
                "injury_severity_score": self._calculate_injury_severity(injury_description),
            }
        }
    
    def _score_behavioral_risk(self, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score behavioral risk factors."""
        risk_score = 0.0
        risk_factors = []
        
        # Communication responsiveness
        response_rate = behavioral_data.get("communication_response_rate", 1.0)
        if response_rate < 0.5:
            risk_score += 0.3
            risk_factors.append(("Poor communication responsiveness", "high"))
        elif response_rate < 0.7:
            risk_score += 0.1
            risk_factors.append(("Below-average responsiveness", "medium"))
        
        # Compliance with requests
        compliance_rate = behavioral_data.get("compliance_rate", 1.0)
        if compliance_rate < 0.6:
            risk_score += 0.2
            risk_factors.append(("Poor compliance with requests", "medium"))
        
        # Contact information completeness
        contact_completeness = behavioral_data.get("contact_completeness", 1.0)
        if contact_completeness < 0.8:
            risk_score += 0.1
            risk_factors.append(("Incomplete contact information", "low"))
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_details": {
                "communication_score": response_rate,
                "compliance_score": compliance_rate,
                "contact_quality": contact_completeness,
            }
        }
    
    def _score_external_risk(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score external risk factors."""
        risk_score = 0.0
        risk_factors = []
        
        # Geographic risk
        state = external_data.get("state", "").upper()
        high_litigation_states = ["FL", "CA", "TX", "NY", "NJ"]
        if state in high_litigation_states:
            risk_score += 0.1
            risk_factors.append((f"High-litigation state: {state}", "low"))
        
        # Economic conditions
        unemployment_rate = external_data.get("local_unemployment_rate")
        if unemployment_rate and unemployment_rate > 8.0:
            risk_score += 0.1
            risk_factors.append(("High local unemployment", "low"))
        
        # Market conditions
        market_volatility = external_data.get("market_volatility_index", 0.5)
        if market_volatility > 0.8:
            risk_score += 0.1
            risk_factors.append(("High market volatility", "low"))
        
        return {
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "assessment_details": {
                "geographic_risk": self._assess_geographic_risk(state),
                "economic_conditions": self._assess_economic_conditions(external_data),
            }
        }
    
    # Helper methods for categorization and assessment
    
    def _categorize_income(self, monthly_income: float) -> str:
        """Categorize income level."""
        if monthly_income < 2000:
            return "very_low"
        elif monthly_income < 4000:
            return "low"
        elif monthly_income < 7000:
            return "moderate"
        elif monthly_income < 12000:
            return "high"
        else:
            return "very_high"
    
    def _categorize_credit_score(self, credit_score: int) -> str:
        """Categorize credit score."""
        if not credit_score:
            return "unknown"
        elif credit_score < 580:
            return "poor"
        elif credit_score < 670:
            return "fair"
        elif credit_score < 740:
            return "good"
        elif credit_score < 800:
            return "very_good"
        else:
            return "excellent"
    
    def _get_case_type_risk_level(self, case_type: str) -> str:
        """Get risk level for case type."""
        high_risk = [
            "medical_malpractice", "product_liability", "wrongful_death",
            "class_action", "mass_tort"
        ]
        medium_risk = [
            "workers_compensation", "employment", "premises_liability"
        ]
        
        if case_type in high_risk:
            return "high"
        elif case_type in medium_risk:
            return "medium"
        else:
            return "low"
    
    def _calculate_complexity_score(self, case_description: str) -> float:
        """Calculate case complexity score."""
        complexity_keywords = [
            "multiple", "complex", "federal", "appeals", "expert",
            "class action", "punitive", "conspiracy", "fraud"
        ]
        
        matches = sum(1 for keyword in complexity_keywords 
                     if keyword in case_description.lower())
        
        return min(matches / len(complexity_keywords), 1.0)
    
    def _assess_time_sensitivity(self, incident_date: str) -> str:
        """Assess time sensitivity based on incident date."""
        if not incident_date:
            return "unknown"
        
        try:
            incident_dt = datetime.strptime(incident_date, "%Y-%m-%d")
            days_since = (datetime.now() - incident_dt).days
            
            if days_since > 1095:  # 3 years
                return "critical"
            elif days_since > 730:  # 2 years
                return "high"
            elif days_since > 365:  # 1 year
                return "medium"
            else:
                return "low"
        except ValueError:
            return "invalid"
    
    def _categorize_age_risk(self, age: int) -> str:
        """Categorize age-based risk."""
        if not age:
            return "unknown"
        elif age < 18:
            return "minor"
        elif age > 75:
            return "elderly"
        elif age > 65:
            return "senior"
        else:
            return "adult"
    
    def _calculate_injury_severity(self, injury_description: str) -> float:
        """Calculate injury severity score."""
        severity_keywords = [
            "brain injury", "spinal", "permanent", "disability",
            "amputation", "paralysis", "death", "surgery"
        ]
        
        matches = sum(1 for keyword in severity_keywords 
                     if keyword in injury_description.lower())
        
        return min(matches / len(severity_keywords), 1.0)
    
    def _assess_geographic_risk(self, state: str) -> str:
        """Assess geographic risk level."""
        high_risk_states = ["FL", "CA", "TX", "NY", "NJ"]
        medium_risk_states = ["IL", "PA", "OH", "MI", "GA"]
        
        if state in high_risk_states:
            return "high"
        elif state in medium_risk_states:
            return "medium"
        else:
            return "low"
    
    def _assess_economic_conditions(self, external_data: Dict[str, Any]) -> str:
        """Assess local economic conditions."""
        unemployment = external_data.get("local_unemployment_rate", 5.0)
        
        if unemployment > 10.0:
            return "poor"
        elif unemployment > 7.0:
            return "fair"
        elif unemployment > 4.0:
            return "good"
        else:
            return "excellent"