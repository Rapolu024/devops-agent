#!/bin/bash

# DevOps Agentic AI - Docker Run Script
# This script helps you run the DevOps agent in different modes using Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data temp monitoring
    
    # Set proper permissions
    chmod 755 logs data temp
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual credentials before running the agent."
        return 1
    fi
    return 0
}

# Build Docker image
build_image() {
    print_status "Building DevOps Agent Docker image..."
    docker build -t devops-agent:latest .
    print_status "Docker image built successfully!"
}

# Run status check
run_status() {
    print_header "Running DevOps Agent Status Check"
    docker run --rm \
        -v "$(pwd)/logs:/app/logs" \
        devops-agent:latest python run.py --status
}

# Run in interactive mode
run_interactive() {
    print_header "Running DevOps Agent in Interactive Mode"
    
    if ! setup_env; then
        print_error "Please configure .env file first"
        exit 1
    fi
    
    docker run -it --rm \
        --env-file .env \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/temp:/app/temp" \
        -v "/var/run/docker.sock:/var/run/docker.sock" \
        -v "$HOME/.aws:/home/devopsagent/.aws:ro" \
        -v "$HOME/.config/gcloud:/home/devopsagent/.config/gcloud:ro" \
        -v "$HOME/.azure:/home/devopsagent/.azure:ro" \
        -p 8080:8080 \
        devops-agent:latest python run.py
}

# Run in batch mode
run_batch() {
    local repo_url=$1
    
    if [ -z "$repo_url" ]; then
        print_error "Repository URL is required for batch mode"
        echo "Usage: $0 batch <repository_url>"
        exit 1
    fi
    
    print_header "Running DevOps Agent in Batch Mode"
    print_status "Repository: $repo_url"
    
    if ! setup_env; then
        print_error "Please configure .env file first"
        exit 1
    fi
    
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/logs:/app/logs" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/temp:/app/temp" \
        -v "/var/run/docker.sock:/var/run/docker.sock" \
        -v "$HOME/.aws:/home/devopsagent/.aws:ro" \
        -v "$HOME/.config/gcloud:/home/devopsagent/.config/gcloud:ro" \
        -v "$HOME/.azure:/home/devopsagent/.azure:ro" \
        devops-agent:latest python run.py "$repo_url"
}

# Run with full stack (docker-compose)
run_stack() {
    print_header "Running DevOps Agent with Full Stack"
    
    if ! setup_env; then
        print_error "Please configure .env file first"
        exit 1
    fi
    
    print_status "Starting all services with docker-compose..."
    docker-compose up -d
    
    print_status "Services started! Access points:"
    echo "  - DevOps Agent: http://localhost:8080"
    echo "  - Grafana: http://localhost:3000 (admin/admin123)"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    
    print_status "To view logs: docker-compose logs -f devops-agent"
    print_status "To stop: docker-compose down"
}

# Stop the stack
stop_stack() {
    print_header "Stopping DevOps Agent Stack"
    docker-compose down
    print_status "All services stopped."
}

# View logs
view_logs() {
    local service=${1:-devops-agent}
    print_header "Viewing logs for $service"
    docker-compose logs -f "$service"
}

# Clean up
cleanup() {
    print_header "Cleaning up Docker resources"
    
    # Stop and remove containers
    docker-compose down -v
    
    # Remove the image
    docker rmi devops-agent:latest 2>/dev/null || true
    
    # Remove unused volumes
    docker volume prune -f
    
    print_status "Cleanup completed!"
}

# Show usage
show_usage() {
    echo "DevOps Agentic AI - Docker Run Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  build           Build Docker image"
    echo "  status          Run status check"
    echo "  interactive     Run in interactive mode"
    echo "  batch <url>     Run in batch mode with repository URL"
    echo "  stack           Run full stack with docker-compose"
    echo "  stop            Stop the full stack"
    echo "  logs [service]  View logs (default: devops-agent)"
    echo "  cleanup         Clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 status"
    echo "  $0 interactive"
    echo "  $0 batch https://github.com/user/repo"
    echo "  $0 stack"
    echo "  $0 logs devops-agent"
    echo "  $0 cleanup"
}

# Main execution
main() {
    check_docker
    create_directories
    
    local command=${1:-help}
    
    case $command in
        build)
            build_image
            ;;
        status)
            build_image
            run_status
            ;;
        interactive)
            build_image
            run_interactive
            ;;
        batch)
            build_image
            run_batch "$2"
            ;;
        stack)
            check_docker_compose
            build_image
            run_stack
            ;;
        stop)
            check_docker_compose
            stop_stack
            ;;
        logs)
            check_docker_compose
            view_logs "$2"
            ;;
        cleanup)
            check_docker_compose
            cleanup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
