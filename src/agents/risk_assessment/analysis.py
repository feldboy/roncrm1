"""Case analysis utilities for risk assessment."""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime


class CaseAnalyzer:
    """
    Advanced case analysis for risk assessment.
    
    Provides text analysis, pattern recognition, and
    case classification capabilities.
    """
    
    def __init__(self):
        """Initialize the case analyzer."""
        self.case_type_keywords = {
            "auto_accident": [
                "car accident", "vehicle accident", "auto collision", "traffic accident",
                "rear-end", "head-on collision", "hit and run", "drunk driver"
            ],
            "slip_and_fall": [
                "slip and fall", "trip and fall", "premises liability", "wet floor",
                "uneven surface", "poor lighting", "negligent maintenance"
            ],
            "medical_malpractice": [
                "medical malpractice", "doctor negligence", "hospital error",
                "misdiagnosis", "surgical error", "medication error", "birth injury"
            ],
            "workers_compensation": [
                "workplace injury", "work-related injury", "on-the-job accident",
                "workers comp", "occupational injury", "industrial accident"
            ],
            "product_liability": [
                "defective product", "product malfunction", "design defect",
                "manufacturing defect", "failure to warn", "product recall"
            ],
            "wrongful_death": [
                "wrongful death", "fatal accident", "death claim", "survival action",
                "loss of consortium", "funeral expenses"
            ]
        }
        
        self.severity_indicators = {
            "critical": [
                "death", "fatal", "brain injury", "spinal cord", "paralysis",
                "permanent disability", "amputation", "vegetative state"
            ],
            "severe": [
                "surgery", "hospitalization", "fracture", "internal bleeding",
                "organ damage", "burns", "scarring", "chronic pain"
            ],
            "moderate": [
                "emergency room", "physical therapy", "medication", "treatment",
                "x-ray", "MRI", "specialist", "follow-up"
            ],
            "minor": [
                "bruising", "soreness", "minor cuts", "first aid", "ice pack",
                "over-the-counter", "bandage", "rest"
            ]
        }
        
        self.liability_indicators = {
            "clear": [
                "admitted fault", "clear negligence", "violation", "criminal charges",
                "cited", "obviously at fault", "undisputed"
            ],
            "likely": [
                "negligent", "careless", "failed to", "should have", "duty of care",
                "breach of duty", "reasonable person"
            ],
            "disputed": [
                "disputed", "conflicting", "unclear", "investigation ongoing",
                "both parties claim", "different versions", "he said she said"
            ],
            "weak": [
                "no witnesses", "no evidence", "pre-existing", "comparative fault",
                "assumption of risk", "contributory negligence"
            ]
        }
    
    def analyze_case_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze case description text for risk factors.
        
        Args:
            description: Case description text.
            
        Returns:
            dict: Analysis results including classification and risk factors.
        """
        if not description:
            return self._empty_analysis()
        
        description_lower = description.lower()
        
        analysis = {
            "case_type_classification": self._classify_case_type(description_lower),
            "severity_assessment": self._assess_severity(description_lower),
            "liability_assessment": self._assess_liability(description_lower),
            "complexity_factors": self._identify_complexity_factors(description_lower),
            "red_flags": self._identify_red_flags(description_lower),
            "key_entities": self._extract_key_entities(description),
            "timeline_indicators": self._extract_timeline_indicators(description),
            "financial_indicators": self._extract_financial_indicators(description),
        }
        
        # Calculate overall risk score based on analysis
        analysis["calculated_risk_score"] = self._calculate_description_risk_score(analysis)
        
        return analysis
    
    def _classify_case_type(self, description: str) -> Dict[str, Any]:
        """Classify case type based on description."""
        case_type_scores = {}
        
        for case_type, keywords in self.case_type_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in description:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                case_type_scores[case_type] = {
                    "score": score,
                    "confidence": min(score / len(keywords), 1.0),
                    "matched_keywords": matched_keywords
                }
        
        # Determine most likely case type
        if case_type_scores:
            best_match = max(case_type_scores.items(), key=lambda x: x[1]["score"])
            primary_case_type = best_match[0]
            confidence = best_match[1]["confidence"]
        else:
            primary_case_type = "unknown"
            confidence = 0.0
        
        return {
            "primary_case_type": primary_case_type,
            "confidence": confidence,
            "all_scores": case_type_scores
        }
    
    def _assess_severity(self, description: str) -> Dict[str, Any]:
        """Assess injury/damage severity from description."""
        severity_scores = {level: 0 for level in self.severity_indicators.keys()}
        matched_indicators = {level: [] for level in self.severity_indicators.keys()}
        
        for severity_level, indicators in self.severity_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    severity_scores[severity_level] += 1
                    matched_indicators[severity_level].append(indicator)
        
        # Determine primary severity level
        if any(severity_scores.values()):
            primary_severity = max(severity_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_severity = "unknown"
        
        return {
            "primary_severity": primary_severity,
            "severity_scores": severity_scores,
            "matched_indicators": matched_indicators,
            "severity_risk_multiplier": self._get_severity_risk_multiplier(primary_severity)
        }
    
    def _assess_liability(self, description: str) -> Dict[str, Any]:
        """Assess liability strength from description."""
        liability_scores = {level: 0 for level in self.liability_indicators.keys()}
        matched_indicators = {level: [] for level in self.liability_indicators.keys()}
        
        for liability_level, indicators in self.liability_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    liability_scores[liability_level] += 1
                    matched_indicators[liability_level].append(indicator)
        
        # Determine primary liability assessment
        if any(liability_scores.values()):
            primary_liability = max(liability_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_liability = "unknown"
        
        return {
            "primary_liability": primary_liability,
            "liability_scores": liability_scores,
            "matched_indicators": matched_indicators,
            "liability_strength": self._get_liability_strength_score(primary_liability)
        }
    
    def _identify_complexity_factors(self, description: str) -> List[Dict[str, Any]]:
        """Identify factors that increase case complexity."""
        complexity_patterns = [
            {
                "factor": "Multiple Parties",
                "patterns": ["multiple defendants", "several parties", "various entities"],
                "risk_impact": 0.2
            },
            {
                "factor": "Federal Jurisdiction",
                "patterns": ["federal court", "interstate", "federal law"],
                "risk_impact": 0.15
            },
            {
                "factor": "Class Action Elements",
                "patterns": ["class action", "multiple plaintiffs", "similar cases"],
                "risk_impact": 0.3
            },
            {
                "factor": "Expert Testimony Required",
                "patterns": ["expert witness", "technical analysis", "specialized knowledge"],
                "risk_impact": 0.1
            },
            {
                "factor": "Insurance Disputes",
                "patterns": ["insurance denial", "coverage dispute", "bad faith"],
                "risk_impact": 0.15
            },
            {
                "factor": "Criminal Elements",
                "patterns": ["criminal charges", "police investigation", "felony"],
                "risk_impact": 0.2
            }
        ]
        
        identified_factors = []
        
        for factor_info in complexity_patterns:
            matched_patterns = []
            for pattern in factor_info["patterns"]:
                if pattern in description:
                    matched_patterns.append(pattern)
            
            if matched_patterns:
                identified_factors.append({
                    "factor": factor_info["factor"],
                    "matched_patterns": matched_patterns,
                    "risk_impact": factor_info["risk_impact"]
                })
        
        return identified_factors
    
    def _identify_red_flags(self, description: str) -> List[Dict[str, Any]]:
        """Identify potential red flags in the case description."""
        red_flag_patterns = [
            {
                "flag": "Pre-existing Conditions",
                "patterns": ["pre-existing", "prior injury", "previous condition"],
                "severity": "high"
            },
            {
                "flag": "Substance Abuse",
                "patterns": ["alcohol", "drugs", "intoxicated", "substance abuse"],
                "severity": "high"
            },
            {
                "flag": "Mental Health Issues",
                "patterns": ["depression", "anxiety", "psychiatric", "mental health"],
                "severity": "medium"
            },
            {
                "flag": "Delayed Reporting",
                "patterns": ["delayed report", "didn't report initially", "waited to report"],
                "severity": "medium"
            },
            {
                "flag": "Witness Issues",
                "patterns": ["no witnesses", "unreliable witness", "witness unavailable"],
                "severity": "medium"
            },
            {
                "flag": "Documentation Problems",
                "patterns": ["no documentation", "lost records", "incomplete records"],
                "severity": "high"
            }
        ]
        
        identified_flags = []
        
        for flag_info in red_flag_patterns:
            matched_patterns = []
            for pattern in flag_info["patterns"]:
                if pattern in description:
                    matched_patterns.append(pattern)
            
            if matched_patterns:
                identified_flags.append({
                    "flag": flag_info["flag"],
                    "matched_patterns": matched_patterns,
                    "severity": flag_info["severity"]
                })
        
        return identified_flags
    
    def _extract_key_entities(self, description: str) -> Dict[str, List[str]]:
        """Extract key entities from case description."""
        entities = {
            "locations": [],
            "organizations": [],
            "dates": [],
            "monetary_amounts": [],
            "medical_terms": [],
            "legal_terms": []
        }
        
        # Extract monetary amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?'
        entities["monetary_amounts"] = re.findall(money_pattern, description)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'[A-Za-z]+ \d{1,2}, \d{4}'
        ]
        for pattern in date_patterns:
            entities["dates"].extend(re.findall(pattern, description))
        
        # Extract medical terms (basic pattern matching)
        medical_keywords = [
            "hospital", "doctor", "physician", "surgery", "medication",
            "diagnosis", "treatment", "therapy", "rehabilitation"
        ]
        for keyword in medical_keywords:
            if keyword.lower() in description.lower():
                entities["medical_terms"].append(keyword)
        
        # Extract legal terms
        legal_keywords = [
            "negligence", "liability", "damages", "settlement", "lawsuit",
            "court", "attorney", "legal", "claim", "compensation"
        ]
        for keyword in legal_keywords:
            if keyword.lower() in description.lower():
                entities["legal_terms"].append(keyword)
        
        return entities
    
    def _extract_timeline_indicators(self, description: str) -> Dict[str, Any]:
        """Extract timeline and urgency indicators."""
        timeline_patterns = {
            "immediate": ["immediately", "right away", "emergency", "urgent"],
            "recent": ["recently", "last week", "few days ago", "yesterday"],
            "delayed": ["weeks later", "months later", "delayed", "eventually"],
            "ongoing": ["ongoing", "continuing", "still", "current"]
        }
        
        timeline_indicators = {}
        
        for timeframe, patterns in timeline_patterns.items():
            matched = [pattern for pattern in patterns if pattern in description.lower()]
            if matched:
                timeline_indicators[timeframe] = matched
        
        return timeline_indicators
    
    def _extract_financial_indicators(self, description: str) -> Dict[str, Any]:
        """Extract financial impact indicators."""
        financial_patterns = {
            "medical_costs": ["medical bills", "hospital costs", "treatment expenses"],
            "lost_wages": ["lost wages", "time off work", "unable to work"],
            "property_damage": ["property damage", "vehicle damage", "repair costs"],
            "future_losses": ["future medical", "ongoing treatment", "permanent disability"]
        }
        
        financial_indicators = {}
        
        for category, patterns in financial_patterns.items():
            matched = [pattern for pattern in patterns if pattern in description.lower()]
            if matched:
                financial_indicators[category] = matched
        
        return financial_indicators
    
    def _calculate_description_risk_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate risk score based on description analysis."""
        base_risk = 0.0
        
        # Case type risk
        case_type = analysis["case_type_classification"]["primary_case_type"]
        case_type_risks = {
            "medical_malpractice": 0.3,
            "product_liability": 0.25,
            "wrongful_death": 0.4,
            "auto_accident": 0.15,
            "slip_and_fall": 0.1,
            "workers_compensation": 0.1,
            "unknown": 0.2
        }
        base_risk += case_type_risks.get(case_type, 0.2)
        
        # Severity risk
        severity = analysis["severity_assessment"]["primary_severity"]
        severity_multiplier = analysis["severity_assessment"]["severity_risk_multiplier"]
        base_risk += severity_multiplier
        
        # Liability risk (inverse - weaker liability = higher risk)
        liability_strength = analysis["liability_assessment"]["liability_strength"]
        base_risk += (1.0 - liability_strength) * 0.2
        
        # Complexity factors
        complexity_impact = sum(
            factor["risk_impact"] for factor in analysis["complexity_factors"]
        )
        base_risk += min(complexity_impact, 0.3)  # Cap complexity impact
        
        # Red flags
        red_flag_impact = 0
        for flag in analysis["red_flags"]:
            if flag["severity"] == "high":
                red_flag_impact += 0.15
            elif flag["severity"] == "medium":
                red_flag_impact += 0.1
        base_risk += min(red_flag_impact, 0.4)  # Cap red flag impact
        
        return min(base_risk, 1.0)
    
    def _get_severity_risk_multiplier(self, severity: str) -> float:
        """Get risk multiplier based on severity level."""
        multipliers = {
            "critical": 0.4,
            "severe": 0.3,
            "moderate": 0.15,
            "minor": 0.05,
            "unknown": 0.2
        }
        return multipliers.get(severity, 0.2)
    
    def _get_liability_strength_score(self, liability: str) -> float:
        """Get liability strength score (higher = stronger liability)."""
        strength_scores = {
            "clear": 0.9,
            "likely": 0.7,
            "disputed": 0.4,
            "weak": 0.2,
            "unknown": 0.5
        }
        return strength_scores.get(liability, 0.5)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "case_type_classification": {
                "primary_case_type": "unknown",
                "confidence": 0.0,
                "all_scores": {}
            },
            "severity_assessment": {
                "primary_severity": "unknown",
                "severity_scores": {},
                "matched_indicators": {},
                "severity_risk_multiplier": 0.2
            },
            "liability_assessment": {
                "primary_liability": "unknown",
                "liability_scores": {},
                "matched_indicators": {},
                "liability_strength": 0.5
            },
            "complexity_factors": [],
            "red_flags": [],
            "key_entities": {},
            "timeline_indicators": {},
            "financial_indicators": {},
            "calculated_risk_score": 0.5
        }