#!/bin/bash

# Sri Lanka Tourism Chatbot - Startup Script

set -e

echo "🇱🇰 Starting Sri Lanka Tourism Multilingual Chatbot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p models
    mkdir -p docker/nginx/ssl
    
    print_success "Directories created"
}

# Copy environment file if it doesn't exist
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_warning "Created .env file from env.example. Please update it with your configurations."
        else
            print_error "env.example file not found. Please create a .env file manually."
            exit 1
        fi
    fi
    
    print_success "Environment setup completed"
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build images
    docker-compose build
    
    # Start services
    docker-compose up -d mongodb redis
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Start backend and Rasa services
    docker-compose up -d backend rasa rasa-actions
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Start nginx (optional)
    docker-compose up -d nginx
    
    print_success "All services started successfully"
}

# Setup database and seed data
setup_database() {
    print_status "Setting up database and seeding initial data..."
    
    # Wait for backend to be ready
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T backend python scripts/setup_database.py; then
            print_success "Database setup and seeding completed"
            break
        else
            print_warning "Attempt $attempt/$max_attempts failed. Retrying in 5 seconds..."
            sleep 5
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Database setup failed after $max_attempts attempts"
        exit 1
    fi
}

# Train Rasa model
train_rasa_model() {
    print_status "Training Rasa model..."
    
    if docker-compose exec -T rasa rasa train --config config.yml --domain domain.yml --data data/; then
        print_success "Rasa model training completed"
    else
        print_warning "Rasa model training failed, but continuing with startup"
    fi
}

# Show service status
show_status() {
    print_status "Checking service status..."
    
    docker-compose ps
    
    echo ""
    print_success "🎉 Sri Lanka Tourism Chatbot is now running!"
    echo ""
    echo "📊 Service URLs:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Backend API: http://localhost:8000"
    echo "   • Rasa Chatbot: http://localhost:5005"
    echo "   • MongoDB: mongodb://localhost:27017"
    echo "   • Redis: redis://localhost:6379"
    echo ""
    echo "🔐 Default Admin Credentials:"
    echo "   • Username: admin"
    echo "   • Password: admin123"
    echo "   • (Please change these in production!)"
    echo ""
    echo "📝 Logs:"
    echo "   • View logs: docker-compose logs -f [service_name]"
    echo "   • All logs: docker-compose logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   • docker-compose down"
    echo ""
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check backend health
    max_attempts=10
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Backend is healthy"
            break
        else
            print_warning "Backend health check attempt $attempt/$max_attempts failed. Retrying in 3 seconds..."
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
    
    # Check Rasa health
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5005/status &> /dev/null; then
            print_success "Rasa is healthy"
            break
        else
            print_warning "Rasa health check attempt $attempt/$max_attempts failed. Retrying in 3 seconds..."
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
}

# Main execution
main() {
    echo "================================================"
    echo "🇱🇰 Sri Lanka Tourism Multilingual Chatbot"
    echo "================================================"
    echo ""
    
    check_dependencies
    create_directories
    setup_environment
    start_services
    setup_database
    train_rasa_model
    health_check
    show_status
    
    print_success "Startup completed successfully! 🚀"
}

# Handle script interruption
trap 'echo ""; print_warning "Startup interrupted. Cleaning up..."; docker-compose down; exit 1' INT TERM

# Run main function
main "$@"
