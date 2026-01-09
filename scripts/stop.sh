#!/bin/bash

# Sri Lanka Tourism Chatbot - Stop Script

set -e

echo "🛑 Stopping Sri Lanka Tourism Multilingual Chatbot..."

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

# Stop services gracefully
stop_services() {
    print_status "Stopping services gracefully..."
    
    if docker-compose ps --services --filter "status=running" | grep -q .; then
        docker-compose stop
        print_success "All services stopped"
    else
        print_warning "No running services found"
    fi
}

# Remove containers (optional)
remove_containers() {
    if [ "$1" = "--remove" ] || [ "$1" = "-r" ]; then
        print_status "Removing containers..."
        docker-compose down
        print_success "Containers removed"
    fi
}

# Remove volumes (optional)
remove_volumes() {
    if [ "$1" = "--volumes" ] || [ "$1" = "-v" ]; then
        print_status "Removing volumes (this will delete all data)..."
        read -p "Are you sure you want to remove all data? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            print_success "Volumes removed"
        else
            print_warning "Volume removal cancelled"
        fi
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --remove, -r    Remove containers after stopping"
    echo "  --volumes, -v   Remove volumes (WARNING: This deletes all data)"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Just stop services"
    echo "  $0 --remove     # Stop and remove containers"
    echo "  $0 --volumes    # Stop, remove containers and volumes"
}

# Main execution
main() {
    case "$1" in
        --help|-h)
            show_usage
            exit 0
            ;;
        --volumes|-v)
            remove_volumes "$1"
            ;;
        --remove|-r)
            remove_containers "$1"
            ;;
        "")
            stop_services
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    print_success "Stop operation completed! 🏁"
}

main "$@"
