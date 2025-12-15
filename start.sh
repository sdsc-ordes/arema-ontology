#!/bin/bash

# AREMA Ontology Service - Quick Start Script

set -e

echo "🚀 Starting AREMA Ontology Manager"
echo "=================================="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Determine docker compose command (new vs old)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ docker compose not available. Please install Docker Compose."
    exit 1
fi

# Check for .env file, create from template if missing
if [ ! -f .env ]; then
    if [ -f .env.dist ]; then
        echo "📝 Creating .env from .env.dist..."
        cp .env.dist .env
        echo "⚠️  Created .env file. IMPORTANT: Edit .env and set FUSEKI_USERNAME and FUSEKI_PASSWORD before continuing!"
        echo "Press Enter after you've set the credentials, or Ctrl+C to exit..."
        read
    else
        echo "❌ No .env file found and no .env.dist template available."
        echo "Please create a .env file with FUSEKI_USERNAME and FUSEKI_PASSWORD."
        exit 1
    fi
fi

# Verify required env vars are set
if ! grep -q "FUSEKI_PASSWORD=." .env 2>/dev/null || ! grep -q "FUSEKI_USERNAME=." .env 2>/dev/null; then
    echo "❌ FUSEKI_USERNAME or FUSEKI_PASSWORD not set in .env file."
    echo "Please edit .env and set both variables."
    exit 1
fi

# Start services
echo ""
echo "🐳 Starting Docker containers..."
$DOCKER_COMPOSE up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check health
echo ""
echo "🏥 Checking service health..."
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ AREMA Ontology Service is healthy"
else
    echo "⚠️  Service may still be starting up..."
fi

if curl -sf http://localhost:3030/$/ping > /dev/null 2>&1; then
    echo "✅ Fuseki is healthy"
else
    echo "⚠️  Fuseki may still be starting up..."
fi

# Show status
echo ""
echo "📊 Service Status:"
echo "=================="
$DOCKER_COMPOSE ps

echo ""
echo "✨ Services are running!"
echo ""
echo "📍 Access points:"
echo "   - API Service:     http://localhost:8000"
echo "   - API Docs:        http://localhost:8000/docs"
echo "   - Fuseki UI:       http://localhost:3030"
echo ""
echo "🔧 Quick commands:"
echo "   - View logs:       $DOCKER_COMPOSE logs -f"
echo "   - Stop services:   $DOCKER_COMPOSE down"
echo "   - Restart:         $DOCKER_COMPOSE restart"
echo ""
echo "📚 Trigger an update:"
echo "   curl -X PUT http://localhost:8000/update \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"mock_mode\": false}'"
echo ""
