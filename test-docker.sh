#!/bin/bash

# Test script for Docker deployment
set -e

echo "🐳 Testing Data Generator Docker Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if docker-compose is available
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

print_status "Docker Compose is available: $COMPOSE_CMD"

# Build the application
echo ""
echo "🏗️  Building the application..."
$COMPOSE_CMD build

if [ $? -eq 0 ]; then
    print_status "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Start the application
echo ""
echo "🚀 Starting the application..."
$COMPOSE_CMD up -d

if [ $? -eq 0 ]; then
    print_status "Application started successfully"
else
    print_error "Failed to start application"
    exit 1
fi

# Wait for the application to be ready
echo ""
echo "⏳ Waiting for application to be ready..."
sleep 10

# Test the health endpoint
echo ""
echo "🔍 Testing health endpoint..."
if curl -f http://localhost:8000/ping > /dev/null 2>&1; then
    print_status "Health check passed"
else
    print_warning "Health check failed, but application might still be starting..."
fi

# Test the API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Test strategies endpoint
if curl -f http://localhost:8000/get_all_strategies > /dev/null 2>&1; then
    print_status "Strategies endpoint working"
else
    print_warning "Strategies endpoint not responding"
fi

# Test frontend
echo ""
echo "🌐 Testing frontend..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_warning "Frontend not accessible"
fi

# Show running containers
echo ""
echo "📊 Running containers:"
$COMPOSE_CMD ps

# Show logs
echo ""
echo "📝 Recent logs:"
$COMPOSE_CMD logs --tail=20

echo ""
echo "🎉 Docker deployment test completed!"
echo ""
echo "Access your application at:"
echo "  🌐 Web Interface: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  ❤️  Health Check: http://localhost:8000/ping"
echo ""
echo "To stop the application:"
echo "  $COMPOSE_CMD down"
echo ""
echo "To view logs:"
echo "  $COMPOSE_CMD logs -f" 