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
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'ingredients'):
                ingredients = product.ingredients
            elif isinstance(product, dict) and 'ingredients' in product:
                ingredients = product['ingredients']
            else:
                # Skip products without ingredients
                continue
                
            for ingredient in ingredients:
                # Handle both Ingredient objects and dictionaries
                if hasattr(ingredient, 'name'):
                    ing_name = ingredient.name.lower()
                elif isinstance(ingredient, dict) and 'name' in ingredient:
                    ing_name = ingredient['name'].lower()
                else:
                    continue
                    
                # Track ingredient frequency
                ingredient_frequency[ing_name] = ingredient_frequency.get(ing_name, 0) + 1
                
                # Map to functional benefits
                if ing_name in self.functional_ingredient_map:
                    functions = self.functional_ingredient_map[ing_name]
                    for function in functions:
                        if function not in functional_profile:
                            functional_profile[function] = []
                        
                        # Handle both object and dictionary formats for ingredient and product
                        ingredient_name = ingredient.name if hasattr(ingredient, 'name') else ingredient.get('name', 'Unknown')
                        product_name = product.name if hasattr(product, 'name') else product.get('product_name', 'Unknown')
                        concentration = ingredient.concentration if hasattr(ingredient, 'concentration') else ingredient.get('concentration', None)
                        concentration_unit = ingredient.concentration_unit if hasattr(ingredient, 'concentration_unit') else ingredient.get('concentration_unit', None)
                        
                        functional_profile[function].append({
                            "ingredient": ingredient_name,
                            "product": product_name,
                            "concentration": concentration,
                            "concentration_unit": concentration_unit
                        })
                
                # Concentration analysis
                concentration = ingredient.concentration if hasattr(ingredient, 'concentration') else ingredient.get('concentration', None)
                if concentration:
                    if ing_name not in concentration_analysis:
                        concentration_analysis[ing_name] = []
                    
                    product_name = product.name if hasattr(product, 'name') else product.get('product_name', 'Unknown')
                    concentration_unit = ingredient.concentration_unit if hasattr(ingredient, 'concentration_unit') else ingredient.get('concentration_unit', None)
                    
                    concentration_analysis[ing_name].append({
                        "product": product_name,
                        "concentration": concentration,
                        "unit": concentration_unit
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
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'pricing') and product.pricing and hasattr(product.pricing, 'base_price'):
                # EnhancedProduct object
                pricing_obj = product.pricing
                price_info = {
                    "product_name": getattr(product, 'name', 'Unknown'),
                    "base_price": pricing_obj.base_price,
                    "currency": getattr(pricing_obj, 'currency', 'USD')
                }
                
                if hasattr(pricing_obj, 'servings_per_container') and pricing_obj.servings_per_container:
                    price_per_serving = pricing_obj.base_price / pricing_obj.servings_per_container
                    price_info["price_per_serving"] = price_per_serving
                
                if hasattr(pricing_obj, 'quantity') and hasattr(pricing_obj, 'quantity_unit') and pricing_obj.quantity:
                    price_per_unit = pricing_obj.base_price / pricing_obj.quantity
                    price_info["price_per_unit"] = price_per_unit
                    price_info["unit"] = pricing_obj.quantity_unit
                
                pricing_data.append(price_info)
                
            elif isinstance(product, dict):
                # Dictionary format - look for pricing fields
                price_info = {
                    "product_name": product.get('product_name', 'Unknown'),
                    "base_price": None,
                    "currency": "USD"
                }
                
                # Check for different possible pricing field names
                if 'price' in product and product['price']:
                    price_info["base_price"] = float(product['price'])
                elif 'pricing' in product and isinstance(product['pricing'], dict):
                    pricing_dict = product['pricing']
                    if 'base_price' in pricing_dict:
                        price_info["base_price"] = float(pricing_dict['base_price'])
                    elif 'price' in pricing_dict:
                        price_info["base_price"] = float(pricing_dict['price'])
                
                # Check for servings information
                if 'servings_per_container' in product and product['servings_per_container']:
                    try:
                        servings = float(product['servings_per_container'])
                        if price_info["base_price"]:
                            price_info["price_per_serving"] = price_info["base_price"] / servings
                    except (ValueError, TypeError):
                        pass
                
                # Only add if we have some pricing information
                if price_info["base_price"]:
                    pricing_data.append(price_info)
        
        if not pricing_data:
            return {"error": "No pricing data available", "products_with_pricing": 0}
        
        # Calculate pricing statistics
        base_prices = [p["base_price"] for p in pricing_data if p["base_price"]]
        per_serving_prices = [p["price_per_serving"] for p in pricing_data if "price_per_serving" in p and p["price_per_serving"]]
        
        return {
            "products_with_pricing": len(pricing_data),
            "base_price_range": {"min": min(base_prices), "max": max(base_prices), "average": sum(base_prices) / len(base_prices)} if base_prices else {},
            "per_serving_range": {"min": min(per_serving_prices), "max": max(per_serving_prices), "average": sum(per_serving_prices) / len(per_serving_prices)} if per_serving_prices else {},
            "detailed_pricing": pricing_data
        }
    
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
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'brand') and product.brand:
                brand_name = product.brand
            elif isinstance(product, dict) and product.get('brand'):
                brand_name = product['brand']
            else:
                continue  # Skip products without brand information
                
            if brand_name not in brands:
                brands[brand_name] = []
            brands[brand_name].append(product)
        
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
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'format') and product.format:
                format_name = product.format
            elif isinstance(product, dict) and product.get('format'):
                format_name = product['format']
            else:
                format_name = "unknown"
                
            formats[format_name] = formats.get(format_name, 0) + 1
        comparison["format_distribution"] = formats
        
        return comparison
    
    def _identify_data_gaps(self, products: List[EnhancedProduct]) -> List[str]:
        """Identify missing data that limits analysis quality"""
        gaps = []
        
        if not products:
            gaps.append("No products found in dataset")
            return gaps
        
        # Check for missing ingredient data
        products_missing_ingredients = []
        for product in products:
            if hasattr(product, 'ingredients'):
                if not product.ingredients:
                    products_missing_ingredients.append(getattr(product, 'name', 'Unknown'))
            elif isinstance(product, dict):
                if not product.get('ingredients'):
                    products_missing_ingredients.append(product.get('product_name', 'Unknown'))
        
        if products_missing_ingredients:
            gaps.append(f"Ingredient information missing for {len(products_missing_ingredients)} products")
        
        # Check for missing pricing data
        products_missing_pricing = []
        for product in products:
            if hasattr(product, 'pricing') and product.pricing and hasattr(product.pricing, 'base_price'):
                if not product.pricing.base_price:
                    products_missing_pricing.append(getattr(product, 'name', 'Unknown'))
            elif isinstance(product, dict):
                has_price = False
                if 'price' in product and product['price']:
                    has_price = True
                elif 'pricing' in product and isinstance(product['pricing'], dict):
                    pricing_dict = product['pricing']
                    if 'base_price' in pricing_dict and pricing_dict['base_price']:
                        has_price = True
                    elif 'price' in pricing_dict and pricing_dict['price']:
                        has_price = True
                
                if not has_price:
                    products_missing_pricing.append(product.get('product_name', 'Unknown'))
        
        if products_missing_pricing:
            gaps.append(f"Pricing information missing for {len(products_missing_pricing)} products")
        
        # Check for missing brand information
        products_missing_brand = []
        for product in products:
            if hasattr(product, 'brand'):
                if not product.brand:
                    products_missing_brand.append(getattr(product, 'name', 'Unknown'))
            elif isinstance(product, dict):
                if not product.get('brand'):
                    products_missing_brand.append(product.get('product_name', 'Unknown'))
        
        if products_missing_brand:
            gaps.append(f"Brand information missing for {len(products_missing_brand)} products")
        
        return gaps
    
    def _calculate_analysis_confidence(self, products: List[EnhancedProduct], data_gaps: List[str]) -> float:
        """Calculate confidence score based on data completeness"""
        if not products:
            return 0.0
        
        # Base confidence starts at 0.5
        confidence = 0.5
        
        # Add confidence for each product with complete data
        for product in products:
            product_confidence = 0.0
            
            # Check ingredients
            if hasattr(product, 'ingredients') and product.ingredients:
                product_confidence += 0.2
            elif isinstance(product, dict) and product.get('ingredients'):
                product_confidence += 0.2
            
            # Check pricing
            if hasattr(product, 'pricing') and product.pricing and hasattr(product.pricing, 'base_price') and product.pricing.base_price:
                product_confidence += 0.2
            elif isinstance(product, dict):
                has_price = False
                if 'price' in product and product['price']:
                    has_price = True
                elif 'pricing' in product and isinstance(product['pricing'], dict):
                    pricing_dict = product['pricing']
                    if 'base_price' in pricing_dict and pricing_dict['base_price']:
                        has_price = True
                    elif 'price' in pricing_dict and pricing_dict['price']:
                        has_price = True
                
                if has_price:
                    product_confidence += 0.2
            
            # Check brand
            if hasattr(product, 'brand') and product.brand:
                product_confidence += 0.1
            elif isinstance(product, dict) and product.get('brand'):
                product_confidence += 0.1
            
            # Check category
            if hasattr(product, 'category') and product.category:
                product_confidence += 0.1
            elif isinstance(product, dict) and product.get('category'):
                product_confidence += 0.1
            
            # Add to total confidence
            confidence += product_confidence
        
        # Penalize for data gaps
        gap_penalty = len(data_gaps) * 0.05
        confidence = max(0.0, confidence - gap_penalty)
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    def _generate_insights(self, products: List[EnhancedProduct], analysis: Dict[str, Any]) -> List[str]:
        """Generate insights based on analysis results"""
        insights = []
        
        if not products:
            insights.append("No products available for analysis")
            return insights
        
        # Product count insights
        insights.append(f"Analyzed {len(products)} products in the dataset")
        
        # Pricing insights
        pricing_analysis = analysis.get("pricing_analysis", {})
        if pricing_analysis.get("base_price_range"):
            price_range = pricing_analysis["base_price_range"]
            insights.append(f"Price range: ${price_range['min']:.2f} - ${price_range['max']:.2f} (avg: ${price_range['average']:.2f})")
        
        if pricing_analysis.get("per_serving_range"):
            serving_range = pricing_analysis["per_serving_range"]
            insights.append(f"Per-serving cost range: ${serving_range['min']:.2f} - ${serving_range['max']:.2f} (avg: ${serving_range['average']:.2f})")
        
        # Functional ingredient insights
        functional_analysis = analysis.get("functional_analysis", {})
        if functional_analysis.get("functional_benefits"):
            profile = functional_analysis["functional_benefits"]
            top_functions = sorted(profile.items(), key=lambda x: len(x[1]), reverse=True)[:3]
            insights.append(f"Top functional benefits: {', '.join([f'{func} ({len(products)} products)' for func, products in top_functions])}")
        
        # Data quality insights
        data_gaps = analysis.get("data_gaps", [])
        if data_gaps:
            insights.append(f"Data gaps identified: {len(data_gaps)} areas need improvement")
        
        # Confidence insights
        confidence = analysis.get("analysis_confidence", 0)
        if confidence < 0.5:
            insights.append("Analysis confidence is low due to missing data")
        elif confidence > 0.8:
            insights.append("High confidence analysis with comprehensive data")
        else:
            insights.append("Moderate confidence analysis with some data limitations")
        
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
        prices = []
        for product in products:
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'pricing') and product.pricing and hasattr(product.pricing, 'base_price') and product.pricing.base_price:
                prices.append(product.pricing.base_price)
            elif isinstance(product, dict):
                if 'price' in product and product['price']:
                    prices.append(float(product['price']))
                elif 'pricing' in product and isinstance(product['pricing'], dict):
                    pricing_dict = product['pricing']
                    if 'base_price' in pricing_dict and pricing_dict['base_price']:
                        prices.append(float(pricing_dict['base_price']))
                    elif 'price' in pricing_dict and pricing_dict['price']:
                        prices.append(float(pricing_dict['price']))
        
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
            # Handle both EnhancedProduct objects and dictionaries
            if hasattr(product, 'ingredients'):
                ingredients = product.ingredients
            elif isinstance(product, dict) and 'ingredients' in product:
                ingredients = product['ingredients']
            else:
                continue
                
            for ingredient in ingredients:
                # Handle both Ingredient objects and dictionaries
                if hasattr(ingredient, 'name'):
                    all_ingredients.add(ingredient.name.lower())
                elif isinstance(ingredient, dict) and 'name' in ingredient:
                    all_ingredients.add(ingredient['name'].lower())
        
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
