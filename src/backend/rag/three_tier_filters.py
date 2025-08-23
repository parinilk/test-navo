"""
Three-Tier Filter System for RAG
Implements the filter categorization from RAG Filters.md:
- Tier 1: Product-Level Filters
- Tier 2: Ingredient-Level Filters  
- Tier 3: Claim/Positioning-Level Filters
"""
from typing import Dict, List, Any, Optional
import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class FilterTier(Enum):
    """Filter tier classification"""
    TIER_1_PRODUCT = "tier_1_product"
    TIER_2_INGREDIENT = "tier_2_ingredient" 
    TIER_3_CLAIM = "tier_3_claim"

class ThreeTierFilterExtractor:
    """
    Extracts filters according to the three-tier system from RAG Filters.md
    """
    
    def __init__(self):
        # Tier 1: Product-Level Filters
        self.tier1_filters = {
            "format": {
                "powder": ["powder", "powdered", "dust"],
                "capsule": ["capsule", "caps", "tablet", "pill", "softgel"],
                "gummy": ["gummy", "gummies", "chewable", "chews"],
                "beverage": ["drink", "beverage", "liquid drink", "shake"],
                "pouch": ["pouch", "packet", "sachet"]
            },
            "primary_benefit": {
                "skin_health": ["skin health", "skincare", "complexion", "skin glow"],
                "joint_support": ["joint support", "joint health", "mobility", "flexibility"],
                "hair_nails": ["hair growth", "nail health", "hair nails", "stronger nails"],
                "general_wellness": ["general wellness", "overall health", "vitality", "energy"]
            },
            "price_ranges": {
                "under_20": ["under $20", "below $20", "less than $20", "budget"],
                "20_to_40": ["$20 to $40", "between $20 and $40", "mid-range"],
                "40_to_60": ["$40 to $60", "between $40 and $60"],
                "over_60": ["over $60", "above $60", "premium", "luxury"]
            },
            "brands": [
                "vital proteins", "ancient nutrition", "sports research",
                "great lakes", "neocell", "youtheory", "bulletproof",
                "orgain", "garden of life", "nature's bounty"
            ],
            "sales_channels": {
                "walmart": ["walmart", "wal-mart"],
                "amazon": ["amazon", "amazon.com"],
                "dtc": ["direct to consumer", "DTC", "brand website"],
                "in_store": ["in-store", "retail", "physical store"]
            },
            "pack_sizes": [
                r"(\d+)\s*ct", r"(\d+)\s*count", r"(\d+)\s*servings",
                r"(\d+)\s*capsules", r"(\d+)\s*gummies"
            ],
            "country_origin": [
                "made in USA", "made in Canada", "manufactured in",
                "sourced from", "origin"
            ]
        }
        
        # Tier 2: Ingredient-Level Filters
        self.tier2_filters = {
            "ingredient_name": {
                "hydrolyzed_collagen": ["hydrolyzed collagen", "collagen peptides", "collagen hydrolysate"],
                "biotin": ["biotin", "vitamin b7", "vitamin h", "d-biotin"],
                "ashwagandha": ["ashwagandha", "withania somnifera", "indian ginseng"],
                "retinol": ["retinol", "vitamin a", "retinyl palmitate", "retinaldehyde"],
                "hyaluronic_acid": ["hyaluronic acid", "HA", "sodium hyaluronate", "hyaluronan"],
                "vitamin_c": ["vitamin c", "ascorbic acid", "l-ascorbic acid", "ascorbyl palmitate"],
                "niacinamide": ["niacinamide", "vitamin b3", "nicotinamide", "nicotinic acid amide"],
                "peptides": ["peptides", "copper peptides", "matrixyl", "argireline", "palmitoyl"],
                "ceramides": ["ceramides", "ceramide np", "ceramide ap", "ceramide eop"],
                "alpha_hydroxy_acids": ["aha", "glycolic acid", "lactic acid", "mandelic acid", "citric acid"],
                "beta_hydroxy_acids": ["bha", "salicylic acid", "betaine salicylate"],
                "antioxidants": ["vitamin e", "green tea", "resveratrol", "coq10", "glutathione"],
                "probiotics": ["probiotics", "lactobacillus", "bifidobacterium", "saccharomyces"],
                "omega_fatty_acids": ["omega 3", "omega 6", "omega 9", "epa", "dha", "gla"]
            },
            "ingredient_form": {
                "marine_collagen": ["marine collagen", "fish collagen", "sea collagen", "ocean collagen"],
                "bovine_collagen": ["bovine collagen", "beef collagen", "cow collagen", "bovine hide"],
                "type_i_collagen": ["type 1 collagen", "type i collagen", "collagen type 1", "type 1"],
                "type_ii_collagen": ["type 2 collagen", "type ii collagen", "collagen type 2", "type 2"],
                "type_iii_collagen": ["type 3 collagen", "type iii collagen", "collagen type 3", "type 3"],
                "peptides": ["peptides", "hydrolyzed", "broken down", "low molecular weight"],
                "natural_derived": ["natural", "plant-derived", "botanical", "herbal", "organic"],
                "synthetic": ["synthetic", "lab-made", "artificial", "man-made"],
                "fermented": ["fermented", "bio-fermented", "k-ferment", "fermentation derived"]
            },
            "usage_context": {
                "rinse_off": ["rinse-off", "cleanser", "face wash", "shampoo", "body wash", "exfoliant"],
                "leave_on": ["leave-on", "serum", "moisturizer", "cream", "lotion", "essence", "ampoule"],
                "ingestible": ["supplement", "capsule", "powder", "drink", "oral", "tablet", "gummy"],
                "topical": ["topical", "applied to skin", "external use", "surface application"],
                "hair_care": ["hair care", "hair treatment", "scalp", "hair growth", "hair loss"],
                "body_care": ["body care", "body lotion", "body cream", "body serum"],
                "eye_care": ["eye care", "eye cream", "eye serum", "under eye", "eye contour"]
            },
            "jurisdiction": {
                "usa": ["USA", "United States", "US", "America", "FDA", "federal"],
                "canada": ["Canada", "Health Canada", "Canadian", "HC", "Canadian regulations"],
                "eu": ["EU", "European Union", "Europe", "EFSA", "European", "EU regulations"],
                "california": ["California", "Prop 65", "CA Prop 65", "Cal Prop 65", "CA regulations"],
                "uk": ["UK", "United Kingdom", "Britain", "MHRA", "British", "UK regulations"],
                "australia": ["Australia", "Australian", "TGA", "Australian regulations"],
                "japan": ["Japan", "Japanese", "PMDA", "Japanese regulations"],
                "korea": ["Korea", "Korean", "MFDS", "Korean regulations"]
            },
            "max_amounts": [
                r"(\d+(?:\.\d+)?)\s*%",  # Percentage
                r"(\d+(?:\.\d+)?)\s*mg",  # Milligrams
                r"(\d+(?:\.\d+)?)\s*mcg",  # Micrograms
                r"(\d+(?:\.\d+)?)\s*iu",   # International Units
                r"(\d+(?:\.\d+)?)\s*ppm"   # Parts per million
            ],
            "regulatory_status": {
                "approved": ["approved", "permitted", "allowed", "cleared", "authorized"],
                "restricted": ["restricted", "limited", "controlled", "regulated", "monitored"],
                "banned": ["banned", "prohibited", "forbidden", "illegal", "not allowed"],
                "pending": ["pending", "under review", "being evaluated", "submitted"],
                "grandfathered": ["grandfathered", "legacy", "existing use", "pre-existing"]
            }
        }
        
        # Tier 3: Claim/Positioning-Level Filters
        self.tier3_filters = {
            "claim_category": {
                "beauty": ["beauty", "cosmetic", "aesthetic", "appearance", "looks"],
                "anti_aging": ["anti-aging", "anti aging", "antiaging", "youthful", "age-defying"],
                "joint_flexibility": ["joint flexibility", "joint health", "mobility", "flexibility", "range of motion"],
                "gut_health": ["gut health", "digestive health", "intestinal health", "microbiome", "digestion"],
                "energy": ["energy", "vitality", "stamina", "endurance", "alertness"],
                "immune": ["immune", "immunity", "immune support", "immune system", "defense"],
                "sleep": ["sleep", "rest", "relaxation", "calm", "stress relief"],
                "weight_management": ["weight management", "weight loss", "metabolism", "fat burning", "appetite control"],
                "cognitive": ["cognitive", "brain health", "memory", "focus", "mental clarity"],
                "hormonal": ["hormonal", "hormone balance", "endocrine", "thyroid", "adrenal"]
            },
            "claim_format": {
                "supports": ["supports", "helps maintain", "assists with", "contributes to", "promotes"],
                "clinically_tested": ["clinically tested", "scientifically proven", "research backed", "evidence based"],
                "made_with": ["made with", "contains", "formulated with", "infused with", "enriched with"],
                "natural": ["natural", "naturally derived", "botanical", "herbal", "plant-based"],
                "clean": ["clean", "clean beauty", "non-toxic", "safe", "gentle"],
                "dermatologist_recommended": ["dermatologist recommended", "dermatologist tested", "doctor approved"],
                "vegan_friendly": ["vegan", "vegan friendly", "plant-based", "cruelty-free", "animal-free"]
            },
            "target_demographic": {
                "women": ["women", "female", "ladies", "women's health", "feminine"],
                "men": ["men", "male", "men's health", "masculine", "grooming"],
                "athletes": ["athletes", "sports", "fitness", "active", "performance"],
                "40_plus": ["40+", "40 plus", "mature", "aging", "midlife", "over 40"],
                "pregnant": ["pregnant", "pregnancy", "expecting", "maternal", "prenatal"],
                "seniors": ["seniors", "elderly", "aging", "65+", "older adults", "mature"],
                "teens": ["teens", "teenagers", "adolescent", "young", "youth"],
                "newborns": ["newborns", "babies", "infants", "0-2 years", "early childhood"]
            },
            "lifestyle": {
                "vegan": ["vegan", "plant-based", "animal-free", "cruelty-free"],
                "vegetarian": ["vegetarian", "plant-based", "no meat"],
                "keto": ["keto", "ketogenic", "low carb", "high fat"],
                "paleo": ["paleo", "paleolithic", "ancestral", "primal"],
                "organic": ["organic", "certified organic", "organically grown"],
                "gluten_free": ["gluten free", "gluten-free", "no gluten", "celiac friendly"],
                "dairy_free": ["dairy free", "dairy-free", "lactose free", "no dairy"],
                "allergen_free": ["allergen free", "hypoallergenic", "sensitive skin", "gentle"]
            },
            "skin_concerns": {
                "acne": ["acne", "breakouts", "blemishes", "pimples", "clogged pores"],
                "aging": ["aging", "wrinkles", "fine lines", "sagging", "loss of elasticity"],
                "hyperpigmentation": ["hyperpigmentation", "dark spots", "sun spots", "melasma", "uneven skin tone"],
                "dryness": ["dryness", "dehydration", "flaky", "rough", "tight"],
                "sensitivity": ["sensitivity", "irritation", "redness", "reactive", "delicate"],
                "large_pores": ["large pores", "enlarged pores", "pore size", "pore appearance"],
                "texture": ["texture", "rough", "bumpy", "uneven", "smooth"]
            },
            "product_positioning": {
                "luxury": ["luxury", "premium", "high-end", "exclusive", "boutique"],
                "mass_market": ["mass market", "affordable", "accessible", "mainstream", "drugstore"],
                "professional": ["professional", "pro", "salon", "spa", "clinic"],
                "indie": ["indie", "independent", "small batch", "artisanal", "handcrafted"],
                "clean_beauty": ["clean beauty", "green beauty", "eco-friendly", "sustainable", "conscious"],
                "medical_grade": ["medical grade", "clinical", "therapeutic", "medical", "professional strength"]
            }
        }
        
        # Severity patterns for regulatory
        self.severity_patterns = [
            r"severe\s+(\w+)", r"mild\s+(\w+)", r"moderate\s+(\w+)",
            r"warning.*(\w+)", r"caution.*(\w+)"
        ]
    
    def extract_all_filters(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract filters from all three tiers
        
        Args:
            query: User query string
            context: Optional context information
            
        Returns:
            Dict with filters organized by tier
        """
        logger.info(f"🔍 Extracting three-tier filters from: '{query[:50]}...'")
        
        query_lower = query.lower()
        context = context or {}
        
        result = {
            "tier_1_product": self._extract_tier1_filters(query_lower, context),
            "tier_2_ingredient": self._extract_tier2_filters(query_lower, context),
            "tier_3_claim": self._extract_tier3_filters(query_lower, context),
            "extracted_values": {},  # Specific values extracted
            "filter_confidence": {},  # Confidence scores per filter
            "suggested_filters": []  # Additional filters to consider
        }
        
        # Count total filters extracted
        total_filters = (
            len([f for f in result["tier_1_product"].values() if f]) +
            len([f for f in result["tier_2_ingredient"].values() if f]) +
            len([f for f in result["tier_3_claim"].values() if f])
        )
        
        logger.info(f"✅ Extracted {total_filters} filters across all tiers")
        return result
    
    def _extract_tier1_filters(self, query: str, context: Dict) -> Dict[str, Any]:
        """Extract Tier 1: Product-Level Filters"""
        filters = {
            "format": None,
            "primary_benefit": None,
            "price_range": None,
            "brand": None,
            "sales_channel": None,
            "pack_size": None,
            "country_origin": None,
            "weight_volume": None
        }
        
        # Extract format
        for format_type, keywords in self.tier1_filters["format"].items():
            if any(keyword in query for keyword in keywords):
                filters["format"] = format_type
                break
        
        # Extract primary benefit
        for benefit, keywords in self.tier1_filters["primary_benefit"].items():
            if any(keyword in query for keyword in keywords):
                filters["primary_benefit"] = benefit
                break
        
        # Extract price range
        filters["price_range"] = self._extract_price_filter(query)
        
        # Extract brand
        for brand in self.tier1_filters["brands"]:
            if brand in query:
                filters["brand"] = brand
                break
        
        # Extract sales channel
        for channel, keywords in self.tier1_filters["sales_channels"].items():
            if any(keyword in query for keyword in keywords):
                filters["sales_channel"] = channel
                break
        
        # Extract pack size
        filters["pack_size"] = self._extract_pack_size(query)
        
        # Extract country origin
        for pattern in self.tier1_filters["country_origin"]:
            if pattern in query:
                filters["country_origin"] = pattern
                break
        
        return {k: v for k, v in filters.items() if v is not None}
    
    def _extract_tier2_filters(self, query: str, context: Dict) -> Dict[str, Any]:
        """Extract Tier 2: Ingredient-Level Filters"""
        filters = {
            "ingredient_name": [],
            "ingredient_form": None,
            "usage_context": None,
            "jurisdiction": None,
            "max_amount": None,
            "caffeine_content": None,
            "condition_of_use": None
        }
        
        # Extract ingredient names
        for ingredient, keywords in self.tier2_filters["ingredient_name"].items():
            if any(keyword in query for keyword in keywords):
                filters["ingredient_name"].append(ingredient)
        
        # Extract ingredient form
        for form, keywords in self.tier2_filters["ingredient_form"].items():
            if any(keyword in query for keyword in keywords):
                filters["ingredient_form"] = form
                break
        
        # Extract usage context
        for context_type, keywords in self.tier2_filters["usage_context"].items():
            if any(keyword in query for keyword in keywords):
                filters["usage_context"] = context_type
                break
        
        # Extract jurisdiction
        for jurisdiction, keywords in self.tier2_filters["jurisdiction"].items():
            if any(keyword in query for keyword in keywords):
                filters["jurisdiction"] = jurisdiction
                break
        
        # Extract max amounts
        filters["max_amount"] = self._extract_max_amounts(query)
        
        # Extract caffeine content
        for caffeine_level, keywords in self.tier2_filters["caffeine_content"].items():
            if any(keyword in query for keyword in keywords):
                filters["caffeine_content"] = caffeine_level
                break
        
        return {k: v for k, v in filters.items() if v}
    
    def _extract_tier3_filters(self, query: str, context: Dict) -> Dict[str, Any]:
        """Extract Tier 3: Claim/Positioning-Level Filters"""
        filters = {
            "claim_category": [],
            "claim_format": [],
            "target_demographic": [],
            "lifestyle": [],
            "brand_voice": None
        }
        
        # Extract claim categories
        for category, keywords in self.tier3_filters["claim_category"].items():
            if any(keyword in query for keyword in keywords):
                filters["claim_category"].append(category)
        
        # Extract claim formats
        for format_type, keywords in self.tier3_filters["claim_format"].items():
            if any(keyword in query for keyword in keywords):
                filters["claim_format"].append(format_type)
        
        # Extract target demographics
        for demo, keywords in self.tier3_filters["target_demographic"].items():
            if any(keyword in query for keyword in keywords):
                filters["target_demographic"].append(demo)
        
        # Extract lifestyle filters
        for lifestyle, keywords in self.tier3_filters["lifestyle"].items():
            if any(keyword in query for keyword in keywords):
                filters["lifestyle"].append(lifestyle)
        
        # Infer brand voice from context
        if context.get('role'):
            role = context['role'].lower()
            if 'scientist' in role or 'research' in role:
                filters["brand_voice"] = "science_backed"
            elif 'marketing' in role:
                filters["brand_voice"] = "emotional"
            elif 'natural' in query or 'organic' in query:
                filters["brand_voice"] = "natural"
        
        return {k: v for k, v in filters.items() if v}
    
    def _extract_price_filter(self, query: str) -> Optional[Dict[str, float]]:
        """Extract price range from query"""
        # Under/below patterns
        under_pattern = r"under\s*\$?(\d+)"
        match = re.search(under_pattern, query)
        if match:
            return {"max": float(match.group(1))}
        
        # Over/above patterns  
        over_pattern = r"(?:over|above)\s*\$?(\d+)"
        match = re.search(over_pattern, query)
        if match:
            return {"min": float(match.group(1))}
        
        # Between pattern
        between_pattern = r"between\s*\$?(\d+)\s*(?:and|to)\s*\$?(\d+)"
        match = re.search(between_pattern, query)
        if match:
            return {"min": float(match.group(1)), "max": float(match.group(2))}
        
        return None
    
    def _extract_pack_size(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract pack size information"""
        for pattern in self.tier1_filters["pack_sizes"]:
            match = re.search(pattern, query)
            if match:
                return {
                    "count": int(match.group(1)),
                    "unit": match.group(0).split(match.group(1))[1].strip()
                }
        return None
    
    def _extract_max_amounts(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract maximum amount constraints"""
        for pattern in self.tier2_filters["max_amounts"]:
            match = re.search(pattern, query)
            if match:
                return {
                    "amount": float(match.group(1)),
                    "unit": match.group(2)
                }
        return None
    
    def get_filter_suggestions(self, query: str, extracted_filters: Dict) -> List[Dict[str, Any]]:
        """
        Suggest additional filters that might be relevant
        """
        suggestions = []
        
        # If ingredient is mentioned, suggest related filters
        if extracted_filters.get("tier_2_ingredient", {}).get("ingredient_name"):
            suggestions.append({
                "filter": "usage_context",
                "reason": "Ingredient usage context affects regulatory requirements",
                "options": list(self.tier2_filters["usage_context"].keys())
            })
        
        # If target demographic is unclear, suggest clarification
        if not extracted_filters.get("tier_3_claim", {}).get("target_demographic"):
            if any(word in query for word in ["for", "targeting", "aimed at"]):
                suggestions.append({
                    "filter": "target_demographic", 
                    "reason": "Target demographic affects product positioning",
                    "options": list(self.tier3_filters["target_demographic"].keys())
                })
        
        # If price is mentioned without range, suggest clarification
        if "price" in query and not extracted_filters.get("tier_1_product", {}).get("price_range"):
            suggestions.append({
                "filter": "price_range",
                "reason": "Price range helps narrow product recommendations",
                "options": ["under_20", "20_to_40", "40_to_60", "over_60"]
            })
        
        return suggestions

# Global instance
three_tier_filter_extractor = ThreeTierFilterExtractor()
