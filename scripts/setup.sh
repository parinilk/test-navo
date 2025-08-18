#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo "=================================="
}

# Check if required tools are installed
check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_success "Git is installed ($(git --version))"
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js is installed ($NODE_VERSION)"
        
        # Check if it's the right version
        if [[ $NODE_VERSION =~ v18\. ]] || [[ $NODE_VERSION =~ v19\. ]] || [[ $NODE_VERSION =~ v20\. ]]; then
            print_success "Node.js version is compatible"
        else
            print_warning "Node.js version should be 18+ for optimal compatibility"
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        print_success "npm is installed ($(npm --version))"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python is installed ($PYTHON_VERSION)"
        
        # Check if it's Python 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python version is compatible (3.11+)"
        else
            print_warning "Python 3.11+ is recommended for this project"
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        echo "Visit: https://www.python.org/"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip is installed ($(pip3 --version))"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
}

# Create environment file from template
setup_environment() {
    print_header "Setting up Environment Configuration"
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success "Created .env file from template"
        else
            print_error "env.example template not found"
            exit 1
        fi
        
        print_warning "IMPORTANT: Please update .env file with your API keys:"
        echo "  - OPENAI_API_KEY=your-openai-api-key"
        echo "  - PINECONE_API_KEY=your-pinecone-api-key"
        echo "  - SERPAPI_API_KEY=your-serpapi-key"
        echo "  - SUPABASE_URL=your-supabase-url"
        echo "  - SUPABASE_KEY=your-supabase-key"
        echo ""
        echo "Without these keys, the application will not function properly."
    else
        print_success ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Creating Project Directories"
    
    directories=(
        "src/frontend"
        "src/backend/api"
        "src/backend/scraping"
        "src/backend/rag"
        "src/backend/models"
        "src/shared"
        "tests/frontend"
        "tests/backend"
        "tests/integration"
        "docs/api"
        "scripts"
        "logs"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Initialize git repository if not already initialized
setup_git() {
    print_header "Setting up Git Repository"
    
    if [ ! -d ".git" ]; then
        git init
        print_success "Initialized Git repository"
        
        # Add initial commit
        if [ -f "README.md" ]; then
            git add README.md .gitignore env.example
            git commit -m "Initial commit: Add project documentation and configuration"
            print_success "Created initial commit"
        fi
    else
        print_success "Git repository already initialized"
    fi
    
    # Setup git hooks for code quality
    if [ ! -f ".git/hooks/pre-commit" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks for Navo..."

# Frontend checks
if [ -d "src/frontend" ] && [ -f "src/frontend/package.json" ]; then
    echo "Checking frontend code..."
    cd src/frontend
    npm run lint
    npm run type-check
    cd ../..
fi

# Backend checks
if [ -d "src/backend" ] && [ -f "src/backend/requirements.txt" ]; then
    echo "Checking backend code..."
    cd src/backend
    python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    python -m black --check .
    cd ../..
fi

echo "Pre-commit checks completed ✓"
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Created pre-commit git hook for code quality"
    fi
}

# Install local dependencies
install_dependencies() {
    print_header "Installing Local Dependencies"
    
    # Frontend dependencies
    if [ -f "src/frontend/package.json" ]; then
        print_info "Installing frontend dependencies..."
        cd src/frontend
        if npm install; then
            print_success "Frontend dependencies installed"
        else
            print_warning "Failed to install frontend dependencies"
        fi
        cd ../..
    else
        print_info "Frontend package.json not found, will need to be created"
    fi
    
    # Backend dependencies
    if [ -f "src/backend/requirements.txt" ]; then
        print_info "Installing backend dependencies..."
        if command -v python3 &> /dev/null; then
            python3 -m pip install --user -r src/backend/requirements.txt
            print_success "Backend dependencies installed"
            
            # Install development dependencies if available
            if [ -f "src/backend/requirements-dev.txt" ]; then
                python3 -m pip install --user -r src/backend/requirements-dev.txt
                print_success "Development dependencies installed"
            fi
        else
            print_warning "Python 3 not found, skipping backend dependencies"
        fi
    else
        print_info "Backend requirements.txt not found, will need to be created"
    fi
}

# Setup database connection
setup_database() {
    print_header "Setting up Database Connection"
    
    print_info "For local development, you have several options:"
    echo ""
    echo "1. Use Supabase (Recommended):"
    echo "   - Go to https://supabase.com"
    echo "   - Create a new project"
    echo "   - Get your connection string and API keys"
    echo "   - Update your .env file"
    echo ""
    echo "2. Use Railway PostgreSQL:"
    echo "   - Go to https://railway.app"
    echo "   - Create a new PostgreSQL database"
    echo "   - Get your connection string"
    echo "   - Update your .env file"
    echo ""
    echo "3. Use local PostgreSQL (Advanced):"
    echo "   - Install PostgreSQL locally"
    echo "   - Create a database named 'navo'"
    echo "   - Update DATABASE_URL in .env"
    echo ""
    
    print_warning "Make sure to update your .env file with the correct DATABASE_URL"
}

# Display final instructions
show_final_instructions() {
    echo ""
    print_header "🎉 Navo Setup Completed!"
    echo ""
    
    print_info "Next Steps:"
    echo "1. Configure your API keys in the .env file:"
    echo "   - OpenAI API key for GPT-4o and embeddings"
    echo "   - Pinecone API key for vector database"
    echo "   - SerpAPI key for Walmart product search"
    echo "   - Supabase credentials for authentication"
    echo ""
    echo "2. Set up your database:"
    echo "   - Choose from Supabase, Railway, or local PostgreSQL"
    echo "   - Update DATABASE_URL in your .env file"
    echo ""
    echo "3. Start the development environment:"
    echo "   # Terminal 1 - Frontend"
    echo "   cd src/frontend"
    echo "   npm run dev"
    echo ""
    echo "   # Terminal 2 - Backend"
    echo "   cd src/backend"
    echo "   uvicorn main:app --reload"
    echo ""
    echo "4. Access the services:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    
    print_info "Useful Commands:"
    echo "  cd src/frontend && npm run dev    # Start frontend dev server"
    echo "  cd src/backend && uvicorn main:app --reload  # Start backend dev server"
    echo "  cd src/frontend && npm test       # Run frontend tests"
    echo "  cd src/backend && pytest          # Run backend tests"
    echo ""
    
    print_info "Deployment Options:"
    echo "  - Frontend: Deploy to Vercel"
    echo "  - Backend: Deploy to Railway or Render"
    echo "  - Database: Use Supabase"
    echo "  - Cache: Use Redis Cloud or Upstash"
    echo ""
    
    print_info "Team Resources:"
    echo "  Figma: https://www.figma.com/design/yzvSVtbZ7YTqtWrngm5Bby/Navo"
    echo "  Tech Office Hours: Saturdays/Sundays 10 AM - 12 PM EST"
    echo ""
    
    if [ -f ".env" ] && grep -q "your-openai-api-key" .env; then
        print_warning "⚠️  Remember to update your .env file with real API keys!"
    fi
}

# Main execution
main() {
    echo "🚀 Setting up Navo - AI Research Assistant for Beauty & Wellness"
    echo "Target: 5-week development timeline"
    echo "Team: 8 developers across Frontend, Backend, RAG, and DevOps"
    echo ""
    
    check_dependencies
    create_directories
    setup_environment
    setup_git
    install_dependencies
    setup_database
    show_final_instructions
}

# Error handling
trap 'echo -e "\n${RED}Setup failed at line $LINENO${NC}"; exit 1' ERR

# Run main function
main "$@" 