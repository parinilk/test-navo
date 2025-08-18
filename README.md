# Navo: Understand products. Unlock markets.

## Overview
Navo is an AI-powered research assistant that helps beauty and wellness brands make smarter decisions by providing product-level data and insights. Our platform combines structured product data, semantic search, and LLM reasoning to deliver fast, context-rich answers across the entire product lifecycle.

**Market Opportunity**: $677B Global Beauty Market • $98B U.S. Beauty & Personal Care • $30B Global Indie Brands

## Technology Stack

### Frontend
- **Framework**: React 20+ with TypeScript
- **Styling**: Tailwind CSS, ShadCN UI
- **Build Tool**: Next.js
- **State Management**: Redux Toolkit
- **Testing**: Jest, React Testing Library

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **Cache**: Redis
- **API Documentation**: OpenAPI/Swagger
- **Testing**: Pytest

### AI & Data Pipeline(Hypothetically)
- **LLM Integration**: OpenAI GPT-4o via API
- **RAG Orchestration**: LangChain
- **Vector Search**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Data Scraping**: Playwright, ScraperAPI, SerpAPI

### Infrastructure
- **CI/CD**: GitHub Actions
- **Frontend Deployment**: Vercel
- **Backend Deployment**: Railway, Render, or AWS
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis Cloud or Upstash
- **Monitoring**: PostHog, Mixpanel

## Project Structure
```
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── frontend/        # React/Next.js application
│   ├── backend/         # FastAPI services
│   │   ├── api/         # API endpoints
│   │   ├── scraping/    # Data collection scripts
│   │   ├── rag/         # RAG pipeline and LLM integration
│   │   └── models/      # Database models
│   └── shared/          # Shared utilities
├── scripts/            # Development and deployment scripts
├── tests/              # Test suites
└── .github/            # GitHub workflows and templates
```

## Team Structure

### Leadership
- **Mentor**: Suganya
- **PMs**: Jessie Lee, Amber Cesair, Mohan K
- **Designers**: Lena Mitric, Jacob Ghil
- **Engineering Leads**: Sudhira Chegu, Parinil Kala

### Development Team
| Role | Primary | Secondary | Hours/week |
|------|---------|-----------|------------|
| **Engineering Lead - Backend & Data** | Sudhira Chegu (EST) | API, DB, Infra, RAG review | 21-40 |
| **LangChain + RAG Developer** | Hasnul Sanna (IST) | Embedding logic, backend validation | ~10 |
| **Scraping Lead** | Khushi Desai (CST) | SerpAPI, Playwright, data enrichment | 10-15 |
| **Frontend Support + Integration** | Vaishnav A. Bhujbal (CST) | QA, API integration | 15-20 |
| **QA Lead** | Zuhair Abdul Haleem (EST) | Test prompts, E2E testing | 15 |
| **DevOps Lead** | Parinil Kala (IST) | GitHub, CI/CD, PR review | 20-25 |
| **Backend + Vector DB** | Atharva Salpekar (IST) | Vector DB, embeddings | 5 |

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ (or use Supabase)
- Redis 7+ (or use Redis Cloud/Upstash)

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/your-org/navo.git
cd navo

# Run setup script
./scripts/setup.sh

# Start development environment
# Frontend
cd src/frontend
npm install
npm run dev

# Backend (in another terminal)
cd src/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Manual Setup
```bash
# Frontend setup
cd src/frontend
npm install
npm run dev

# Backend setup
cd src/backend
pip install -r requirements.txt
uvicorn main:app --reload

# Environment setup
cp env.example .env
# Update .env with your API keys and configuration
```

## Deployment Options

### Option 1: Vercel + Railway (Recommended for MVP)
- **Frontend**: Deploy to Vercel (automatic from GitHub)
- **Backend**: Deploy to Railway (Python FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis Cloud or Upstash

### Option 2: Vercel + Render
- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Render (Python service)
- **Database**: Supabase
- **Cache**: Redis Cloud

### Option 3: AWS/GCP/Azure
- **Frontend**: AWS S3 + CloudFront or GCP Cloud Storage
- **Backend**: AWS Lambda/ECS or GCP Cloud Run
- **Database**: AWS RDS or GCP Cloud SQL
- **Cache**: AWS ElastiCache or GCP Memorystore

### Option 4: DigitalOcean App Platform
- **Frontend**: DigitalOcean App Platform (Node.js)
- **Backend**: DigitalOcean App Platform (Python)
- **Database**: DigitalOcean Managed Databases
- **Cache**: DigitalOcean Managed Redis

## Development Workflow

### Data Pipeline
1. **Data Scraping**: Collect product data from Walmart using SerpAPI + Playwright
2. **Data Processing**: Clean and structure supplement facts, ingredients, pricing
3. **Embedding Generation**: Create vector embeddings for semantic search
4. **Vector Storage**: Store embeddings in Pinecone with metadata

### RAG Architecture
1. **Query Processing**: User submits natural language questions
2. **Semantic Search**: Retrieve relevant product data from Pinecone
3. **Context Assembly**: Combine retrieved data with query context
4. **LLM Generation**: Generate insights using GPT-4o via LangChain
5. **Response Delivery**: Return structured insights to frontend

### Development Phases (5-week timeline)

#### Week 1: Foundation
- [x] GitHub repo setup and CI/CD
- [x] Begin scraping target SKUs (SerpAPI + Playwright)
- [x] Define data model and Postgres schema
- [x] Start embedding pipeline + Pinecone test

#### Week 2: Core Development
- [x] Scraping refinement and enrichment logic
- [] LangChain prompt design + prototype retrieval chain
- [] Develop API endpoints with FastAPI
- [x] Build basic React UI layout

#### Week 3: Integration
- [ ] Integrate embedding + Pinecone with RAG chains
- [ ] Connect FastAPI backend to frontend UI
- [ ] Start user query testing and logging results
- [ ] Mid-point sync and adjustments

#### Week 4: Enhancement
- [ ] Improve prompt response quality and accuracy
- [ ] Polish UI and add metadata display
- [ ] Write and run integration tests
- [ ] Fix bugs from initial user testing

#### Week 5: Finalization
- [ ] Finalize MVP features
- [ ] Run end-to-end product demos
- [ ] Prepare documentation and video walkthrough
- [ ] Optional: feedback and logging features

## Data Sources & Schema

### Target Data Sources
| Phase | Channels | Region | Complexity |
|-------|----------|---------|------------|
| **MVP** | **Walmart** | US | 🔹 Low |
| **Post-MVP** | Shopee, Lazada | SEA/Taiwan | 🔸 Medium-High |
| **Phase 3** | Amazon, iHerb, brand sites | Global | 🔸 High |

### Core Data Fields
- **Product name, price, size/weight, brand**
- **Product type** (powder, capsule, gummy)
- **Supplement facts** (active ingredients, dosage)
- **Ingredients list**
- **Primary claims** ("supports joint health", "glowing skin")
- **Country of origin, packaging type**
- **Rating/review count**

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh

### Product Data
- `GET /api/v1/products` - List products with filters
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/search` - Semantic product search

### AI Research Assistant
- `POST /api/v1/chat/query` - Submit research questions
- `GET /api/v1/chat/history` - Get conversation history
- `POST /api/v1/chat/feedback` - Submit feedback on responses

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our development process, coding standards, and how to submit pull requests.

## Documentation
- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Data Sources & Schema](docs/data-schema.md)

## Team Communication
- **Technical Office Hours**: Every Saturday/Sunday, 10 AM - 12 PM EST
- **Standup**: Weekly 15-minute developer standup
- **Design Reviews**: PM-Designer collaboration sessions
- **Figma**: [Design System](https://www.figma.com/design/yzvSVtbZ7YTqtWrngm5Bby/Navo)

## License
[License information] 
