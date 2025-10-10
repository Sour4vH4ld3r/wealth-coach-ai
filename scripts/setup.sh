#!/bin/bash
set -e

echo "=========================================="
echo "Wealth Coach AI Assistant - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo -e "${RED}Please do not run this script as root${NC}"
   exit 1
fi

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION >= 3.11" | bc)" -eq 1 ]; then
        success "Python $PYTHON_VERSION found"
    else
        error "Python 3.11+ required (found $PYTHON_VERSION)"
        exit 1
    fi
else
    error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    success "Docker found"
else
    warning "Docker not found. Install Docker for containerized deployment"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    success "Docker Compose found"
else
    warning "Docker Compose not found. Install for multi-container deployment"
fi

echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    success ".env file created"
    warning "Please edit .env with your configuration (especially OPENAI_API_KEY)"
else
    success ".env file already exists"
fi

echo ""

# Ask user for setup type
echo "Choose setup type:"
echo "1) Development (local Python virtual environment)"
echo "2) Production (Docker containers)"
read -p "Enter choice [1-2]: " setup_choice

case $setup_choice in
    1)
        echo ""
        echo "Setting up DEVELOPMENT environment..."
        echo ""

        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating Python virtual environment..."
            python3 -m venv venv
            success "Virtual environment created"
        else
            success "Virtual environment already exists"
        fi

        # Activate virtual environment
        source venv/bin/activate

        # Upgrade pip
        echo "Upgrading pip..."
        pip install --upgrade pip > /dev/null 2>&1
        success "pip upgraded"

        # Install dependencies
        echo "Installing Python dependencies (this may take a few minutes)..."
        pip install -r requirements.txt > /dev/null 2>&1
        success "Dependencies installed"

        # Create necessary directories
        mkdir -p data/vector_store data/cache logs
        success "Data directories created"

        # Start Docker services (Redis and ChromaDB)
        echo ""
        echo "Starting supporting services (Redis, ChromaDB)..."
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d redis chromadb
            success "Redis and ChromaDB started"
        else
            warning "Docker Compose not available. You'll need to run Redis and ChromaDB manually"
        fi

        echo ""
        success "Development setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Edit .env with your OpenAI API key"
        echo "2. Activate virtual environment: source venv/bin/activate"
        echo "3. Load knowledge base: python scripts/load_knowledge.py"
        echo "4. Start server: cd backend && uvicorn main:app --reload"
        echo "5. Visit http://localhost:8000/docs for API documentation"
        ;;

    2)
        echo ""
        echo "Setting up PRODUCTION environment..."
        echo ""

        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            error "Docker is required for production setup"
            exit 1
        fi

        # Create necessary directories
        mkdir -p data/vector_store data/cache logs config
        success "Data directories created"

        # Build Docker images
        echo "Building Docker images..."
        docker-compose build
        success "Docker images built"

        # Start all services
        echo "Starting all services..."
        docker-compose up -d
        success "All services started"

        # Wait for services to be ready
        echo "Waiting for services to be healthy..."
        sleep 10

        # Check health
        if curl -s http://localhost:8000/health > /dev/null; then
            success "Backend API is healthy"
        else
            warning "Backend API health check failed. Check logs: docker-compose logs backend"
        fi

        echo ""
        success "Production setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Edit .env with your production configuration"
        echo "2. Load knowledge base: docker-compose exec backend python scripts/load_knowledge.py"
        echo "3. Visit http://localhost:8000/docs for API documentation"
        echo "4. Monitor logs: docker-compose logs -f"
        echo "5. For SSL/HTTPS, configure nginx and enable the production profile"
        ;;

    *)
        error "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Setup complete! 🚀"
echo "=========================================="
