#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Frontend Tests
run_frontend_tests() {
    print_header "Running Frontend Tests"
    
    if [ ! -d "src/frontend" ]; then
        print_error "Frontend directory not found"
        return 1
    fi
    
    cd src/frontend
    
    print_info "Installing dependencies..."
    npm install
    
    print_info "Running linting..."
    npm run lint
    
    print_info "Running type checking..."
    npm run type-check
    
    print_info "Running unit tests..."
    npm test
    
    print_info "Building application..."
    npm run build
    
    cd ../..
    print_success "Frontend tests completed"
}

# Backend Tests
run_backend_tests() {
    print_header "Running Backend Tests"
    
    if [ ! -d "src/backend" ]; then
        print_error "Backend directory not found"
        return 1
    fi
    
    cd src/backend
    
    print_info "Installing dependencies..."
    pip install -r requirements.txt
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    print_info "Running linting (flake8)..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    print_info "Checking code formatting (black)..."
    black --check .
    
    print_info "Running type checking (mypy)..."
    mypy .
    
    print_info "Running unit tests (pytest)..."
    pytest
    
    cd ../..
    print_success "Backend tests completed"
}

# Main execution
main() {
    echo "🧪 Running Local Tests for Navo"
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Run tests
    run_frontend_tests
    run_backend_tests
    
    echo ""
    print_header "🎉 All Tests Completed!"
    echo ""
    print_info "Next steps:"
    echo "1. Start backend: cd src/backend && uvicorn main:app --reload"
    echo "2. Start frontend: cd src/frontend && npm run dev"
    echo "3. Run E2E tests: cd src/frontend && npx playwright test"
    echo ""
    print_info "When ready for deployment:"
    echo "1. Uncomment .github/workflows/ci.yml"
    echo "2. Set up your deployment platform"
    echo "3. Configure GitHub secrets"
}

# Error handling
trap 'echo -e "\n${RED}Test failed at line $LINENO${NC}"; exit 1' ERR

# Run main function
main "$@"
