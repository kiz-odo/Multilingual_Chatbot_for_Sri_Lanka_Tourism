#!/bin/bash

# Sri Lanka Tourism Chatbot - Development Setup Script

set -e

echo "🔧 Setting up Sri Lanka Tourism Chatbot for Development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        major_version=$(echo $python_version | cut -d'.' -f1)
        minor_version=$(echo $python_version | cut -d'.' -f2)
        
        if [ "$major_version" -eq 3 ] && [ "$minor_version" -ge 9 ]; then
            print_success "Python $python_version found"
        else
            print_error "Python 3.9+ required. Found: $python_version"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment file..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Created .env file from env.example"
            print_warning "Please update .env file with your configurations"
        else
            print_error "env.example file not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Setup MongoDB (Docker)
setup_mongodb() {
    print_status "Setting up MongoDB for development..."
    
    if command -v docker &> /dev/null; then
        # Check if MongoDB container is already running
        if ! docker ps | grep -q tourism_mongodb; then
            print_status "Starting MongoDB container..."
            docker run -d \
                --name tourism_mongodb \
                -p 27017:27017 \
                -e MONGO_INITDB_ROOT_USERNAME=admin \
                -e MONGO_INITDB_ROOT_PASSWORD=password123 \
                -e MONGO_INITDB_DATABASE=sri_lanka_tourism_bot \
                -v mongodb_data:/data/db \
                mongo:6.0
            
            print_success "MongoDB container started"
            sleep 5
        else
            print_warning "MongoDB container already running"
        fi
    else
        print_warning "Docker not found. Please install MongoDB manually or use Docker"
    fi
}

# Setup Redis (Docker)
setup_redis() {
    print_status "Setting up Redis for development..."
    
    if command -v docker &> /dev/null; then
        if ! docker ps | grep -q tourism_redis; then
            print_status "Starting Redis container..."
            docker run -d \
                --name tourism_redis \
                -p 6379:6379 \
                redis:7-alpine
            
            print_success "Redis container started"
        else
            print_warning "Redis container already running"
        fi
    else
        print_warning "Docker not found. Please install Redis manually or use Docker"
    fi
}

# Install Rasa
setup_rasa() {
    print_status "Setting up Rasa..."
    
    # Install spaCy language model
    python -m spacy download en_core_web_md
    
    print_success "Rasa setup completed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p models
    mkdir -p backend/rasa/models
    
    print_success "Directories created"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Wait for MongoDB to be ready
    sleep 5
    
    # Run database setup
    if python scripts/setup_database.py; then
        print_success "Database initialized and seeded"
    else
        print_warning "Database initialization failed. You may need to run it manually later."
    fi
}

# Train Rasa model
train_rasa() {
    print_status "Training Rasa model..."
    
    cd backend/rasa
    if rasa train --config config.yml --domain domain.yml --data data/; then
        print_success "Rasa model trained successfully"
    else
        print_warning "Rasa training failed. You may need to train manually later."
    fi
    cd ../..
}

# Show development instructions
show_instructions() {
    print_success "🎉 Development setup completed!"
    echo ""
    echo "📝 Development Commands:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate     # Windows"
    echo ""
    echo "2. Start the backend server:"
    echo "   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "3. Start Rasa server:"
    echo "   cd backend/rasa"
    echo "   rasa run --enable-api --cors \"*\" --port 5005"
    echo ""
    echo "4. Start Rasa actions server (in another terminal):"
    echo "   cd backend/rasa"
    echo "   rasa run actions --port 5055"
    echo ""
    echo "📊 Development URLs:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Backend API: http://localhost:8000"
    echo "   • Rasa API: http://localhost:5005"
    echo "   • MongoDB: mongodb://localhost:27017"
    echo "   • Redis: redis://localhost:6379"
    echo ""
    echo "🔐 Default Admin Credentials:"
    echo "   • Username: admin"
    echo "   • Password: admin123"
    echo ""
    echo "🛠️ Useful Development Commands:"
    echo "   • Format code: black backend/"
    echo "   • Sort imports: isort backend/"
    echo "   • Run tests: pytest backend/tests/"
    echo "   • Train Rasa: cd backend/rasa && rasa train"
    echo ""
}

# Main execution
main() {
    echo "================================================"
    echo "🔧 Development Setup - Sri Lanka Tourism Bot"
    echo "================================================"
    echo ""
    
    check_python
    setup_venv
    install_dependencies
    setup_env
    create_directories
    setup_mongodb
    setup_redis
    setup_rasa
    init_database
    train_rasa
    show_instructions
    
    print_success "Development setup completed successfully! 🚀"
}

# Handle script interruption
trap 'echo ""; print_warning "Setup interrupted."; exit 1' INT TERM

# Run main function
main "$@"
