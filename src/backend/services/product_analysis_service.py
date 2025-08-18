"""
Product Analysis Service for Navo Research Assistant
Provides deep product intelligence as specified in System Prompt
"""

import logging
from typing import List, Dict, Any, Optional
# Import with fallback
try:
    from models.enhanced_product import EnhancedProduct, ProductAnalysis, Ingredient, PricingMetrics
except ImportError:
    # Use basic types if enhanced model isn't available
    EnhancedProduct = dict
    ProductAnalysis = dict
    Ingredient = dict
    PricingMetrics = dict

logger = logging.getLogger(__name__)

class ProductAnalysisService:
    """
    Service for advanced product analysis
    Implements System Prompt requirements for deep product intelligence
    """
    
    def __init__(self):
        self.functional_ingredient_map = self._load_functional_ingredients()
        self.market_benchmarks = self._load_market_benchmarks()
    
    def analyze_products(self, products: List[EnhancedProduct], query_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive product analysis with gap identification
        Follows System Prompt requirements for evidence-based insights
        """
        if not products:
            return self._create_no_products_analysis(query_context)
        
        analysis = {
            "total_products": len(products),
            "analysis_confidence": 0.0,
            "data_gaps": [],
            "key_insights": [],
            "comparative_analysis": {},
            "functional_analysis": {},
            "pricing_analysis": {},
            "recommendations": [],
            "evidence_quality": "unknown"
        }
        
        try:
            # Functional ingredient analysis
            analysis["functional_analysis"] = self._analyze_functional_ingredients(products)
            
            # Pricing analysis with per-serving calculations
            analysis["pricing_analysis"] = self._analyze_pricing_strategies(products)
            
            # Comparative analysis
            analysis["comparative_analysis"] = self._compare_products(products)
            
            # Identify data gaps
            analysis["data_gaps"] = self._identify_data_gaps(products)
            
            # Calculate analysis confidence
            analysis["analysis_confidence"] = self._calculate_analysis_confidence(products, analysis["data_gaps"])
            
            # Generate evidence-based insights
            analysis["key_insights"] = self._generate_insights(products, analysis)
            
            # Determine evidence quality
            analysis["evidence_quality"] = self._assess_evidence_quality(products, analysis)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_analysis_recommendations(products, analysis)
            
            logger.info(f"Product analysis completed for {len(products)} products")
            return analysis
            
        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            return self._create_fallback_analysis(products, str(e))
    
    def _analyze_functional_ingredients(self, products: List[EnhancedProduct]) -> Dict[str, Any]:
        """Analyze functional ingredients across products"""
        functional_profile = {}
        ingredient_frequency = {}
        concentration_analysis = {}
        
        for product in products:
            for ingredient in product.ingredients:
                # Track ingredient frequency
                ing_name = ingredient.name.lower()
                ingredient_frequency[ing_name] = ingredient_frequency.get(ing_name, 0) + 1
                
                # Map to functional benefits
                if ing_name in self.functional_ingredient_map:
                    functions = self.functional_ingredient_map[ing_name]
                    for function in functions:
                        if function not in functional_profile:
                            functional_profile[function] = []
                        functional_profile[function].append({
                            "ingredient": ingredient.name,
                            "product": product.name,
                            "concentration": ingredient.concentration,
                            "concentration_unit": ingredient.concentration_unit
                        })
                
                # Concentration analysis
                if ingredient.concentration:
                    if ing_name not in concentration_analysis:
                        concentration_analysis[ing_name] = []
                    concentration_analysis[ing_name].append({
                        "product": product.name,
                        "concentration": ingredient.concentration,
                        "unit": ingredient.concentration_unit
                    })
        
        return {
            "functional_benefits": functional_profile,
            "ingredient_frequency": ingredient_frequency,
            "concentration_ranges": concentration_analysis,
            "most_common_actives": sorted(ingredient_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_pricing_strategies(self, products: List[EnhancedProduct]) -> Dict[str, Any]:
        """Analyze pricing with per-serving calculations"""
        pricing_data = []
        
        for product in products:
            if product.pricing and product.pricing.base_price:
                price_info = {
                    "product": product.name,
                    "brand": product.brand,
                    "base_price": product.pricing.base_price,
                    "currency": product.pricing.currency
                }
                
                # Calculate per-serving cost if possible
                if product.pricing.servings_per_container:
                    price_per_serving = product.pricing.base_price / product.pricing.servings_per_container
                    price_info["price_per_serving"] = round(price_per_serving, 2)
                
                # Calculate per-unit cost if possible
                if product.pricing.quantity and product.pricing.quantity_unit:
                    price_per_unit = product.pricing.base_price / product.pricing.quantity
                    price_info["price_per_unit"] = round(price_per_unit, 2)
                    price_info["unit"] = product.pricing.quantity_unit
                
                pricing_data.append(price_info)
        
        if not pricing_data:
            return {"error": "No pricing data available", "products_with_pricing": 0}
        
        # Calculate statistics
        base_prices = [p["base_price"] for p in pricing_data]
        per_serving_prices = [p["price_per_serving"] for p in pricing_data if "price_per_serving" in p]
        
        analysis = {
            "products_with_pricing": len(pricing_data),
            "price_range": {
                "min": min(base_prices),
                "max": max(base_prices),
                "average": round(sum(base_prices) / len(base_prices), 2)
            },
            "detailed_pricing": pricing_data
        }
        
        if per_serving_prices:
            analysis["per_serving_range"] = {
                "min": min(per_serving_prices),
                "max": max(per_serving_prices),
                "average": round(sum(per_serving_prices) / len(per_serving_prices), 2)
            }
        
        return analysis
    
    def _compare_products(self, products: List[EnhancedProduct]) -> Dict[str, Any]:
        """Detailed product comparison analysis"""
        comparison = {
            "brand_analysis": {},
            "format_distribution": {},
            "unique_differentiators": [],
            "market_gaps": []
        }
        
        # Brand analysis
        brands = {}
        for product in products:
            if product.brand not in brands:
                brands[product.brand] = []
            brands[product.brand].append(product)
        
        for brand, brand_products in brands.items():
            comparison["brand_analysis"][brand] = {
                "product_count": len(brand_products),
                "price_range": self._get_brand_price_range(brand_products),
                "unique_ingredients": self._get_unique_ingredients(brand_products),
                "positioning": self._analyze_brand_positioning(brand_products)
            }
        
        # Format distribution
        formats = {}
        for product in products:
            format_name = product.format or "unknown"
            formats[format_name] = formats.get(format_name, 0) + 1
        comparison["format_distribution"] = formats
        
        return comparison
    
    def _identify_data_gaps(self, products: List[EnhancedProduct]) -> List[str]:
        """Identify missing critical data for analysis"""
        gaps = []
        
        # Check for missing ingredient information
        products_missing_ingredients = [p.name for p in products if not p.ingredients]
        if products_missing_ingredients:
            gaps.append(f"Ingredient lists missing for: {', '.join(products_missing_ingredients[:3])}{'...' if len(products_missing_ingredients) > 3 else ''}")
        
        # Check for missing concentrations
        products_missing_concentrations = []
        for product in products:
            if product.ingredients:
                missing_conc = [ing.name for ing in product.ingredients if ing.role.value in ["active", "functional"] and not ing.concentration]
                if missing_conc:
                    products_missing_concentrations.append(product.name)
        
        if products_missing_concentrations:
            gaps.append(f"Active ingredient concentrations missing for: {', '.join(products_missing_concentrations[:3])}{'...' if len(products_missing_concentrations) > 3 else ''}")
        
        # Check for missing pricing data
        products_missing_pricing = [p.name for p in products if not p.pricing or not p.pricing.base_price]
        if products_missing_pricing:
            gaps.append(f"Pricing data missing for: {', '.join(products_missing_pricing[:3])}{'...' if len(products_missing_pricing) > 3 else ''}")
        
        return gaps
    
    def _calculate_analysis_confidence(self, products: List[EnhancedProduct], data_gaps: List[str]) -> float:
        """Calculate confidence score for analysis"""
        base_confidence = 1.0
        
        # Deduct for data gaps
        gap_penalty = len(data_gaps) * 0.15
        confidence = base_confidence - gap_penalty
        
        # Adjust based on sample size
        if len(products) < 3:
            confidence -= 0.2  # Small sample size
        elif len(products) > 10:
            confidence += 0.1  # Good sample size
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_insights(self, products: List[EnhancedProduct], analysis: Dict[str, Any]) -> List[str]:
        """Generate evidence-based insights"""
        insights = []
        
        # Functional ingredient insights
        functional_analysis = analysis.get("functional_analysis", {})
        if functional_analysis.get("most_common_actives"):
            top_ingredient = functional_analysis["most_common_actives"][0]
            insights.append(f"Most common active ingredient: {top_ingredient[0]} (found in {top_ingredient[1]} products)")
        
        # Pricing insights
        pricing_analysis = analysis.get("pricing_analysis", {})
        if pricing_analysis.get("per_serving_range"):
            avg_per_serving = pricing_analysis["per_serving_range"]["average"]
            insights.append(f"Average cost per serving: ${avg_per_serving}")
        
        # Market gap insights
        if analysis["data_gaps"]:
            insights.append(f"Analysis limited by missing data: {len(analysis['data_gaps'])} critical gaps identified")
        
        return insights
    
    def _assess_evidence_quality(self, products: List[EnhancedProduct], analysis: Dict[str, Any]) -> str:
        """Assess quality of evidence for analysis"""
        confidence = analysis.get("analysis_confidence", 0.0)
        
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "insufficient"
    
    def _generate_analysis_recommendations(self, products: List[EnhancedProduct], analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if analysis["evidence_quality"] in ["low", "insufficient"]:
            recommendations.append("Analysis confidence is low - additional product data needed for reliable insights")
        
        if analysis["data_gaps"]:
            recommendations.append("Consider obtaining missing data for more comprehensive analysis")
        
        if len(products) < 5:
            recommendations.append("Expand product sample size for more robust comparative analysis")
        
        return recommendations
    
    def _load_functional_ingredients(self) -> Dict[str, List[str]]:
        """Load ingredient to function mapping"""
        return {
            "hyaluronic acid": ["hydration", "plumping"],
            "vitamin c": ["antioxidant", "brightening", "collagen_synthesis"],
            "retinol": ["anti_aging", "cell_turnover", "collagen_synthesis"],
            "niacinamide": ["pore_minimizing", "oil_control", "brightening"],
            "salicylic acid": ["exfoliation", "acne_treatment", "pore_cleansing"],
            "ceramides": ["barrier_repair", "hydration", "moisture_retention"],
            "peptides": ["anti_aging", "collagen_synthesis", "firming"],
            "glycolic acid": ["exfoliation", "brightening", "texture_improvement"],
            "zinc": ["skin_health", "healing", "oil_control"],
            "biotin": ["skin_health", "barrier_function"]
        }
    
    def _load_market_benchmarks(self) -> Dict[str, Any]:
        """Load market benchmarks for comparison"""
        return {
            "average_collagen_serving_cost": 1.50,
            "premium_price_threshold": 3.00,
            "mass_market_price_threshold": 1.00
        }
    
    # Helper methods
    def _get_brand_price_range(self, products: List[EnhancedProduct]) -> Dict[str, float]:
        """Get price range for a brand"""
        prices = [p.pricing.base_price for p in products if p.pricing and p.pricing.base_price]
        if not prices:
            return {"min": 0, "max": 0, "average": 0}
        return {
            "min": min(prices),
            "max": max(prices),
            "average": round(sum(prices) / len(prices), 2)
        }
    
    def _get_unique_ingredients(self, products: List[EnhancedProduct]) -> List[str]:
        """Get unique ingredients for a brand"""
        all_ingredients = set()
        for product in products:
            for ingredient in product.ingredients:
                all_ingredients.add(ingredient.name.lower())
        return list(all_ingredients)
    
    def _analyze_brand_positioning(self, products: List[EnhancedProduct]) -> str:
        """Analyze brand positioning"""
        avg_price = self._get_brand_price_range(products)["average"]
        
        if avg_price > self.market_benchmarks["premium_price_threshold"]:
            return "premium"
        elif avg_price < self.market_benchmarks["mass_market_price_threshold"]:
            return "mass_market"
        else:
            return "mid_tier"
    
    def _create_no_products_analysis(self, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis when no products found"""
        return {
            "total_products": 0,
            "analysis_confidence": 0.0,
            "data_gaps": ["No products found for analysis"],
            "key_insights": ["No product data available for the specified query"],
            "recommendations": [
                "Expand search criteria to find relevant products",
                "Check if product database contains items matching your query",
                "Consider alternative search terms or categories"
            ],
            "evidence_quality": "none"
        }
    
    def _create_fallback_analysis(self, products: List[EnhancedProduct], error: str) -> Dict[str, Any]:
        """Create fallback analysis when processing fails"""
        return {
            "total_products": len(products),
            "analysis_confidence": 0.0,
            "data_gaps": [f"Analysis failed: {error}"],
            "key_insights": ["Product analysis encountered technical difficulties"],
            "recommendations": [
                "Technical analysis failed - using basic product information only",
                "Consider re-running analysis or using simplified queries"
            ],
            "evidence_quality": "none"
        }
