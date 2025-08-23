"""
Enhanced Regulatory Service for Beauty and Wellness Industry
Provides comprehensive regulatory compliance information and ingredient safety profiles
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class RegulatoryService:
    """
    Enhanced regulatory service with comprehensive beauty and wellness industry knowledge
    """
    
    def __init__(self):
        # Regulatory databases by region
        self.regulatory_databases = {
            "canada": {
                "authority": "Health Canada",
                "cosmetics_database": "Cosmetic Ingredient Hotlist",
                "supplement_database": "Natural Health Products Database",
                "restricted_ingredients": [
                    "retinol", "tretinoin", "hydroquinone", "mercury", "lead",
                    "formaldehyde", "parabens", "phthalates", "triclosan"
                ],
                "concentration_limits": {
                    "retinol": {"max": "1.0%", "usage": "Leave-on products only"},
                    "hydroquinone": {"max": "2.0%", "usage": "Prescription only"},
                    "salicylic_acid": {"max": "2.0%", "usage": "Rinse-off products only"}
                }
            },
            "usa": {
                "authority": "FDA",
                "cosmetics_database": "FDA Cosmetic Ingredient Database",
                "supplement_database": "Dietary Supplement Ingredient Database",
                "restricted_ingredients": [
                    "mercury", "lead", "formaldehyde", "bithionol", "chloroform",
                    "methylene chloride", "vinyl chloride", "zirconium"
                ],
                "concentration_limits": {
                    "retinol": {"max": "1.0%", "usage": "Leave-on products only"},
                    "salicylic_acid": {"max": "2.0%", "usage": "Rinse-off products only"},
                    "alpha_hydroxy_acids": {"max": "10.0%", "usage": "With pH > 3.5"}
                }
            },
            "eu": {
                "authority": "European Commission",
                "cosmetics_database": "CosIng Database",
                "supplement_database": "Novel Food Catalogue",
                "restricted_ingredients": [
                    "retinol", "tretinoin", "hydroquinone", "mercury", "lead",
                    "formaldehyde", "parabens", "phthalates", "triclosan"
                ],
                "concentration_limits": {
                    "retinol": {"max": "0.3%", "usage": "Leave-on products only"},
                    "hydroquinone": {"max": "1.0%", "usage": "Prescription only"},
                    "salicylic_acid": {"max": "2.0%", "usage": "Rinse-off products only"}
                }
            },
            "california": {
                "authority": "California Proposition 65",
                "cosmetics_database": "Prop 65 List",
                "supplement_database": "Prop 65 List",
                "restricted_ingredients": [
                    "lead", "cadmium", "mercury", "formaldehyde", "toluene",
                    "phthalates", "bisphenol A", "arsenic"
                ],
                "warning_requirements": {
                    "lead": "May cause cancer and reproductive harm",
                    "formaldehyde": "Known to cause cancer",
                    "phthalates": "May cause reproductive harm"
                }
            }
        }
        
        # Ingredient safety profiles
        self.ingredient_safety_profiles = {
            "retinol": {
                "safety_rating": "moderate",
                "pregnancy_safe": False,
                "sensitive_skin": "caution",
                "regulatory_status": {
                    "canada": "restricted",
                    "usa": "restricted", 
                    "eu": "restricted",
                    "california": "warning_required"
                },
                "usage_guidelines": {
                    "max_concentration": "1.0%",
                    "application": "Evening use only",
                    "sun_protection": "Required",
                    "startup": "Gradual introduction recommended"
                },
                "side_effects": [
                    "Skin irritation", "Redness", "Peeling", "Sun sensitivity"
                ],
                "alternatives": [
                    "Bakuchiol", "Peptides", "Niacinamide", "Alpha-hydroxy acids"
                ]
            },
            "collagen": {
                "safety_rating": "high",
                "pregnancy_safe": True,
                "sensitive_skin": "safe",
                "regulatory_status": {
                    "canada": "approved",
                    "usa": "approved",
                    "eu": "approved", 
                    "california": "approved"
                },
                "usage_guidelines": {
                    "max_concentration": "No limit",
                    "application": "Any time",
                    "sun_protection": "Not required",
                    "startup": "No special requirements"
                },
                "side_effects": [
                    "Rare allergic reactions", "Mild irritation (topical)"
                ],
                "alternatives": [
                    "Peptides", "Hyaluronic acid", "Ceramides", "Amino acids"
                ]
            },
            "hyaluronic_acid": {
                "safety_rating": "very_high",
                "pregnancy_safe": True,
                "sensitive_skin": "very_safe",
                "regulatory_status": {
                    "canada": "approved",
                    "usa": "approved",
                    "eu": "approved",
                    "california": "approved"
                },
                "usage_guidelines": {
                    "max_concentration": "No limit",
                    "application": "Any time",
                    "sun_protection": "Not required", 
                    "startup": "No special requirements"
                },
                "side_effects": [
                    "Very rare allergic reactions"
                ],
                "alternatives": [
                    "Glycerin", "Aloe vera", "Sodium PCA", "Urea"
                ]
            },
            "salicylic_acid": {
                "safety_rating": "moderate",
                "pregnancy_safe": False,
                "sensitive_skin": "caution",
                "regulatory_status": {
                    "canada": "restricted",
                    "usa": "restricted",
                    "eu": "restricted", 
                    "california": "warning_required"
                },
                "usage_guidelines": {
                    "max_concentration": "2.0%",
                    "application": "Rinse-off products only",
                    "sun_protection": "Required",
                    "startup": "Gradual introduction recommended"
                },
                "side_effects": [
                    "Skin irritation", "Redness", "Dryness", "Sun sensitivity"
                ],
                "alternatives": [
                    "Azelaic acid", "Niacinamide", "Tea tree oil", "Zinc"
                ]
            }
        }
        
        # Product category regulations
        self.product_category_regulations = {
            "skincare": {
                "leave_on": {
                    "ingredient_restrictions": ["retinol", "hydroquinone", "high_concentration_acids"],
                    "testing_requirements": ["Stability testing", "Preservative efficacy"],
                    "labeling_requirements": ["Ingredient list", "Usage instructions", "Warnings"]
                },
                "rinse_off": {
                    "ingredient_restrictions": ["salicylic_acid", "benzoyl_peroxide"],
                    "testing_requirements": ["Safety testing", "Efficacy testing"],
                    "labeling_requirements": ["Ingredient list", "Usage instructions"]
                }
            },
            "supplements": {
                "oral": {
                    "ingredient_restrictions": ["prescription_ingredients", "controlled_substances"],
                    "testing_requirements": ["Identity testing", "Purity testing", "Potency testing"],
                    "labeling_requirements": ["Supplement facts", "Daily value", "Warnings"]
                },
                "topical": {
                    "ingredient_restrictions": ["drug_ingredients", "high_concentration_actives"],
                    "testing_requirements": ["Safety testing", "Efficacy testing"],
                    "labeling_requirements": ["Ingredient list", "Usage instructions"]
                }
            }
        }
    
    def get_ingredient_safety_profile(self, ingredient: str, region: str = "canada") -> Dict[str, Any]:
        """Get comprehensive safety profile for an ingredient"""
        ingredient_lower = ingredient.lower()
        
        # Find matching ingredient
        for key, profile in self.ingredient_safety_profiles.items():
            if key in ingredient_lower or any(alias in ingredient_lower for alias in profile.get("aliases", [])):
                result = profile.copy()
                
                # Add region-specific information
                if region in profile["regulatory_status"]:
                    result["regional_status"] = profile["regulatory_status"][region]
                    
                    # Add regional authority info
                    if region in self.regulatory_databases:
                        result["authority"] = self.regulatory_databases[region]["authority"]
                        result["database"] = self.regulatory_databases[region]["cosmetics_database"]
                
                return result
        
        # Return default profile for unknown ingredients
        return {
            "safety_rating": "unknown",
            "pregnancy_safe": "unknown",
            "sensitive_skin": "unknown",
            "regulatory_status": "unknown",
            "note": "Ingredient not found in database. Consult regulatory authority for current status."
        }
    
    def check_regulatory_compliance(
        self, 
        ingredients: List[str], 
        region: str, 
        product_type: str = "skincare",
        usage_context: str = "leave_on"
    ) -> Dict[str, Any]:
        """Check regulatory compliance for ingredient list"""
        compliance_result = {
            "compliant": True,
            "warnings": [],
            "restrictions": [],
            "required_testing": [],
            "labeling_requirements": [],
            "confidence_score": 1.0
        }
        
        if region not in self.regulatory_databases:
            compliance_result["compliant"] = False
            compliance_result["warnings"].append(f"Region '{region}' not supported")
            compliance_result["confidence_score"] = 0.0
            return compliance_result
        
        regulatory_db = self.regulatory_databases[region]
        
        # Check each ingredient
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Check if ingredient is restricted
            if any(restricted in ingredient_lower for restricted in regulatory_db["restricted_ingredients"]):
                compliance_result["restrictions"].append({
                    "ingredient": ingredient,
                    "status": "restricted",
                    "reason": f"Ingredient is restricted in {region}"
                })
                compliance_result["compliant"] = False
            
            # Check concentration limits
            if ingredient_lower in regulatory_db.get("concentration_limits", {}):
                limit_info = regulatory_db["concentration_limits"][ingredient_lower]
                compliance_result["restrictions"].append({
                    "ingredient": ingredient,
                    "status": "limited",
                    "max_concentration": limit_info["max"],
                    "usage_restrictions": limit_info["usage"]
                })
            
            # Get safety profile
            safety_profile = self.get_ingredient_safety_profile(ingredient, region)
            if safety_profile["safety_rating"] in ["moderate", "low"]:
                compliance_result["warnings"].append({
                    "ingredient": ingredient,
                    "warning": f"Safety rating: {safety_profile['safety_rating']}",
                    "side_effects": safety_profile.get("side_effects", [])
                })
        
        # Check product category requirements
        if product_type in self.product_category_regulations:
            category_regs = self.product_category_regulations[product_type]
            if usage_context in category_regs:
                usage_regs = category_regs[usage_context]
                
                # Add required testing
                compliance_result["required_testing"].extend(usage_regs.get("testing_requirements", []))
                
                # Add labeling requirements
                compliance_result["labeling_requirements"].extend(usage_regs.get("labeling_requirements", []))
        
        # Calculate confidence score
        if compliance_result["restrictions"]:
            compliance_result["confidence_score"] = max(0.3, 1.0 - len(compliance_result["restrictions"]) * 0.2)
        
        if compliance_result["warnings"]:
            compliance_result["confidence_score"] = max(0.5, compliance_result["confidence_score"] - len(compliance_result["warnings"]) * 0.1)
        
        return compliance_result
    
    def get_regulatory_updates(self, region: str, timeframe: str = "recent") -> List[Dict[str, Any]]:
        """Get recent regulatory updates for a region"""
        # This would integrate with regulatory databases for real-time updates
        # For now, return mock data
        updates = {
            "canada": [
                {
                    "date": "2024-01-15",
                    "update": "New restrictions on retinol concentration in leave-on products",
                    "impact": "Products with >1% retinol require prescription",
                    "effective_date": "2024-07-01"
                }
            ],
            "usa": [
                {
                    "date": "2024-01-10", 
                    "update": "FDA guidance on clean beauty claims",
                    "impact": "Stricter requirements for 'clean' and 'natural' labeling",
                    "effective_date": "2024-06-01"
                }
            ],
            "eu": [
                {
                    "date": "2024-01-20",
                    "update": "Updated CosIng database with new ingredient classifications",
                    "impact": "Several ingredients reclassified as restricted",
                    "effective_date": "2024-08-01"
                }
            ]
        }
        
        return updates.get(region, [])
    
    def suggest_compliant_alternatives(
        self, 
        restricted_ingredient: str, 
        region: str,
        product_type: str = "skincare"
    ) -> List[Dict[str, Any]]:
        """Suggest compliant alternatives for restricted ingredients"""
        alternatives = []
        
        # Get safety profile for the restricted ingredient
        safety_profile = self.get_ingredient_safety_profile(restricted_ingredient, region)
        
        if "alternatives" in safety_profile:
            for alt_ingredient in safety_profile["alternatives"]:
                alt_profile = self.get_ingredient_safety_profile(alt_ingredient, region)
                
                alternatives.append({
                    "ingredient": alt_ingredient,
                    "safety_rating": alt_profile["safety_rating"],
                    "regulatory_status": alt_profile.get("regional_status", "unknown"),
                    "efficacy_comparison": "Similar benefits with better safety profile",
                    "formulation_notes": "May require different concentration or application method"
                })
        
        return alternatives
    
    def generate_compliance_report(
        self, 
        product_formulation: Dict[str, Any], 
        target_regions: List[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report for product formulation"""
        report = {
            "product_name": product_formulation.get("name", "Unknown Product"),
            "formulation_date": datetime.utcnow().isoformat(),
            "target_regions": target_regions,
            "overall_compliance": True,
            "regional_reports": {},
            "recommendations": [],
            "risk_assessment": "low"
        }
        
        ingredients = product_formulation.get("ingredients", [])
        product_type = product_formulation.get("type", "skincare")
        usage_context = product_formulation.get("usage_context", "leave_on")
        
        for region in target_regions:
            regional_compliance = self.check_regulatory_compliance(
                ingredients, region, product_type, usage_context
            )
            
            report["regional_reports"][region] = regional_compliance
            
            if not regional_compliance["compliant"]:
                report["overall_compliance"] = False
                report["risk_assessment"] = "high"
            
            # Add regional recommendations
            if regional_compliance["restrictions"]:
                for restriction in regional_compliance["restrictions"]:
                    if restriction["status"] == "restricted":
                        alternatives = self.suggest_compliant_alternatives(
                            restriction["ingredient"], region, product_type
                        )
                        report["recommendations"].append({
                            "region": region,
                            "issue": f"Ingredient '{restriction['ingredient']}' is restricted",
                            "alternatives": alternatives,
                            "priority": "high"
                        })
        
        return report

# Global instance
regulatory_service = RegulatoryService()
