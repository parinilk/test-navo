"""
Enhanced Query Processor
Integrates Intent Router, Three-Tier Filters, and LLM Filter Extraction
Implements the complete RAG Filters.md architecture
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .intent_router import intent_router, DatasetType
from .three_tier_filters import three_tier_filter_extractor
from .llm_filter_extractor import llm_filter_extractor
from .clarification_node import clarification_node

logger = logging.getLogger(__name__)

class EnhancedQueryProcessor:
    """
    Complete implementation of RAG Filters.md architecture:
    User Query → Intent Router → Filter Extractor → Retriever(s) → Answer Composer
    """
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
        # Initialize LLM filter extractor with LLM service
        if llm_service:
            llm_filter_extractor.llm_service = llm_service
    
    async def process_query_complete(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        use_llm_extraction: bool = True
    ) -> Dict[str, Any]:
        """
        Complete query processing following RAG Filters.md architecture
        
        Flow:
        1. Intent Router (route to datasets)
        2. Filter Extractor (LLM or rule-based)
        3. Prepare retrieval strategy
        
        Args:
            query: User query string
            context: Optional context information
            use_llm_extraction: Whether to use LLM for filter extraction
            
        Returns:
            Complete processing result with routing and filters
        """
        logger.info(f"🚀 Processing query with enhanced RAG architecture: '{query[:50]}...'")
        
        processing_start = datetime.utcnow()
        result = {
            "query": query,
            "context": context or {},
            "processing_timestamp": processing_start.isoformat(),
            "pipeline_steps": []
        }
        
        try:
            # Step 0: Clarification Node - Check if query needs clarification (RAG Filters.md position)
            logger.info("🤔 Step 0: Clarification Assessment")
            step0_start = datetime.utcnow()
            
            # Skip clarification if context suggests it should be bypassed
            if not clarification_node.should_bypass_clarification(context):
                clarity_assessment = clarification_node.assess_query_clarity(query, context)
                
                result["clarification_assessment"] = clarity_assessment
                result["pipeline_steps"].append({
                    "step": "clarification_assessment",
                    "duration_ms": (datetime.utcnow() - step0_start).total_seconds() * 1000,
                    "status": "completed",
                    "clarity_score": clarity_assessment["clarity_score"],
                    "needs_clarification": clarity_assessment["needs_clarification"]
                })
                
                # Return early if clarification is required
                if clarity_assessment["needs_clarification"] and clarity_assessment.get("clarification_type") == "required":
                    result["clarification_required"] = True
                    result["clarification_response"] = clarification_node.format_clarification_response(clarity_assessment, query)
                    logger.info(f"🔄 Query requires clarification (clarity: {clarity_assessment['clarity_score']:.2f})")
                    return result
                
                logger.info(f"✅ Clarity assessment passed (score: {clarity_assessment['clarity_score']:.2f})")
            else:
                logger.info("⏭️ Clarification bypassed based on context")
                result["clarification_assessment"] = {"bypassed": True, "reason": "Context bypass"}
            
            # Step 1: Intent Router - Route to appropriate datasets
            logger.info("📍 Step 1: Intent Routing")
            step1_start = datetime.utcnow()
            
            routing_result = intent_router.route_query(query, context)
            
            result["intent_routing"] = routing_result
            result["pipeline_steps"].append({
                "step": "intent_routing",
                "duration_ms": (datetime.utcnow() - step1_start).total_seconds() * 1000,
                "status": "completed",
                "primary_dataset": routing_result["primary_dataset"].value,
                "confidence": routing_result["confidence"]
            })
            
            logger.info(f"✅ Routed to {routing_result['primary_dataset'].value} (confidence: {routing_result['confidence']:.2f})")
            
            # Step 2: Filter Extraction
            logger.info("🔍 Step 2: Filter Extraction")
            step2_start = datetime.utcnow()
            
            if use_llm_extraction and self.llm_service:
                # LLM-based extraction (preferred method from RAG Filters.md)
                filter_result = await llm_filter_extractor.extract_filters_with_llm(query, context)
            else:
                # Fallback to rule-based three-tier extraction
                filter_result = three_tier_filter_extractor.extract_all_filters(query, context)
                filter_result = {
                    "extracted_filters": self._flatten_tier_filters(filter_result),
                    "extraction_method": "rule_based",
                    "confidence": 0.7
                }
            
            result["filter_extraction"] = filter_result
            result["pipeline_steps"].append({
                "step": "filter_extraction",
                "duration_ms": (datetime.utcnow() - step2_start).total_seconds() * 1000,
                "status": "completed",
                "method": filter_result.get("extraction_method", "unknown"),
                "filters_count": len(filter_result.get("extracted_filters", {}))
            })
            
            logger.info(f"✅ Extracted {len(filter_result.get('extracted_filters', {}))} filters using {filter_result.get('extraction_method')}")
            
            # Step 3: Prepare Retrieval Strategy
            logger.info("🎯 Step 3: Retrieval Strategy")
            step3_start = datetime.utcnow()
            
            retrieval_strategy = self._prepare_retrieval_strategy(
                routing_result, 
                filter_result, 
                query, 
                context
            )
            
            result["retrieval_strategy"] = retrieval_strategy
            result["pipeline_steps"].append({
                "step": "retrieval_strategy",
                "duration_ms": (datetime.utcnow() - step3_start).total_seconds() * 1000,
                "status": "completed",
                "strategy_type": retrieval_strategy["strategy_type"]
            })
            
            logger.info(f"✅ Prepared {retrieval_strategy['strategy_type']} retrieval strategy")
            
            # Step 4: Quality Assessment
            result["quality_assessment"] = self._assess_processing_quality(result)
            
            # Total processing time
            total_duration = (datetime.utcnow() - processing_start).total_seconds() * 1000
            result["total_processing_time_ms"] = total_duration
            
            logger.info(f"🎉 Enhanced query processing completed in {total_duration:.0f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced query processing failed: {e}")
            result["error"] = {
                "message": str(e),
                "type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            return result
    
    def _flatten_tier_filters(self, tier_result: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten three-tier filter result to simple dict"""
        flattened = {}
        
        for tier_name, tier_filters in tier_result.items():
            if tier_name.startswith("tier_") and isinstance(tier_filters, dict):
                flattened.update(tier_filters)
        
        return flattened
    
    def _prepare_retrieval_strategy(
        self, 
        routing_result: Dict[str, Any], 
        filter_result: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare retrieval strategy based on routing and filters
        """
        primary_dataset = DatasetType(routing_result["primary_dataset"])
        secondary_datasets = [DatasetType(d) for d in routing_result.get("secondary_datasets", [])]
        extracted_filters = filter_result.get("extracted_filters", {})
        
        strategy = {
            "strategy_type": routing_result["query_strategy"],
            "collections": routing_result["collections_needed"],
            "vector_search_config": self._prepare_vector_search_config(extracted_filters),
            "database_filters": self._prepare_database_filters(extracted_filters),
            "search_parameters": {
                "similarity_threshold": self._calculate_similarity_threshold(routing_result),
                "top_k": self._calculate_top_k(extracted_filters),
                "rerank": routing_result["confidence"] < 0.8  # Rerank if low confidence
            },
            "web_search_trigger": self._should_trigger_web_search(routing_result, filter_result, query),
            "clarification_needed": self._assess_clarification_need(routing_result, filter_result)
        }
        
        # Dataset-specific optimizations
        if primary_dataset == DatasetType.REGULATORY_COMPLIANCE:
            strategy["search_parameters"]["similarity_threshold"] = 0.85  # Higher precision for regulatory
            strategy["require_exact_jurisdiction"] = True
            
        elif primary_dataset == DatasetType.PRODUCT_DATA:
            strategy["search_parameters"]["top_k"] = min(20, strategy["search_parameters"]["top_k"] * 2)  # More products
            strategy["enable_price_sorting"] = "price_range" in extracted_filters
            
        elif primary_dataset == DatasetType.BOTH:
            strategy["fusion_method"] = "weighted_combine"
            strategy["regulatory_weight"] = 0.6 if filter_result.get("regulatory_sensitive") else 0.3
        
        return strategy
    
    def _prepare_vector_search_config(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare configuration for vector search based on extracted filters"""
        config = {
            "query_expansion": [],
            "metadata_filters": {},
            "boost_fields": []
        }
        
        # Add filter-based query expansion
        if "primary_benefit" in filters:
            benefit = filters["primary_benefit"]
            if benefit == "Skin Health":
                config["query_expansion"].extend(["skincare", "complexion", "glow", "hydration"])
            elif benefit == "Joint Support":
                config["query_expansion"].extend(["mobility", "flexibility", "cartilage", "inflammation"])
        
        # Add ingredient-based boosts
        if "ingredient_name" in filters:
            ingredients = filters["ingredient_name"]
            if isinstance(ingredients, list):
                config["boost_fields"].extend(ingredients)
            else:
                config["boost_fields"].append(ingredients)
        
        # Add metadata filters
        for filter_name in ["format", "brand", "usage_context", "jurisdiction"]:
            if filter_name in filters:
                config["metadata_filters"][filter_name] = filters[filter_name]
        
        return config
    
    def _prepare_database_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare MongoDB filters from extracted filters"""
        db_filters = {}
        
        # Direct field mappings
        field_mappings = {
            "brand": "brand",
            "format": "category",  # Assuming format maps to category
            "jurisdiction": "compliance_region"
        }
        
        for filter_name, db_field in field_mappings.items():
            if filter_name in filters:
                db_filters[db_field] = {"$regex": filters[filter_name], "$options": "i"}
        
        # Price range filters
        if "price_range" in filters:
            price_range = filters["price_range"]
            if price_range == "Under $20":
                db_filters["price"] = {"$lt": 20}
            elif price_range == "$20-$40":
                db_filters["price"] = {"$gte": 20, "$lt": 40}
            elif price_range == "$40-$60":
                db_filters["price"] = {"$gte": 40, "$lt": 60}
            elif price_range == "Over $60":
                db_filters["price"] = {"$gte": 60}
        
        # Ingredient filters
        if "ingredient_name" in filters:
            ingredients = filters["ingredient_name"]
            if isinstance(ingredients, list):
                # Match any of the ingredients
                db_filters["ingredients"] = {"$in": [{"$regex": ing, "$options": "i"} for ing in ingredients]}
            else:
                db_filters["ingredients"] = {"$regex": ingredients, "$options": "i"}
        
        return db_filters
    
    def _calculate_similarity_threshold(self, routing_result: Dict[str, Any]) -> float:
        """Calculate appropriate similarity threshold based on routing confidence"""
        base_threshold = 0.75
        confidence = routing_result["confidence"]
        
        # Higher confidence = can use lower threshold (more results)
        # Lower confidence = need higher threshold (more precise results)
        if confidence > 0.9:
            return base_threshold - 0.1
        elif confidence < 0.6:
            return base_threshold + 0.1
        else:
            return base_threshold
    
    def _calculate_top_k(self, filters: Dict[str, Any]) -> int:
        """Calculate appropriate top_k based on filter specificity"""
        base_k = 10
        
        # More specific filters = can retrieve more results
        filter_count = len(filters)
        
        if filter_count >= 4:
            return base_k + 5  # Very specific, get more results
        elif filter_count >= 2:
            return base_k + 2  # Moderately specific
        else:
            return base_k  # Not very specific, keep it focused
    
    def _should_trigger_web_search(
        self, 
        routing_result: Dict[str, Any], 
        filter_result: Dict[str, Any], 
        query: str
    ) -> bool:
        """
        Determine if web search should be triggered (enhanced to handle data insufficiency)
        """
        # Trigger conditions from RAG Filters.md
        trigger_keywords = ["FDA", "recent news", "latest", "new", "updates", "current"]
        
        # Check for trigger keywords
        if any(keyword in query.lower() for keyword in trigger_keywords):
            return True
        
        # Low confidence routing might benefit from web search
        if routing_result["confidence"] < 0.5:
            return True
        
        # Regulatory queries might need current information
        if DatasetType(routing_result["primary_dataset"]) == DatasetType.REGULATORY_COMPLIANCE:
            regulatory_trigger = ["regulation", "approved", "banned", "updated"]
            if any(keyword in query.lower() for keyword in regulatory_trigger):
                return True
        
        # NEW: Automatically trigger web search for market analysis queries
        market_analysis_keywords = [
            "pricing", "price", "cost", "median", "competitive", "competitors",
            "market", "brands", "products", "analysis", "landscape", "strategy",
            "premium", "value", "affordable", "expensive", "comparison"
        ]
        
        if any(keyword in query.lower() for keyword in market_analysis_keywords):
            return True
        
        # NEW: Trigger web search for queries that need current market data
        current_market_keywords = [
            "which brands", "how do", "compare", "differences", "trends",
            "latest products", "new launches", "market position", "competitive advantage"
        ]
        
        if any(keyword in query.lower() for keyword in current_market_keywords):
            return True
        
        # NEW: Trigger web search when data quality is poor
        if filter_result.get("data_quality_score", 1.0) < 0.6:
            return True
        
        return False
    
    def _assess_clarification_need(
        self, 
        routing_result: Dict[str, Any], 
        filter_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess if query needs clarification"""
        clarification = {
            "needed": False,
            "confidence_threshold": 0.6,
            "reasons": [],
            "suggested_clarifications": []
        }
        
        # Low routing confidence
        if routing_result["confidence"] < clarification["confidence_threshold"]:
            clarification["needed"] = True
            clarification["reasons"].append("Low routing confidence")
            clarification["suggested_clarifications"].append("Please specify your primary goal")
        
        # No filters extracted
        if not filter_result.get("extracted_filters"):
            clarification["needed"] = True
            clarification["reasons"].append("No specific filters identified")
            clarification["suggested_clarifications"].append("Please provide more specific criteria")
        
        # Conflicting datasets needed
        if len(routing_result.get("secondary_datasets", [])) > 1:
            clarification["needed"] = True
            clarification["reasons"].append("Multiple data sources needed")
            clarification["suggested_clarifications"].append("Please clarify your primary focus")
        
        return clarification
    
    def _assess_processing_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality of the processing pipeline"""
        quality = {
            "overall_score": 0.0,
            "component_scores": {},
            "recommendations": []
        }
        
        # Intent routing quality
        routing_confidence = result.get("intent_routing", {}).get("confidence", 0)
        quality["component_scores"]["intent_routing"] = routing_confidence
        
        # Filter extraction quality
        filter_confidence = result.get("filter_extraction", {}).get("confidence", 0)
        quality["component_scores"]["filter_extraction"] = filter_confidence
        
        # Processing speed quality (faster = better, up to reasonable limit)
        processing_time = result.get("total_processing_time_ms", 1000)
        speed_score = max(0, min(1.0, (2000 - processing_time) / 2000))
        quality["component_scores"]["processing_speed"] = speed_score
        
        # Calculate overall score
        quality["overall_score"] = (
            routing_confidence * 0.4 + 
            filter_confidence * 0.4 + 
            speed_score * 0.2
        )
        
        # Add recommendations
        if routing_confidence < 0.7:
            quality["recommendations"].append("Consider query clarification")
        if filter_confidence < 0.6:
            quality["recommendations"].append("May benefit from more specific terms")
        if processing_time > 1500:
            quality["recommendations"].append("Consider caching for similar queries")
        
        return quality

# Global instance
enhanced_query_processor = EnhancedQueryProcessor()
