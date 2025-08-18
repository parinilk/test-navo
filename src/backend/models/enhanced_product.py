"""
Enhanced Product Data Model for Navo Research Assistant
Aligns with System Prompt requirements for detailed product analysis
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ProductType(str, Enum):
    LEAVE_ON = "leave_on"
    RINSE_OFF = "rinse_off"
    SUPPLEMENT = "supplement"
    CONSUMABLE = "consumable"

class IngredientRole(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FUNCTIONAL = "functional"
    PRESERVATIVE = "preservative"

class Ingredient(BaseModel):
    name: str
    role: IngredientRole
    concentration: Optional[float] = None
    concentration_unit: Optional[str] = None  # %, mg, IU, etc.
    inci_name: Optional[str] = None
    function: Optional[str] = None  # "hydration", "anti-aging", etc.
    regulatory_status: Optional[str] = None

class Claim(BaseModel):
    text: str
    claim_type: str  # "efficacy", "sensory", "marketing"
    substantiation: Optional[str] = None
    regulatory_compliant: Optional[bool] = None

class PricingMetrics(BaseModel):
    base_price: Optional[float] = None
    currency: str = "USD"
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    servings_per_container: Optional[int] = None
    price_per_serving: Optional[float] = None
    price_per_unit: Optional[float] = None  # per gram, ml, etc.

class RegulatoryInfo(BaseModel):
    jurisdiction: str  # "US", "CA", "EU"
    product_category: str  # "cosmetic", "supplement", "drug"
    restricted_ingredients: List[str] = []
    required_warnings: List[str] = []
    compliance_status: Optional[str] = None

class EnhancedProduct(BaseModel):
    # Basic Info
    id: str
    name: str
    brand: str
    category: str
    subcategory: Optional[str] = None
    
    # Product Classification
    product_type: Optional[ProductType] = None
    format: Optional[str] = None  # "powder", "capsule", "cream", etc.
    
    # Ingredients
    ingredients: List[Ingredient] = []
    key_actives: List[str] = []
    support_ingredients: List[str] = []
    
    # Claims & Marketing
    claims: List[Claim] = []
    marketing_copy: Optional[str] = None
    target_concerns: List[str] = []  # "hydration", "anti-aging", etc.
    
    # Pricing
    pricing: Optional[PricingMetrics] = None
    
    # Regulatory
    regulatory_info: List[RegulatoryInfo] = []
    
    # Market Data
    availability: Optional[str] = None
    sales_channel: Optional[str] = None
    brand_positioning: Optional[str] = None  # "premium", "mass", "natural"
    
    # Metadata
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    data_completeness_score: Optional[float] = None

class ProductAnalysis(BaseModel):
    """Analysis results for enhanced product intelligence"""
    
    # Ingredient Analysis
    functional_profile: Dict[str, List[str]]  # {"hydration": ["hyaluronic_acid"], ...}
    active_concentration_total: Optional[float] = None
    ingredient_gaps: List[str] = []  # Missing dosage info, etc.
    
    # Regulatory Analysis
    regulatory_flags: List[str] = []
    compliance_confidence: Optional[float] = None
    required_disclaimers: List[str] = []
    
    # Competitive Analysis
    positioning_vs_category: Optional[str] = None
    price_percentile: Optional[float] = None
    unique_differentiators: List[str] = []
    
    # Data Quality
    missing_critical_data: List[str] = []
    confidence_score: float
    recommended_next_steps: List[str] = []
