"""
Regulatory Intelligence Service for Navo Research Assistant
Provides regulatory analysis as specified in System Prompt
"""

import logging
from typing import List, Dict, Any, Optional
# Import with fallback
try:
    from models.enhanced_product import EnhancedProduct, ProductType, RegulatoryInfo
except ImportError:
    # Use basic types if enhanced model isn't available
    EnhancedProduct = dict
    ProductType = str
    RegulatoryInfo = dict

logger = logging.getLogger(__name__)

class RegulatoryService:
    """
    Service for regulatory analysis and compliance checking
    Aligns with System Prompt requirements for regulatory intelligence
    """
    
    def __init__(self):
        # Load regulatory databases (simplified for demo)
        self.health_canada_hotlist = self._load_health_canada_hotlist()
        self.fda_restrictions = self._load_fda_restrictions()
        self.eu_restrictions = self._load_eu_restrictions()
    
    def analyze_product_compliance(self, product: EnhancedProduct, jurisdiction: str = "US") -> Dict[str, Any]:
        """
        Analyze product for regulatory compliance
        Returns detailed compliance analysis with confidence scores
        """
        analysis = {
            "jurisdiction": jurisdiction,
            "compliance_status": "unknown",
            "confidence_score": 0.0,
            "regulatory_flags": [],
            "required_disclaimers": [],
            "missing_data_for_analysis": [],
            "recommendations": []
        }
        
        try:
            # Check ingredient restrictions
            restricted_ingredients = self._check_ingredient_restrictions(product, jurisdiction)
            if restricted_ingredients:
                analysis["regulatory_flags"].extend(restricted_ingredients)
                analysis["compliance_status"] = "needs_review"
            
            # Check product type compliance
            product_type_issues = self._check_product_type_compliance(product, jurisdiction)
            if product_type_issues:
                analysis["regulatory_flags"].extend(product_type_issues)
            
            # Check missing critical data
            missing_data = self._identify_missing_regulatory_data(product)
            analysis["missing_data_for_analysis"] = missing_data
            
            # Calculate confidence score
            analysis["confidence_score"] = self._calculate_confidence_score(product, missing_data)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(product, analysis)
            
            # Determine if disclaimer needed
            if any(flag.get("severity") == "high" for flag in analysis["regulatory_flags"]):
                analysis["required_disclaimers"].append(self._get_regulatory_disclaimer())
            
            logger.info(f"Regulatory analysis completed for {product.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Regulatory analysis failed: {e}")
            return self._create_fallback_analysis(product, str(e))
    
    def _check_ingredient_restrictions(self, product: EnhancedProduct, jurisdiction: str) -> List[Dict[str, Any]]:
        """Check ingredients against regulatory restrictions"""
        flags = []
        
        restriction_db = {
            "US": self.fda_restrictions,
            "CA": self.health_canada_hotlist,
            "EU": self.eu_restrictions
        }.get(jurisdiction, {})
        
        for ingredient in product.ingredients:
            if ingredient.name.lower() in restriction_db:
                restriction = restriction_db[ingredient.name.lower()]
                
                flag = {
                    "ingredient": ingredient.name,
                    "restriction_type": restriction.get("type", "restricted"),
                    "severity": restriction.get("severity", "medium"),
                    "details": restriction.get("details", ""),
                    "requires_concentration_check": restriction.get("concentration_dependent", False)
                }
                
                # Check concentration if specified
                if flag["requires_concentration_check"] and ingredient.concentration:
                    max_allowed = restriction.get("max_concentration", 0)
                    if ingredient.concentration > max_allowed:
                        flag["severity"] = "high"
                        flag["details"] += f" Concentration {ingredient.concentration}% exceeds limit of {max_allowed}%"
                
                flags.append(flag)
        
        return flags
    
    def _check_product_type_compliance(self, product: EnhancedProduct, jurisdiction: str) -> List[Dict[str, Any]]:
        """Check product type specific compliance requirements"""
        flags = []
        
        if product.product_type == ProductType.LEAVE_ON:
            # Leave-on products have stricter requirements
            for ingredient in product.ingredients:
                if ingredient.name.lower() in ["retinol", "vitamin a", "tretinoin"]:
                    if not ingredient.concentration:
                        flags.append({
                            "type": "missing_concentration",
                            "severity": "high",
                            "details": f"Leave-on product with {ingredient.name} requires concentration disclosure"
                        })
        
        return flags
    
    def _identify_missing_regulatory_data(self, product: EnhancedProduct) -> List[str]:
        """Identify missing data that affects regulatory analysis confidence"""
        missing = []
        
        if not product.product_type:
            missing.append("product_type (leave-on vs rinse-off)")
        
        if not product.ingredients:
            missing.append("ingredient_list")
        else:
            concentration_missing = [ing.name for ing in product.ingredients 
                                   if ing.role.value in ["active", "functional"] and not ing.concentration]
            if concentration_missing:
                missing.append(f"concentrations_for: {', '.join(concentration_missing)}")
        
        if not product.claims:
            missing.append("product_claims")
        
        return missing
    
    def _calculate_confidence_score(self, product: EnhancedProduct, missing_data: List[str]) -> float:
        """Calculate confidence score for regulatory analysis"""
        base_score = 1.0
        
        # Deduct for missing critical data
        deduction_per_missing = 0.2
        confidence = base_score - (len(missing_data) * deduction_per_missing)
        
        # Bonus for complete ingredient data
        if product.ingredients and all(ing.concentration for ing in product.ingredients):
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_recommendations(self, product: EnhancedProduct, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if analysis["missing_data_for_analysis"]:
            recommendations.append(f"Obtain missing data: {', '.join(analysis['missing_data_for_analysis'])}")
        
        if analysis["regulatory_flags"]:
            high_severity_flags = [flag for flag in analysis["regulatory_flags"] if flag.get("severity") == "high"]
            if high_severity_flags:
                recommendations.append("Consult regulatory specialist for high-severity ingredient restrictions")
        
        if analysis["confidence_score"] < 0.7:
            recommendations.append("Regulatory analysis confidence is low - additional product information needed")
        
        return recommendations
    
    def _load_health_canada_hotlist(self) -> Dict[str, Dict[str, Any]]:
        """Load Health Canada Cosmetic Ingredient Hotlist (simplified)"""
        return {
            "retinol": {
                "type": "restricted",
                "severity": "medium",
                "concentration_dependent": True,
                "max_concentration": 1.0,  # 1%
                "details": "Restricted in leave-on products above 1%, requires warning labels"
            },
            "hydroquinone": {
                "type": "prohibited",
                "severity": "high",
                "details": "Prohibited in cosmetics in Canada"
            },
            "salicylic acid": {
                "type": "restricted",
                "severity": "low",
                "concentration_dependent": True,
                "max_concentration": 2.0,
                "details": "Limited to 2% in leave-on products"
            }
        }
    
    def _load_fda_restrictions(self) -> Dict[str, Dict[str, Any]]:
        """Load FDA restrictions (simplified)"""
        return {
            "hydroquinone": {
                "type": "drug",
                "severity": "high",
                "details": "Considered drug ingredient above 2%, requires FDA approval"
            },
            "tretinoin": {
                "type": "prescription",
                "severity": "high",
                "details": "Prescription-only ingredient"
            }
        }
    
    def _load_eu_restrictions(self) -> Dict[str, Dict[str, Any]]:
        """Load EU restrictions (simplified)"""
        return {
            "hydroquinone": {
                "type": "prohibited",
                "severity": "high",
                "details": "Prohibited in cosmetic products in EU"
            },
            "formaldehyde": {
                "type": "restricted",
                "severity": "high",
                "concentration_dependent": True,
                "max_concentration": 0.2,
                "details": "Limited to 0.2% as preservative"
            }
        }
    
    def _get_regulatory_disclaimer(self) -> str:
        """Get regulatory disclaimer as specified in system prompt"""
        return """The information presented here is based on publicly available data sources (e.g., Health Canada, FDA databases, product listings). While we aim to provide accurate and helpful insights, this tool is not a substitute for legal, medical, or regulatory advice. Always consult qualified professionals before making product or compliance decisions."""
    
    def _create_fallback_analysis(self, product: EnhancedProduct, error: str) -> Dict[str, Any]:
        """Create fallback analysis when regulatory check fails"""
        return {
            "jurisdiction": "unknown",
            "compliance_status": "analysis_failed",
            "confidence_score": 0.0,
            "regulatory_flags": [],
            "required_disclaimers": [self._get_regulatory_disclaimer()],
            "missing_data_for_analysis": ["regulatory_analysis_failed"],
            "recommendations": [
                "Regulatory analysis encountered an error",
                "Consult regulatory specialist for proper compliance review",
                f"Technical error: {error}"
            ]
        }
