# Navo Backend

FastAPI backend for the Navo AI-powered research assistant.

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to backend directory
cd src/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `src/backend` directory:

```bash
cp env.example .env
```

Update the `.env` file with your actual values:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=Navo_data

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Local Vector Store Paths
EMBEDDINGS_PATH=./data/embeddings
INDEX_PATH=./data/index
```

### 3. Prepare Your Embeddings

Since you have embeddings locally, ensure they are in the correct format and location:

1. **Create the embeddings directory:**
   ```bash
   mkdir -p data/embeddings
   mkdir -p data/index
   ```

2. **Move your embeddings:**
   - Copy your embedding files to `data/embeddings/`
   - Supported formats: `.pkl` (pickle), `.npy` (numpy)
   - Expected files:
     - `embeddings.pkl` or `embeddings.npy` (the actual embeddings)
     - `metadata.pkl` (optional, for product metadata/IDs)

### 4. Start the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### Research Endpoints
- `POST /api/v1/research/query` - Submit research questions
- `GET /api/v1/research/history/{session_id}` - Get conversation history
- `POST /api/v1/research/feedback` - Submit feedback

### Product Endpoints
- `GET /api/v1/products` - List products with filters
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/search` - Search products
- `GET /api/v1/products/categories/list` - List categories
- `GET /api/v1/products/brands/list` - List brands

### Analytics Endpoints
- `GET /api/v1/analytics/trends/{category}` - Category trends
- `POST /api/v1/analytics/competitive` - Competitive analysis
- `GET /api/v1/analytics/summary` - Market summary

## Architecture

```
src/backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── api/                   # API route handlers
│   ├── research.py        # Research query endpoints
│   ├── products.py        # Product data endpoints
│   └── analytics.py       # Analytics endpoints
├── models/                # Database and data models
│   ├── database.py        # MongoDB connection
│   └── vector_store.py    # Local embedding store
├── rag/                   # RAG pipeline components
│   ├── query_processor.py # Query processing and intent detection
│   └── llm_integration.py # OpenAI/LangChain integration
└── data/                  # Local data storage
    ├── embeddings/        # Your embedding files
    └── index/             # Search indices
```

## Database Collections

Based on your MongoDB Atlas setup, the backend expects these collections:

- `main_data` - Your main product data collection
- `research_sessions` - User research session history
- `user_feedback` - User feedback on responses
- `regulatory_compliance` - Regulatory data (if available)

## Embedding Integration

The backend is designed to work with your local embeddings. The `VectorStore` class will attempt to load embeddings from various formats:

1. **Pickle files**: `embeddings.pkl`, `product_embeddings.pkl`, `combined_embeddings.pkl`
2. **NumPy files**: `embeddings.npy`
3. **Metadata files**: `metadata.pkl`, `product_metadata.pkl`, `index_mapping.pkl`

### Expected Embedding Structure

The system expects embeddings in one of these formats:

```python
# Option 1: Dictionary with embeddings and metadata
{
    "embeddings": numpy_array,  # Shape: (n_products, embedding_dimension)
    "metadata": list_or_dict    # Product IDs or metadata
}

# Option 2: Just the numpy array
numpy_array  # Shape: (n_products, embedding_dimension)

# Option 3: Separate files
# embeddings.npy - the embeddings array
# metadata.pkl - the product metadata
```

## Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Research Query:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/research/query" \
        -H "Content-Type: application/json" \
        -d '{"query": "What are the best collagen supplements under $50?"}'
   ```

3. **List Products:**
   ```bash
   curl http://localhost:8000/api/v1/products?limit=5
   ```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error:**
   - Ensure MongoDB is running
   - Check MONGODB_URL in .env file
   - Verify database name matches your setup

2. **Embeddings Not Loading:**
   - Check file paths in EMBEDDINGS_PATH
   - Verify file formats (.pkl or .npy)
   - Check file permissions

3. **OpenAI API Error:**
   - Verify OPENAI_API_KEY is set correctly
   - Check API quota and billing

4. **Import Errors:**
   - Ensure all dependencies are installed
   - Activate virtual environment
   - Try: `pip install -r requirements.txt --upgrade`

### Logging

The application logs important events. Check the console output for:
- ✅ Success messages (green checkmarks)
- ❌ Error messages (red X marks)
- ⚠️ Warning messages (yellow warnings)

## Development

### Adding New Endpoints

1. Create new route in appropriate API file (`api/research.py`, etc.)
2. Add Pydantic models for request/response
3. Implement business logic
4. Test with FastAPI docs at `/docs`

### Modifying RAG Pipeline

1. Update `rag/query_processor.py` for query understanding
2. Modify `rag/llm_integration.py` for LLM prompts
3. Adjust `models/vector_store.py` for embedding search

### Database Changes

1. Update `models/database.py` for new collections
2. Add new aggregation pipelines as needed
3. Update API endpoints to use new data structures
