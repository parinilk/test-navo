# Enhanced RAG Architecture Implementation

This directory implements the complete **RAG Filters.md** architecture with Intent Router, Three-Tier Filters, and LLM Filter Extraction.

## Architecture Overview

```
User Query 
    ↓
Intent Router Node (Route to datasets: product vs regulatory)
    ↓  
Filter Extractor Node (LLM-based preprocessing)
    ↓
Retriever(s) Node (Enhanced vector search with filters)
    ↓
Answer Composer (Dataset-specific response generation)
```

## Core Components

### 1. Intent Router (`intent_router.py`)
Routes queries to appropriate datasets based on content analysis:
- **Product Data**: Pricing, comparisons, product features
- **Regulatory Compliance**: Safety, jurisdiction, ingredient compliance  
- **Both**: Complex queries needing multiple datasets

**Example:**
```python
routing = intent_router.route_query(
    "Is retinol allowed in Canadian skincare?",
    context={"role": "product_developer"}
)
# → Routes to REGULATORY_COMPLIANCE dataset
```

### 2. Three-Tier Filter System (`three_tier_filters.py`)
Implements hierarchical filter extraction:

#### **Tier 1: Product-Level Filters**
- Format (Powder, Capsule, Gummy, etc.)
- Primary Benefit (Skin Health, Joint Support, etc.)
- Price Range (Under $20, $20-$40, etc.)
- Brand, Sales Channel, Pack Size

#### **Tier 2: Ingredient-Level Filters** 
- Ingredient Name (Retinol, Collagen, Biotin, etc.)
- Ingredient Form (Marine, Bovine, Type I/II/III)
- Usage Context (Rinse-off, Leave-on, Ingestible)
- Jurisdiction (USA, Canada, EU, California)

#### **Tier 3: Claim/Positioning-Level Filters**
- Claim Category (Beauty, Anti-aging, Joint Health)
- Claim Format ("Supports...", "Clinically Tested")
- Target Demographic (Women, Men, Athletes, 40+)
- Lifestyle (Vegan, Keto, Organic)

**Example:**
```python
filters = three_tier_filter_extractor.extract_all_filters(
    "Best marine collagen gummies for women over 40"
)
# Returns: {
#   "tier_1_product": {"format": "gummy"},
#   "tier_2_ingredient": {"ingredient_form": "marine_collagen"},
#   "tier_3_claim": {"target_demographic": ["women", "40_plus"]}
# }
```

### 3. LLM Filter Extractor (`llm_filter_extractor.py`)
Uses LLM for intelligent filter preprocessing:

**Input:** `"What are the most affordable collagen powders for skin health?"`

**LLM Output:**
```json
{
  "format": "Powder",
  "primary_benefit": "Skin Health", 
  "price_range": "Under $20",
  "ingredient_name": ["collagen"]
}
```

### 4. Enhanced Query Processor (`enhanced_query_processor.py`)
Orchestrates the complete pipeline:
1. Intent routing to datasets
2. LLM filter extraction  
3. Retrieval strategy preparation
4. Quality assessment

## API Endpoints

### Enhanced Research Query
`POST /api/v1/research/query/enhanced`

Uses the complete RAG Filters architecture:

```json
{
  "query": "What are regulatory-safe retinol alternatives for Canadian skincare?",
  "context": {
    "role": "product_developer",
    "objective": "formulation_compliance"
  }
}
```

**Response includes:**
- Intent routing decision
- Extracted filters with confidence
- Dataset-specific analysis
- Quality assessment metrics

## Usage Examples

### 1. Product Search Query
```python
# Query: "Compare marine collagen powders under $30"
# → Routes to: PRODUCT_DATA
# → Filters: {"format": "Powder", "ingredient_form": "Marine Collagen", "price_range": "Under $30"}
# → Strategy: Enhanced vector search with price filtering
```

### 2. Regulatory Query  
```python
# Query: "Is retinol banned in EU cosmetics?"
# → Routes to: REGULATORY_COMPLIANCE
# → Filters: {"ingredient_name": ["retinol"], "jurisdiction": "EU", "usage_context": "Leave-On"}
# → Strategy: Regulatory database + web search for updates
```

### 3. Hybrid Query
```python
# Query: "Safe collagen ingredients for pregnancy supplements in Canada"
# → Routes to: BOTH datasets
# → Filters: {"ingredient_name": ["collagen"], "target_demographic": ["pregnant"], "jurisdiction": "Canada"}
# → Strategy: Combined product + regulatory analysis
```

## Configuration

### Enable LLM Filter Extraction
```python
# In main.py or initialization
from rag.enhanced_query_processor import enhanced_query_processor
from rag.llm_integration import LLMService

llm_service = LLMService()
enhanced_query_processor.llm_service = llm_service
```

### Dataset Collections
Ensure these MongoDB collections exist:
- `main_data` - Product data
- `regulatory_compliance` - Regulatory information  
- `product_embeddings` - Vector embeddings

## Quality Metrics

The system provides quality assessment:
- **Intent Routing Confidence**: How certain the routing decision is
- **Filter Extraction Confidence**: Quality of extracted filters
- **Overall Processing Score**: Combined quality metric
- **Recommendations**: Suggestions for improving results

## Web Search Integration

Lightweight web search triggers for:
- Recent regulatory updates (`"FDA recent"`, `"latest regulations"`)
- Low confidence queries needing external validation
- Regulatory queries requiring current information

## Fallback Behavior

- **LLM Unavailable**: Falls back to rule-based filter extraction
- **Vector Search Fails**: Uses traditional database queries
- **Dataset Not Found**: Routes to general knowledge base
- **Low Confidence**: Requests user clarification

## Monitoring & Debugging

Enable detailed logging:
```python
import logging
logging.getLogger('rag').setLevel(logging.INFO)
```

Pipeline timing and component performance included in responses for optimization.
