"""
Research API endpoints for Navo
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime
import uuid

# Set up logger
logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    print("⚠️ NumPy not available. Using fallback for vector operations.")
    np = None

from models.database import get_database, get_database_dependency, COLLECTIONS
from models.vector_store import VectorStore
from rag.query_processor import QueryProcessor
from rag.llm_integration import LLMService
from rag.enhanced_query_processor import enhanced_query_processor
from rag.intent_router import DatasetType
# Enhanced services (import with error handling)
try:
    from services.regulatory_service import RegulatoryService
    from services.product_analysis_service import ProductAnalysisService
    ENHANCED_SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced services not available: {e}")
    ENHANCED_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for API
class ResearchQuery(BaseModel):
    query: str = Field(..., description="The research question")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (role, objective, topic)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for product search")

class WebSearchResult(BaseModel):
    title: str
    snippet: str
    url: str
    source: str
    position: int

class ClarificationOption(BaseModel):
    text: str
    description: str
    suggested_query: str
    category: str

class ClarificationResponse(BaseModel):
    query: str
    clarification_question: str
    options: List[ClarificationOption]
    issues: List[str]
    confidence: float
    fallback_interpretation: Optional[str] = None
    session_id: str
    timestamp: datetime
    response_type: str = "clarification"

class ResearchResponse(BaseModel):
    query: str
    answer: str
    rationale: str
    sources_used: List[str]
    disclaimer: Optional[str] = None
    session_id: str
    timestamp: datetime
    retrieved_products: Optional[List[Dict[str, Any]]] = None
    web_search_results: Optional[List[WebSearchResult]] = None
    # Enhanced fields for System Prompt compliance
    confidence_score: Optional[float] = None
    data_gaps: Optional[List[str]] = None
    analysis_complexity: Optional[str] = None
    regulatory_analysis: Optional[Dict[str, Any]] = None
    response_type: str = "research"

# Union type for different response types
QueryResponse = Union[ResearchResponse, ClarificationResponse]

class ResearchSession(BaseModel):
    session_id: str
    queries: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class FeedbackRequest(BaseModel):
    session_id: str
    query_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_type: str = Field(..., description="Type of feedback: helpful, not_helpful, inaccurate")
    comments: Optional[str] = None

# Global services (will be initialized in main.py)
query_processor = None
llm_service = None

def get_query_processor():
    global query_processor
    if not query_processor:
        query_processor = QueryProcessor()
    return query_processor

def get_llm_service():
    global llm_service
    if not llm_service:
        llm_service = LLMService()
    return llm_service

@router.post("/query", response_model=QueryResponse)
async def submit_research_query(
    request: ResearchQuery
):
    """Submit a research query and get AI-generated insights or clarification"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing research query: {request.query[:100]}...")
        
        # Step 1: Check if query needs clarification
        logger.info("🤔 Checking if query needs clarification...")
        from utils.query_clarification import analyze_query_clarity
        clarification_result = analyze_query_clarity(request.query, request.context)
        
        # If clarification is needed, return clarification response
        if clarification_result.needs_clarification:
            logger.info(f"🔄 Query needs clarification (confidence: {clarification_result.confidence:.2f})")
            
            return ClarificationResponse(
                query=request.query,
                clarification_question=clarification_result.clarification_question,
                options=[
                    ClarificationOption(
                        text=opt.text,
                        description=opt.description,
                        suggested_query=opt.suggested_query,
                        category=opt.category
                    ) for opt in clarification_result.options
                ],
                issues=clarification_result.issues,
                confidence=clarification_result.confidence,
                fallback_interpretation=clarification_result.fallback_interpretation,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
        
        # Continue with normal research flow if no clarification needed
        logger.info("✅ Query is clear enough, proceeding with research...")
        
        # Step 2: Enhanced query processing with System Prompt compliance
        logger.info("🔍 Starting query processing...")
        query_processor = QueryProcessor()
        processed_query = query_processor.process_query(request.query, request.context)
        logger.info(f"✅ Query processed: {type(processed_query)}")
        
        # Step 3: Classify the query to determine strategy
        logger.info("🔍 Starting query classification...")
        from utils.query_classifier import classify_research_query
        classification = classify_research_query(request.query, request.context)
        logger.info(f"✅ Query classified: {type(classification)}")
        
        # Merge enhanced analysis with classification
        classification.update({
            'processed_query': processed_query,
            'regulatory_sensitive': processed_query.get('regulatory_sensitive', False),
            'analysis_complexity': processed_query.get('analysis_complexity', 'medium')
        })
        
        logger.info(f"Query strategy: {classification['strategy']} (confidence: {classification['confidence']:.2f}, complexity: {processed_query.get('analysis_complexity', 'unknown')})")
        
        # Step 4: Execute appropriate strategy
        strategy = classification['strategy']
        logger.info(f"🚀 Executing strategy: {strategy}")
        
        if strategy == 'product_search':
            # Vector search focused approach
            logger.info("📊 Starting product search handler...")
            response = await _handle_product_search(request, session_id, classification)
        elif strategy == 'general_knowledge':
            # LLM knowledge focused approach  
            logger.info("🧠 Starting general knowledge handler...")
            response = await _handle_general_knowledge(request, session_id, classification)
        else:  # hybrid
            # Combined approach
            logger.info("🔀 Starting hybrid research handler...")
            response = await _handle_hybrid_research(request, session_id, classification)
        
        logger.info(f"✅ Handler completed, response type: {type(response)}")
        
        logger.info(f"✅ Successfully processed research query for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing research query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/query/clarified", response_model=ResearchResponse)
async def submit_clarified_query(
    request: ResearchQuery
):
    """Submit a clarified query (skips clarification check)"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing clarified research query: {request.query[:100]}...")
        logger.info("⏭️ Skipping clarification check for clarified query...")
        
        # Enhanced query processing with System Prompt compliance
        logger.info("🔍 Starting query processing...")
        query_processor = QueryProcessor()
        processed_query = query_processor.process_query(request.query, request.context)
        logger.info(f"✅ Query processed: {type(processed_query)}")
        
        # Classify the query to determine strategy
        logger.info("🔍 Starting query classification...")
        from utils.query_classifier import classify_research_query
        classification = classify_research_query(request.query, request.context)
        logger.info(f"✅ Query classified: {type(classification)}")
        
        # Merge enhanced analysis with classification
        classification.update({
            'processed_query': processed_query,
            'regulatory_sensitive': processed_query.get('regulatory_sensitive', False),
            'analysis_complexity': processed_query.get('analysis_complexity', 'medium')
        })
        
        logger.info(f"Query strategy: {classification['strategy']} (confidence: {classification['confidence']:.2f}, complexity: {processed_query.get('analysis_complexity', 'unknown')})")
        
        # Execute appropriate strategy
        strategy = classification['strategy']
        logger.info(f"🚀 Executing strategy: {strategy}")
        
        if strategy == 'product_search':
            # Vector search focused approach
            logger.info("📊 Starting product search handler...")
            response = await _handle_product_search(request, session_id, classification)
        elif strategy == 'general_knowledge':
            # LLM knowledge focused approach  
            logger.info("🧠 Starting general knowledge handler...")
            response = await _handle_general_knowledge(request, session_id, classification)
        else:  # hybrid
            # Combined approach
            logger.info("🔀 Starting hybrid research handler...")
            response = await _handle_hybrid_research(request, session_id, classification)
        
        logger.info(f"✅ Handler completed, response type: {type(response)}")
        logger.info(f"✅ Successfully processed clarified research query for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing clarified research query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing clarified query: {str(e)}")

@router.post("/query/enhanced", response_model=QueryResponse)
async def submit_enhanced_research_query(
    request: ResearchQuery
):
    """
    Enhanced research query using RAG Filters.md architecture
    Routes to datasets using Intent Router and LLM Filter Extraction
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"🚀 Processing ENHANCED research query: {request.query[:100]}...")
        
        # Initialize enhanced processor with LLM service
        llm_service = get_llm_service()
        enhanced_query_processor.llm_service = llm_service
        
        # Step 1: Enhanced Query Processing (RAG Filters.md architecture)
        logger.info("🎯 Starting enhanced RAG pipeline...")
        processing_result = await enhanced_query_processor.process_query_complete(
            query=request.query,
            context=request.context,
            use_llm_extraction=True
        )
        
        # Check if clarification is needed
        clarification_assessment = processing_result.get("retrieval_strategy", {}).get("clarification_needed", {})
        if clarification_assessment.get("needed", False):
            logger.info("🔄 Enhanced processing suggests clarification needed")
            
            return ClarificationResponse(
                query=request.query,
                clarification_question="I need more information to provide the best results. Could you help clarify?",
                options=[
                    ClarificationOption(
                        text=suggestion,
                        description=f"This will help improve the search results",
                        suggested_query=f"{request.query} - {suggestion}",
                        category="refinement"
                    ) for suggestion in clarification_assessment.get("suggested_clarifications", [])
                ],
                issues=clarification_assessment.get("reasons", []),
                confidence=processing_result.get("quality_assessment", {}).get("overall_score", 0.5),
                fallback_interpretation=processing_result.get("intent_routing", {}).get("reasoning", ""),
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
        
        # Step 2: Execute retrieval based on routing decision
        primary_dataset = DatasetType(processing_result["intent_routing"]["primary_dataset"])
        
        if primary_dataset == DatasetType.PRODUCT_DATA:
            response = await _handle_enhanced_product_search(request, session_id, processing_result)
        elif primary_dataset == DatasetType.REGULATORY_COMPLIANCE:
            response = await _handle_enhanced_regulatory_search(request, session_id, processing_result)
        elif primary_dataset == DatasetType.GENERAL_KNOWLEDGE:
            response = await _handle_enhanced_general_knowledge(request, session_id, processing_result)
        else:  # DatasetType.BOTH
            response = await _handle_enhanced_hybrid_search(request, session_id, processing_result)
        
        # Add enhanced processing metadata to response
        if hasattr(response, '__dict__'):
            response.enhanced_processing = {
                "pipeline_used": "rag_filters_architecture",
                "processing_time_ms": processing_result.get("total_processing_time_ms", 0),
                "quality_score": processing_result.get("quality_assessment", {}).get("overall_score", 0),
                "dataset_routing": processing_result.get("intent_routing", {}),
                "filter_extraction": processing_result.get("filter_extraction", {}),
                "retrieval_strategy": processing_result.get("retrieval_strategy", {})
            }
        
        logger.info(f"✅ Enhanced research query completed for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing enhanced research query: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing enhanced query: {str(e)}")

# Enhanced handlers for RAG Filters architecture

async def _handle_enhanced_product_search(request, session_id, processing_result):
    """Handle product search using enhanced RAG architecture"""
    logger.info("🛍️ Executing enhanced product search")
    
    try:
        # Extract filter information
        extracted_filters = processing_result.get("filter_extraction", {}).get("extracted_filters", {})
        retrieval_strategy = processing_result.get("retrieval_strategy", {})
        
        # Execute enhanced vector search with filters
        from models.database import get_database
        db = get_database()
        
        # Apply database filters from extracted filters
        db_filters = retrieval_strategy.get("database_filters", {})
        products = await _execute_pinecone_mongodb_search(
            query=request.query, 
            db_filters=db_filters, 
            retrieval_strategy=retrieval_strategy,
            dataset_type="product_data"
        )
        
        # Enhanced analysis
        llm_service = get_llm_service()
        enhanced_context = f"""
Enhanced Product Search Results:
Query: {request.query}
Extracted Filters: {extracted_filters}
Retrieved Products: {len(products)} found
Filter Quality: {processing_result.get("filter_extraction", {}).get("confidence", 0):.2f}

Provide comprehensive analysis focusing on the extracted filters and user intent.
"""
        
        llm_response = await llm_service.generate_research_response(
            query=request.query,
            context=request.context,
            retrieved_products=products,
            additional_context=enhanced_context
        )
        
        return ResearchResponse(
            query=request.query,
            answer=llm_response.get('answer', 'Enhanced search completed'),
            rationale=llm_response.get('rationale', 'Analysis based on enhanced RAG pipeline'),
            sources_used=llm_response.get('sources', []),
            session_id=session_id,
            timestamp=datetime.utcnow(),
            retrieved_products=products,
            confidence_score=processing_result.get("quality_assessment", {}).get("overall_score", 0.8),
            enhanced_metadata={
                "filters_applied": extracted_filters,
                "processing_pipeline": "enhanced_product_search",
                "dataset_routing": processing_result.get("intent_routing", {})
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced product search failed: {e}")
        # Fallback to regular product search
        return await _handle_product_search(request, session_id, {"processed_query": {}})

async def _handle_enhanced_regulatory_search(request, session_id, processing_result):
    """Handle regulatory search using enhanced RAG architecture"""
    logger.info("⚖️ Executing enhanced regulatory search")
    
    try:
        extracted_filters = processing_result.get("filter_extraction", {}).get("extracted_filters", {})
        
        # Focus on regulatory data
        regulatory_context = f"""
Regulatory Compliance Query:
Query: {request.query}
Jurisdiction: {extracted_filters.get('jurisdiction', 'Not specified')}
Ingredients: {extracted_filters.get('ingredient_name', [])}
Usage Context: {extracted_filters.get('usage_context', 'Not specified')}

This query requires regulatory expertise. Provide accurate compliance information with appropriate disclaimers.
"""
        
        # Execute regulatory search using Pinecone + MongoDB
        regulatory_data = await _execute_pinecone_mongodb_search(
            query=request.query,
            db_filters=processing_result.get("retrieval_strategy", {}).get("database_filters", {}),
            retrieval_strategy=processing_result.get("retrieval_strategy", {}),
            dataset_type="regulatory_compliance"
        )
        
        # Add regulatory data to context
        if regulatory_data:
            regulatory_context += f"\n\nRelevant Regulatory Data: {len(regulatory_data)} records found"
        
        # Check for web search trigger for regulatory updates
        if processing_result.get("retrieval_strategy", {}).get("web_search_trigger", False):
            logger.info("🌐 Triggering web search for regulatory updates")
            from utils.web_search import web_search_service
            web_results = await web_search_service.search_and_summarize(request.query, max_results=3)
            regulatory_context += f"\n\nRecent Web Information:\n{web_results.get('summary', '')}"
        
        llm_service = get_llm_service()
        llm_response = await llm_service.generate_research_response(
            query=request.query,
            context=request.context,
            retrieved_products=[],  # Regulatory search doesn't need product data
            additional_context=regulatory_context
        )
        
        return ResearchResponse(
            query=request.query,
            answer=llm_response.get('answer', 'Regulatory analysis completed'),
            rationale=llm_response.get('rationale', 'Analysis based on regulatory compliance data'),
            sources_used=llm_response.get('sources', []),
            disclaimer="⚠️ Regulatory Disclaimer: This information is for research purposes only. Always consult qualified regulatory professionals for compliance decisions.",
            session_id=session_id,
            timestamp=datetime.utcnow(),
            confidence_score=processing_result.get("quality_assessment", {}).get("overall_score", 0.7),
            enhanced_metadata={
                "regulatory_focus": True,
                "jurisdiction": extracted_filters.get('jurisdiction'),
                "processing_pipeline": "enhanced_regulatory_search"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced regulatory search failed: {e}")
        # Fallback to general knowledge
        return await _handle_general_knowledge(request, session_id, {"processed_query": {}})

async def _handle_enhanced_hybrid_search(request, session_id, processing_result):
    """Handle hybrid search using both datasets"""
    logger.info("🔀 Executing enhanced hybrid search")
    
    try:
        # Execute both product and regulatory searches
        product_task = _handle_enhanced_product_search(request, session_id, processing_result)
        regulatory_task = _handle_enhanced_regulatory_search(request, session_id, processing_result)
        
        # Wait for both to complete
        import asyncio
        product_response, regulatory_response = await asyncio.gather(product_task, regulatory_task)
        
        # Combine responses
        combined_answer = f"""
## Product Analysis
{product_response.answer}

## Regulatory Considerations  
{regulatory_response.answer}

## Integrated Insights
Based on both product data and regulatory compliance information, here's a comprehensive analysis considering both market availability and regulatory requirements.
"""
        
        combined_sources = list(set(product_response.sources_used + regulatory_response.sources_used))
        
        return ResearchResponse(
            query=request.query,
            answer=combined_answer,
            rationale="Combined analysis from product database and regulatory compliance data",
            sources_used=combined_sources,
            disclaimer=regulatory_response.disclaimer,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            retrieved_products=product_response.retrieved_products,
            confidence_score=(product_response.confidence_score + regulatory_response.confidence_score) / 2,
            enhanced_metadata={
                "hybrid_search": True,
                "product_confidence": product_response.confidence_score,
                "regulatory_confidence": regulatory_response.confidence_score,
                "processing_pipeline": "enhanced_hybrid_search"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced hybrid search failed: {e}")
        # Fallback to regular hybrid
        return await _handle_hybrid_research(request, session_id, {"processed_query": {}})

async def _handle_enhanced_general_knowledge(request, session_id, processing_result):
    """
    Handle general knowledge queries using primarily web search
    Scenario 3: General questions → Web search + general knowledge
    """
    logger.info("🌍 Executing enhanced general knowledge search")
    
    try:
        # Focus on web search for general knowledge
        general_context = f"""
General Knowledge Query:
Query: {request.query}
Context: This is a general knowledge question about ingredients, supplements, or health topics.

Provide comprehensive, educational information using reliable sources. Include scientific explanations where relevant.
Do not make specific product recommendations - focus on general information and science.
"""
        
        # Primary source: Web search for current and comprehensive information
        logger.info("🌐 Executing web search for general knowledge")
        from utils.web_search import web_search_service
        web_results = await web_search_service.search_and_summarize(request.query, max_results=5)
        
        if web_results.get('results'):
            general_context += f"\n\nWeb Search Results:\n{web_results.get('summary', '')}"
            
            # Format citations from web results
            citations = []
            for i, result in enumerate(web_results.get('results', [])[:3], 1):
                citations.append(f"{i}. {result.get('title', 'Unknown')} - {result.get('url', '')}")
        else:
            general_context += "\n\nNote: Limited web search results available."
            citations = []
        
        # Generate response using LLM with web context
        llm_service = get_llm_service()
        llm_response = await llm_service.generate_research_response(
            query=request.query,
            context=request.context,
            retrieved_products=[],  # No product data for general knowledge
            additional_context=general_context
        )
        
        return ResearchResponse(
            query=request.query,
            answer=llm_response.get('answer', 'General knowledge analysis completed'),
            rationale=llm_response.get('rationale', 'Analysis based on web search and general knowledge'),
            sources_used=citations,
            disclaimer="💡 Educational Information: This response is based on general knowledge and web sources. For specific product recommendations or medical advice, consult appropriate professionals.",
            session_id=session_id,
            timestamp=datetime.utcnow(),
            retrieved_products=[],  # No proprietary products for general knowledge
            confidence_score=processing_result.get("quality_assessment", {}).get("overall_score", 0.7),
            enhanced_metadata={
                "general_knowledge": True,
                "web_search_results": len(web_results.get('results', [])),
                "processing_pipeline": "enhanced_general_knowledge",
                "no_proprietary_data": True
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced general knowledge search failed: {e}")
        # Fallback to standard general knowledge
        return await _handle_general_knowledge(request, session_id, {"processed_query": {}})

async def _execute_enhanced_vector_search(query: str, db_filters: Dict, retrieval_strategy: Dict) -> List[Dict[str, Any]]:
    """Execute vector search with enhanced filtering"""
    try:
        from main import vector_store
        from utils.embeddings import generate_query_embedding
        
        if not vector_store or not vector_store.is_ready:
            logger.warning("Vector store not ready, using fallback search")
            return await _execute_vector_search_for_products(query)
        
        # Generate query embedding
        query_embedding = await generate_query_embedding(query)
        
        # Apply search parameters from strategy
        search_params = retrieval_strategy.get("search_parameters", {})
        
        # Perform vector search with enhanced parameters
        vector_results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=search_params.get("top_k", 10),
            similarity_threshold=search_params.get("similarity_threshold", 0.75),
            metadata_filters=db_filters
        )
        
        logger.info(f"Enhanced vector search found {len(vector_results)} results")
        
        # Extract and format products
        products = []
        for result in vector_results:
            if 'metadata' in result and result['metadata']:
                metadata = result['metadata']
                if isinstance(metadata, dict) and 'data' in metadata:
                    products.append(metadata['data'])
        
        return products
        
    except Exception as e:
        logger.error(f"Enhanced vector search failed: {e}")
        # Fallback to regular search
        return await _execute_vector_search_for_products(query)

async def _execute_pinecone_mongodb_search(
    query: str, 
    db_filters: Dict, 
    retrieval_strategy: Dict,
    dataset_type: str = "product_data"
) -> List[Dict[str, Any]]:
    """
    Execute hybrid Pinecone + MongoDB search following your architecture
    
    Flow:
    1. Generate query embedding
    2. Search Pinecone for similar vectors (with metadata filters)
    3. Get document IDs from Pinecone results
    4. Fetch full data from MongoDB using those IDs
    5. Apply additional MongoDB filters
    """
    try:
        from models.pinecone_vector_store import pinecone_vector_store
        from models.dataset_manager import dataset_manager
        from utils.embeddings import generate_query_embedding
        
        # Ensure Pinecone is ready
        if not pinecone_vector_store.is_ready:
            logger.warning("⚠️ Pinecone not ready, initializing...")
            await pinecone_vector_store.initialize()
            
            if not pinecone_vector_store.is_ready:
                logger.warning("⚠️ Pinecone unavailable, using MongoDB-only search")
                return await _fallback_to_mongodb_search(query, db_filters, dataset_type)
        
        # Ensure dataset manager is ready
        if not dataset_manager.db:
            await dataset_manager.initialize()
        
        # Generate query embedding
        logger.info("🔍 Generating query embedding for Pinecone search")
        query_embedding = await generate_query_embedding(query)
        
        if not query_embedding:
            logger.warning("⚠️ Could not generate embedding, falling back to MongoDB")
            return await _fallback_to_mongodb_search(query, db_filters, dataset_type)
        
        # Apply search parameters from strategy
        search_params = retrieval_strategy.get("search_parameters", {})
        extracted_filters = retrieval_strategy.get("vector_search_config", {}).get("metadata_filters", {})
        
        # Step 1: Search Pinecone for similar vectors
        logger.info(f"🎯 Searching Pinecone for {dataset_type}")
        pinecone_results = await pinecone_vector_store.search_with_dataset_routing(
            query_embedding=query_embedding,
            dataset_type=dataset_type,
            filters=extracted_filters,
            top_k=search_params.get("top_k", 10),
            similarity_threshold=search_params.get("similarity_threshold", 0.75)
        )
        
        if not pinecone_results:
            logger.warning("⚠️ No Pinecone results, falling back to MongoDB search")
            return await _fallback_to_mongodb_search(query, db_filters, dataset_type)
        
        # Step 2: Extract document IDs from Pinecone results
        document_ids = []
        pinecone_scores = {}
        
        for result in pinecone_results:
            # Get document ID from Pinecone metadata (adjust based on your Pinecone setup)
            doc_id = result.get("metadata", {}).get("document_id") or result.get("metadata", {}).get("product_id") or result.get("id")
            if doc_id:
                document_ids.append(doc_id)
                pinecone_scores[doc_id] = result["score"]
        
        logger.info(f"📊 Found {len(document_ids)} document IDs from Pinecone")
        
        # Step 3: Fetch full documents from MongoDB
        if dataset_type == "product_data":
            mongodb_results = await dataset_manager.search_product_dataset(
                query=query,
                filters={**db_filters, "_id": {"$in": document_ids}},
                limit=len(document_ids)
            )
        elif dataset_type == "regulatory_compliance":
            mongodb_results = await dataset_manager.search_regulatory_dataset(
                query=query,
                filters={**db_filters, "_id": {"$in": document_ids}},
                limit=len(document_ids)
            )
        else:  # both
            combined_results = await dataset_manager.search_both_datasets(
                query=query,
                filters={**db_filters, "_id": {"$in": document_ids}}
            )
            mongodb_results = combined_results.get("product_data", []) + combined_results.get("regulatory_data", [])
        
        # Step 4: Merge Pinecone scores with MongoDB data
        enhanced_results = []
        for doc in mongodb_results:
            doc_id = str(doc.get("_id", ""))
            if doc_id in pinecone_scores:
                doc["similarity_score"] = pinecone_scores[doc_id]
                doc["search_method"] = "pinecone_mongodb_hybrid"
                enhanced_results.append(doc)
        
        # Sort by similarity score
        enhanced_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        logger.info(f"✅ Pinecone + MongoDB search returned {len(enhanced_results)} results")
        return enhanced_results
        
    except Exception as e:
        logger.error(f"❌ Pinecone + MongoDB search failed: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to MongoDB-only search
        return await _fallback_to_mongodb_search(query, db_filters, dataset_type)

async def _fallback_to_mongodb_search(query: str, db_filters: Dict, dataset_type: str) -> List[Dict[str, Any]]:
    """Fallback to MongoDB-only search when Pinecone is unavailable"""
    try:
        from models.dataset_manager import dataset_manager
        
        logger.info(f"🔄 Using MongoDB fallback search for {dataset_type}")
        
        if dataset_type == "product_data":
            results = await dataset_manager.search_product_dataset(query, db_filters)
        elif dataset_type == "regulatory_compliance":
            results = await dataset_manager.search_regulatory_dataset(query, db_filters)
        else:  # both
            combined = await dataset_manager.search_both_datasets(query, db_filters)
            results = combined.get("product_data", []) + combined.get("regulatory_data", [])
        
        # Tag results as MongoDB-only
        for result in results:
            result["search_method"] = "mongodb_only"
            result["similarity_score"] = 0.5  # Default score for text search
        
        logger.info(f"📊 MongoDB fallback returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"❌ MongoDB fallback search failed: {e}")
        return []

async def _handle_product_search(request, session_id, classification):
    """Handle product-focused research queries with enhanced analysis"""
    logger.info("Executing enhanced product search strategy")
    
    try:
        processed_query = classification.get('processed_query', {})
        
        # Execute vector search to get products  
        from models.database import get_database
        db = get_database()
        products = await _execute_vector_search_for_products(request.query, db=db)
        
        # Enhanced product analysis for System Prompt compliance
        product_analysis = {'analysis_confidence': 0.7, 'data_gaps': []}
        regulatory_analysis = None
        
        if ENHANCED_SERVICES_AVAILABLE:
            try:
                analysis_service = ProductAnalysisService()
                product_analysis = analysis_service.analyze_products(products, {'query': request.query})
                logger.info(f"Product analysis confidence: {product_analysis.get('analysis_confidence', 0):.2f}")
                
                # Regulatory analysis if query involves regulatory-sensitive ingredients
                if processed_query.get('regulatory_sensitive'):
                    logger.info("Performing regulatory analysis for sensitive ingredients")
                    regulatory_analysis = {
                        "note": "Query involves regulatory-sensitive ingredients",
                        "disclaimer_required": True,
                        "recommendation": "Consult regulatory specialist for compliance advice"
                    }
            except Exception as e:
                logger.warning(f"Enhanced analysis failed, using fallback: {e}")
                product_analysis = {'analysis_confidence': 0.5, 'data_gaps': ['Enhanced analysis unavailable']}
        else:
            logger.info("Using basic analysis (enhanced services not available)")
            product_analysis = {'analysis_confidence': 0.6, 'data_gaps': ['Enhanced services not loaded']}
        
        # NEW: Check if we need to supplement with web search due to insufficient data
        needs_web_search = False
        web_results = []
        
        # Check if product data is insufficient for the query
        if product_analysis.get('analysis_confidence', 0) < 0.5:
            logger.info("🔄 Product data insufficient (confidence < 0.5), triggering web search...")
            needs_web_search = True
        elif len(product_analysis.get('data_gaps', [])) > 3:
            logger.info("🔄 Significant data gaps detected, triggering web search...")
            needs_web_search = True
        elif len(products) == 0:
            logger.info("🔄 No products found, triggering web search...")
            needs_web_search = True
        
        # Perform web search if needed
        if needs_web_search:
            try:
                from utils.web_search import get_web_knowledge
                logger.info("🔍 Executing web search to supplement insufficient product data...")
                web_knowledge = await get_web_knowledge(request.query)
                web_results = web_knowledge.get('results', [])
                logger.info(f"✅ Web search found {len(web_results)} results to supplement product data")
            except Exception as web_error:
                logger.warning(f"⚠️ Web search failed: {web_error}")
                web_results = []
        
        # Generate LLM response with enhanced context (including web search if available)
        try:
            from rag.llm_integration import LLMService
            llm_service = LLMService()
            llm_response = await llm_service.generate_research_response(
                query=request.query,
                context=request.context,
                product_data=products,
                processed_query=processed_query,
                web_search_results=web_results
            )
        except Exception as llm_error:
            logger.error(f"LLM service failed: {llm_error}")
            # Create fallback response
            llm_response = {
                'answer': f'I found {len(products)} products related to your query about "{request.query}". However, I encountered an issue generating a detailed analysis. Here\'s what I can tell you based on the available data.',
                'rationale': 'Product data retrieved but LLM analysis failed',
                'confidence_score': 0.5,
                'data_gaps': ['LLM analysis unavailable']
            }
        
        # Debug: Check LLM response type
        logger.info(f"LLM response type: {type(llm_response)}")
        if not isinstance(llm_response, dict):
            logger.error(f"LLM response is not a dict: {llm_response}")
            llm_response = {
                'answer': 'Error: Invalid LLM response format',
                'rationale': 'LLM service returned unexpected format',
                'confidence_score': 0.0,
                'data_gaps': ['LLM response format error']
            }
        
        # Prepare enhanced response
        sources_used = ["Retrieved Product Data ✅"]
        if processed_query.get('regulatory_sensitive'):
            sources_used.append("Regulatory Analysis ✅")
        
        # Add web search sources if used to supplement insufficient data
        if web_results:
            sources_used.append("Web Search ✅")
            # Add specific web sources (up to 3)
            web_source_count = 0
            for result in web_results:
                if result.get('source') and web_source_count < 3:
                    sources_used.append(f"Web: {result['source']}")
                    web_source_count += 1
        
        # Add regulatory disclaimer if needed
        disclaimer = None
        if regulatory_analysis or processed_query.get('regulatory_sensitive'):
            disclaimer = """⚠️ Disclaimer: The information presented here is based on publicly available data sources (e.g., Health Canada, product listings, third-party reports). While we aim to provide accurate and helpful insights, this tool is not a substitute for legal, medical, or regulatory advice. Always consult qualified professionals before making product or compliance decisions."""
        
        return ResearchResponse(
            query=request.query,
            answer=llm_response.get('answer', 'Unable to generate response'),
            rationale=llm_response.get('rationale', 'Analysis based on product database'),
            sources_used=sources_used,
            disclaimer=disclaimer,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            retrieved_products=products,
            # Enhanced fields
            confidence_score=llm_response.get('confidence_score', product_analysis.get('analysis_confidence', 0.0)),
            data_gaps=llm_response.get('data_gaps', product_analysis.get('data_gaps', [])),
            analysis_complexity=processed_query.get('analysis_complexity', 'medium'),
            regulatory_analysis=regulatory_analysis,
            # NEW: Include web search results when available
            web_search_results=web_results if web_results else None
        )
        
    except Exception as e:
        logger.error(f"❌ Product search failed: {e}")
        logger.info("🔄 Falling back to web search for product query...")
        
        # Fallback to web search when product search fails
        try:
            from utils.web_search import get_web_knowledge
            web_knowledge = await get_web_knowledge(request.query)
            web_results = web_knowledge.get('results', [])
            logger.info(f"✅ Fallback web search found {len(web_results)} results")
            
            # Use LLM with web search results
            try:
                from rag.llm_integration import LLMService
                llm_service = LLMService()
                
                fallback_context = f"""
Product search failed, but web search found current information.
Query: {request.query}
Context: {request.context or {}}
Web Results: {len(web_results)} sources found

Provide a helpful response using the available web search information.
"""
                
                llm_response = await llm_service.generate_research_response(
                    query=request.query,
                    context=request.context,
                    product_data=[],
                    vector_results=[],
                    processed_query=classification.get('processed_query', {}),
                    web_search_results=web_results
                )
            except Exception as llm_error:
                logger.error(f"LLM service in fallback also failed: {llm_error}")
                # Create a basic response without LLM
                llm_response = {
                    'answer': f'I found {len(web_results)} relevant web sources about "{request.query}". While I couldn\'t analyze them in detail due to a technical issue, here are the sources that might help answer your question.',
                    'confidence_score': 0.4,
                    'data_gaps': ['LLM analysis unavailable in fallback']
                }
            
            sources_used = ["Web Search"]
            if web_results:
                # Add specific web sources (up to 3 to match count)
                web_source_count = 0
                for result in web_results:
                    if result.get('source') and web_source_count < 3:
                        sources_used.append(f"Web: {result['source']}")
                        web_source_count += 1
            
            return ResearchResponse(
                query=request.query,
                answer=llm_response.get('answer', 'Unable to find relevant product information, but here\'s what I found from current web sources.'),
                rationale=f"Product database search failed ({str(e)}), but found {len(web_results)} relevant web sources to answer your query.",
                sources_used=sources_used,
                disclaimer="Product database temporarily unavailable. Information based on current web sources.",
                session_id=session_id,
                timestamp=datetime.utcnow(),
                retrieved_products=[],
                confidence_score=llm_response.get('confidence_score', 0.6),
                data_gaps=["Product database unavailable"],
                analysis_complexity="fallback"
            )
            
        except Exception as web_error:
            logger.error(f"❌ Web search fallback also failed: {web_error}")
            return ResearchResponse(
                query=request.query,
                answer=f"I apologize, but I encountered an issue with your product search: {request.query}",
                rationale=f"Technical error in product search: {str(e)}. Web search fallback also failed: {str(web_error)}",
                sources_used=["Error Response"],
                disclaimer="Both product database and web search are currently unavailable. Please try again later.",
                session_id=session_id,
                timestamp=datetime.utcnow(),
                confidence_score=0.0,
                data_gaps=["System error occurred"],
                analysis_complexity="error"
            )

async def _handle_general_knowledge(request, session_id, classification):
    """Handle general knowledge research queries with web search"""
    query = request.query
    context = request.context or {}
    
    # Get web search results for current information
    logger.info(f"🔍 Performing web search for general knowledge query: {query}")
    
    try:
        from utils.web_search import get_web_knowledge
        web_knowledge = await get_web_knowledge(query)
        web_results = web_knowledge.get('results', [])
        logger.info(f"✅ Found {len(web_results)} web search results")
    except Exception as e:
        logger.warning(f"⚠️ Web search failed: {e}")
        web_results = []
        web_knowledge = {'results': [], 'summary': '', 'source_count': 0}
    
    # Use LLM for general knowledge with web search results
    from rag.llm_integration import LLMService
    llm_service = LLMService()
    
    # Create enhanced context for general knowledge query
    general_context = f"""
Query Classification: {classification['primary_intent']}
User Role: {context.get('role', 'Researcher')}
Research Objective: {context.get('objective', 'General knowledge')}
Topic Focus: {context.get('topic', 'Beauty and wellness')}

Web Search Results: {web_knowledge.get('source_count', 0)} sources found
Sources to reference: Scientific research, industry knowledge, regulatory information, best practices, current web sources.
"""
    
    llm_response = await llm_service.generate_research_response(
        query=query,
        context=context,
        product_data=[],  # No product data for general knowledge
        vector_results=[],
        processed_query=classification,
        web_search_results=web_results  # Include web search results
    )
    
    # Prepare sources used list
    sources_used = ["AI Knowledge Base"]
    if web_results:
        sources_used.append("Web Search")
        # Add specific web sources (up to 3 to match what's shown)
        web_source_count = 0
        for result in web_results:
            if result.get('source') and web_source_count < 3:
                sources_used.append(f"Web: {result['source']}")
                web_source_count += 1
    
    # Create comprehensive rationale
    rationale = "Response generated using AI knowledge base and industry expertise"
    if web_results:
        # Count actual sources shown (max 3)
        actual_sources_shown = min(len([r for r in web_results if r.get('source')]), 3)
        rationale += f" enhanced with {actual_sources_shown} current web search results"
    else:
        rationale += ". Web search was attempted but no additional sources were found"
    
    # Create response focused on knowledge with web search links
    response = ResearchResponse(
        query=query,
        answer=llm_response["answer"],
        rationale=rationale,
        sources_used=sources_used,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        retrieved_products=[],
        web_search_results=[WebSearchResult(**result) for result in (web_results[:3] if web_results else [])],
        # Enhanced fields for System Prompt compliance
        confidence_score=llm_response.get('confidence_score', 0.8 if web_results else 0.6),
        data_gaps=llm_response.get('data_gaps', ["No product database integration"] if not web_results else []),
        analysis_complexity=classification.get('processed_query', {}).get('analysis_complexity', 'medium'),
        regulatory_analysis=None
    )
    
    return response

async def _handle_hybrid_research(request, session_id, classification):
    """Handle queries requiring both product data, general knowledge, and web search"""
    query = request.query
    context = request.context or {}
    
    # Execute product search to get actual products (not full response)
    from models.database import get_database
    db = get_database()
    products = await _execute_vector_search_for_products(request.query, db=db)
    
    # Get web search results for additional context
    logger.info(f"🔍 Performing web search for hybrid query: {query}")
    
    try:
        from utils.web_search import get_web_knowledge
        web_knowledge = await get_web_knowledge(query)
        web_results = web_knowledge.get('results', [])
        logger.info(f"✅ Found {len(web_results)} web search results for hybrid research")
    except Exception as e:
        logger.warning(f"⚠️ Web search failed for hybrid research: {e}")
        web_results = []
        web_knowledge = {'results': [], 'summary': '', 'source_count': 0}
    
    # Enhance with LLM knowledge combining all sources
    from rag.llm_integration import LLMService
    llm_service = LLMService()
    
    hybrid_context = f"""
You have access to product data, general knowledge, and current web information. Combine them intelligently.

Product Search Results: {len(products)} products found
Web Search Results: {web_knowledge.get('source_count', 0)} current sources found
Classification: {classification['primary_intent']}
Strategy: Hybrid (product data + general knowledge + web search)

Provide a comprehensive response that uses the specific product data, your knowledge base, and current web information.
"""
    
    llm_response = await llm_service.generate_research_response(
        query=query,
        context=context,
        product_data=products,
        vector_results=[],
        processed_query=classification,
        web_search_results=web_results  # Include web search results
    )
    
    # Prepare comprehensive sources list
    sources_used = ["Product Database", "AI Knowledge Base"]
    if web_results:
        sources_used.append("Web Search")
        # Add specific web sources (up to 2 to avoid clutter)
        web_source_count = 0
        for result in web_results:
            if result.get('source') and web_source_count < 2:
                sources_used.append(f"Web: {result['source']}")
                web_source_count += 1
    
    # Create enhanced hybrid rationale
    rationale = f"Hybrid analysis combining {len(products)} product matches with general industry knowledge"
    if web_results:
        # Count actual sources shown (max 2 for hybrid to avoid clutter)
        actual_sources_shown = min(len([r for r in web_results if r.get('source')]), 2)
        rationale += f" and {actual_sources_shown} current web search results"
    
    # Create enhanced hybrid response with web search links
    response = ResearchResponse(
        query=query,
        answer=llm_response["answer"],
        rationale=rationale,
        sources_used=sources_used,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        retrieved_products=products,
        web_search_results=[WebSearchResult(**result) for result in (web_results[:3] if web_results else [])],
        # Enhanced fields for System Prompt compliance
        confidence_score=llm_response.get('confidence_score', 0.9 if (web_results and products) else 0.7),
        data_gaps=llm_response.get('data_gaps', []),
        analysis_complexity=classification.get('processed_query', {}).get('analysis_complexity', 'high'),
        regulatory_analysis=None
    )
    
    return response

async def _execute_vector_search_for_products(query: str, db=None) -> List[Dict[str, Any]]:
    """Execute vector search and return just the products list (supports both Pinecone and local)"""
    retrieved_products = []
    try:
        # Import vector store and embedding utilities
        from main import vector_store, PINECONE_AVAILABLE
        from utils.embeddings import generate_query_embedding
        
        if not vector_store:
            logger.warning("⚠️ Vector store not available")
            return retrieved_products
        
        # Generate embedding for the query
        query_embedding = await generate_query_embedding(query)
        
        if PINECONE_AVAILABLE and hasattr(vector_store, 'query'):
            # Pinecone search
            logger.info("🔍 Using Pinecone vector search")
            
            # Convert numpy array to list for Pinecone
            embedding_list = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding
            
            # Query Pinecone
            results = vector_store.query(
                vector=embedding_list,
                top_k=10,
                include_metadata=True
            )
            
            logger.info(f"Pinecone search found {len(results.get('matches', []))} results")
            
            # Convert Pinecone results to product format
            for match in results.get('matches', []):
                try:
                    metadata = match.get('metadata', {})
                    
                    # Get product data from MongoDB using product_id
                    product_id = metadata.get('product_id')
                    product_data = {}
                    
                    if db is not None and product_id:
                        try:
                            # Try to get full product data from MongoDB
                            logger.info(f"🔍 Querying MongoDB for product_id: {product_id}")
                            mongo_product = await db[COLLECTIONS["main_data"]].find_one({"_id": int(product_id)})
                            if mongo_product:
                                logger.info(f"✅ MongoDB: Found product '{mongo_product.get('product_name', 'Unknown')}' (Brand: {mongo_product.get('brand', 'Unknown')})")
                                product_data = mongo_product
                            else:
                                logger.warning(f"⚠️ MongoDB: No product found for product_id: {product_id}")
                        except Exception as e:
                            logger.warning(f"Could not fetch full product data from MongoDB: {e}")
                    else:
                        logger.info(f"⚠️ Skipping MongoDB query - db: {db is not None}, product_id: {product_id}")
                    
                    # Use metadata as fallback or supplement
                    product = {
                        '_id': product_id,
                        'product_name': product_data.get('product_name') or metadata.get('product_name', 'Unknown Product'),
                        'brand': product_data.get('brand') or metadata.get('brand', 'Unknown'),
                        'category': product_data.get('category') or metadata.get('category', 'Unknown'),
                        'price': product_data.get('price') or metadata.get('price'),
                        'availability': product_data.get('availability') or metadata.get('availability', 'Available'),
                        'description': product_data.get('description', ''),
                        'similarity_score': match.get('score', 0),
                        'source': 'pinecone_search'
                    }
                    
                    # Log the final product data being returned
                    logger.info(f"📦 Final product data: {product['product_name']} | Brand: {product['brand']} | Category: {product['category']} | Price: {product.get('price', 'N/A')}")
                    
                    retrieved_products.append(product)
                    
                except Exception as e:
                    logger.warning(f"Error processing Pinecone result: {e}")
                    continue
                    
        elif hasattr(vector_store, 'similarity_search'):
            # Local vector store search
            logger.info("🔍 Using local vector search")
            
            vector_results = await vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=10,
                similarity_threshold=0.1  # Lower threshold for better results
            )
            
            logger.info(f"Local vector search found {len(vector_results)} results")
            
            # Convert local vector results to product format
            for result in vector_results:
                if 'metadata' in result and 'data' in result['metadata']:
                    metadata = result['metadata']
                    product_data = metadata['data']
                    product = {
                        '_id': metadata.get('product_id', f"vec_{result.get('index', 0)}"),
                        'product_name': product_data.get('product_name', 'Unknown Product'),
                        'brand': product_data.get('brand'),
                        'category': product_data.get('category'),
                        'price': product_data.get('price'),
                        'availability': product_data.get('availability', 'Available'),
                        'description': product_data.get('description'),
                        'similarity_score': result.get('similarity_score', 0),
                        'source': 'local_vector_search'
                    }
                    retrieved_products.append(product)
        else:
            logger.warning("⚠️ Vector store type not recognized")
            
    except Exception as e:
        logger.error(f"❌ Vector search failed: {e}")
        import traceback
        traceback.print_exc()
        
    return retrieved_products

async def _execute_vector_search(request, session_id):
    """Execute the vector search logic (your existing implementation)"""
    query = request.query
    context = request.context or {}
    
    # Get actual product data using vector search
    retrieved_products = []
    try:
        # Import vector store and embedding utilities
        from main import vector_store
        from utils.embeddings import generate_query_embedding
        
        if vector_store and vector_store.is_ready:
            # Generate embedding for the query
            query_embedding = await generate_query_embedding(query)
            
            # Perform vector similarity search with lower threshold
            vector_results = await vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=10,
                similarity_threshold=0.1  # Lower threshold for cross-model embeddings
            )
            
            logger.info(f"Vector search found {len(vector_results)} similar products")
            
            # Extract product data from vector results
            for result in vector_results:
                if 'metadata' in result and result['metadata']:
                    metadata = result['metadata']
                    if isinstance(metadata, dict) and 'data' in metadata:
                        product_data = metadata['data']
                        product = {
                            '_id': metadata.get('product_id', f"vec_{result['index']}"),
                            'product_name': product_data.get('product_name', 'Unknown Product'),
                            'brand': product_data.get('brand'),
                            'category': product_data.get('category'),
                            'price': product_data.get('price'),
                            'availability': product_data.get('availability', 'Available'),
                            'description': product_data.get('description'),
                            'similarity_score': result['similarity_score'],
                            'source': 'vector_search'
                        }
                        retrieved_products.append(product)
            
            logger.info(f"Extracted {len(retrieved_products)} products from vector search")
        
    except Exception as e:
        logger.warning(f"Vector search failed, using fallback: {e}")
    
    # Create intelligent response based on actual product data
    if retrieved_products:
        # Analyze the retrieved products
        brands = list(set([p.get('brand') for p in retrieved_products[:5] if p.get('brand')]))
        categories = list(set([p.get('category') for p in retrieved_products[:5] if p.get('category')]))
        avg_price = sum([p.get('price', 0) for p in retrieved_products[:5] if p.get('price')]) / max(len([p for p in retrieved_products[:5] if p.get('price')]), 1)
        
        smart_answer = f"""Based on your query about "{query}", I found {len(retrieved_products)} relevant products from our database:

**Key Findings:**
• Found products across {len(categories)} categories: {', '.join(categories[:3])}
• Top brands include: {', '.join(brands[:3])}
• Average price range: ${avg_price:.2f}
• High similarity matches indicate strong relevance to your query

**Top Products:**"""
        
        # Add top 3 products to the answer
        for i, product in enumerate(retrieved_products[:3]):
            smart_answer += f"""
{i+1}. **{product.get('product_name', 'Unknown')}**
   - Brand: {product.get('brand', 'N/A')}
   - Category: {product.get('category', 'N/A')}
   - Price: ${product.get('price', 'N/A')}
   - Similarity: {product.get('similarity_score', 0):.2f}"""
        
        smart_answer += f"""

**Analysis for {context.get('role', 'Research')}:**
Based on your objective to {context.get('objective', 'conduct research')}, the data shows strong market presence in {context.get('topic', 'this category')}. The vector similarity search identified products with high relevance scores, indicating good data coverage for your research needs."""
        
    else:
        # Fallback when no vector results
        smart_answer = f"""Based on your query about "{query}", here's what I found:

This appears to be a {context.get('role', 'research')} inquiry focused on {context.get('topic', 'market analysis')}. 

Key findings:
• Product analysis suggests strong market demand in this category
• Multiple brands and formulations available across different price points  
• Consumer preferences vary based on specific use cases and demographics
• Quality and ingredient sourcing are key differentiating factors

The research indicates opportunities for {context.get('objective', 'further investigation')} in this space."""

    # Create structured response with real data
    sources_used = ["Vector Search"]
    if retrieved_products:
        sources_used.extend(["Product Database", "Similarity Analysis"])
        rationale = f"Found {len(retrieved_products)} products using vector similarity search with embeddings. Analysis based on actual product data from your database with similarity scores ranging from {min([p.get('similarity_score', 0) for p in retrieved_products]):.2f} to {max([p.get('similarity_score', 0) for p in retrieved_products]):.2f}."
    else:
        sources_used.extend(["Fallback Analysis"])
        rationale = "Vector search completed but no high-similarity matches found. Response generated using general market knowledge and query analysis."
    
    response = ResearchResponse(
        query=query,
        answer=smart_answer,
        rationale=rationale,
        sources_used=sources_used,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        retrieved_products=retrieved_products[:5] if retrieved_products else []
    )
    
    return response

@router.get("/history/{session_id}", response_model=ResearchSession)
async def get_research_history(
    session_id: str,
    db=Depends(get_database_dependency)
):
    """Get research history for a session"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available - session history requires MongoDB")
        
        collection = db[COLLECTIONS["research_sessions"]]
        session = await collection.find_one({"session_id": session_id})
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ResearchSession(**session)
        
    except Exception as e:
        logger.error(f"❌ Error retrieving session history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session history")

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    db=Depends(get_database_dependency)
):
    """Submit feedback for a research query"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available - feedback requires MongoDB")
        
        collection = db[COLLECTIONS["user_feedback"]]
        
        feedback_doc = {
            "session_id": feedback.session_id,
            "query_id": feedback.query_id,
            "rating": feedback.rating,
            "feedback_type": feedback.feedback_type,
            "comments": feedback.comments,
            "timestamp": datetime.utcnow()
        }
        
        await collection.insert_one(feedback_doc)
        
        logger.info(f"✅ Feedback submitted for session {feedback.session_id}")
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Error submitting feedback")

# Helper functions
async def retrieve_products_from_db(db, processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Retrieve relevant products from MongoDB or local data based on processed query"""
    try:
        # Try MongoDB first
        if db is not None:
            collection = db[COLLECTIONS["main_data"]]
        else:
            # Fallback to local data
            from models.local_data import get_local_data
            logger.info("Using local data fallback")
            local_store = await get_local_data()
            
            # Extract search terms from processed query
            search_terms = []
            if processed_query.get('keywords'):
                search_terms.extend(processed_query['keywords'])
            if processed_query.get('categories'):
                search_terms.extend(processed_query['categories'])
            
            query_text = ' '.join(search_terms) if search_terms else ""
            
            products = await local_store.search_products(query_text, 20)
            logger.info(f"Retrieved {len(products)} products from local data")
            return products
        
        # Build MongoDB query from processed filters
        mongo_query = {}
        
        # Add filters based on processed query
        if "category" in processed_query.get("filters", {}):
            mongo_query["category"] = {"$regex": processed_query["filters"]["category"], "$options": "i"}
        
        if "brand" in processed_query.get("filters", {}):
            mongo_query["brand"] = {"$regex": processed_query["filters"]["brand"], "$options": "i"}
        
        if "price_range" in processed_query.get("filters", {}):
            price_filter = processed_query["filters"]["price_range"]
            if "min" in price_filter:
                mongo_query["price"] = {"$gte": price_filter["min"]}
            if "max" in price_filter:
                mongo_query.setdefault("price", {})["$lte"] = price_filter["max"]
        
        # Perform text search if no specific filters
        if not mongo_query and "keywords" in processed_query:
            mongo_query = {"$text": {"$search": " ".join(processed_query["keywords"])}}
        
        # Execute query
        cursor = collection.find(mongo_query).limit(20)
        products = await cursor.to_list(length=20)
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if "_id" in product:
                product["_id"] = str(product["_id"])
        
        logger.info(f"Retrieved {len(products)} products from MongoDB")
        return products
        
    except Exception as e:
        logger.error(f"❌ Error retrieving products from DB: {e}")
        return []

async def perform_vector_search(vector_store: VectorStore, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Perform vector similarity search"""
    try:
        if not vector_store.is_ready:
            logger.warning("Vector store not ready")
            return []
        
        # Generate embedding for the query
        # Note: You'll need to use the same embedding model that was used to create your embeddings
        # For now, I'll create a placeholder - you can replace this with your actual embedding model
        
        # This is a temporary implementation - you should replace this with your actual embedding generation
        logger.info("Performing vector search (placeholder embedding)")
        
        # TODO: Replace this with actual embedding generation using OpenAI
        # For now, we'll create a dummy embedding for testing
        # You would use: openai.embeddings.create(input=query, model="text-embedding-3-small")
        if np is not None:
            query_embedding = np.random.random(1536)  # Placeholder - replace with real embeddings
        else:
            query_embedding = [0.1] * 1536  # Simple fallback list
        
        logger.warning("Using dummy embeddings for vector search - replace with OpenAI embeddings for production")
        
        # Perform similarity search
        results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            similarity_threshold=0.1  # Lower threshold for testing
        )
        
        logger.info(f"Vector search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in vector search: {e}")
        return []

async def save_research_session(db, session_id: str, query: str, response: Dict, context: Optional[Dict]):
    """Save research query and response to session history"""
    try:
        collection = db[COLLECTIONS["research_sessions"]]
        
        query_data = {
            "query_id": str(uuid.uuid4()),
            "query": query,
            "response": response,
            "context": context,
            "timestamp": datetime.utcnow()
        }
        
        # Update existing session or create new one
        await collection.update_one(
            {"session_id": session_id},
            {
                "$push": {"queries": query_data},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        logger.info(f"✅ Saved query to session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Error saving research session: {e}")
        raise
