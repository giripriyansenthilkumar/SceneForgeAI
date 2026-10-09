#!/usr/bin/env bash
set -e

# ==============================================================================
# SceneForge AI - Full Docker Stack Deployment Script
# Orchestrates PostgreSQL, Redis, FastAPI Backend, MCP Tool Server & Three.js Studio
# ==============================================================================

BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "======================================================================"
echo "          SceneForge AI — Full Docker Stack Deployment               "
echo "======================================================================"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# 1. Verify Docker Engine availability
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] 'docker' command was not found on your system.${NC}"
    echo ""
    echo -e "${YELLOW}To install Docker on macOS:${NC}"
    echo -e "  Option A (Docker Desktop GUI):"
    echo -e "    ${BOLD}brew install --cask docker${NC}  (then open Docker from /Applications)"
    echo -e "  Option B (Colima CLI daemon - lightweight open-source):"
    echo -e "    ${BOLD}brew install colima docker docker-compose${NC}"
    echo -e "    ${BOLD}colima start --cpu 4 --memory 8${NC}"
    echo ""
    echo -e "${YELLOW}Alternatively, run the complete stack locally without Docker:${NC}"
    echo -e "    ${BOLD}./scripts/start_local_stack.sh${NC}"
    echo ""
    exit 1
fi

# 2. Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}[ERROR] Docker daemon is not responding.${NC}"
    echo -e "${YELLOW}Please ensure Docker Desktop is started or run:${NC}"
    echo -e "    ${BOLD}colima start${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker engine is running.${NC}"

# 3. Create required runtime storage directories
mkdir -p "$ROOT_DIR/storage/exports"
mkdir -p "$ROOT_DIR/storage/scenes"

# 4. Copy .env if not present
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

# 5. Build and launch containers
echo -e "${CYAN}Building and starting SceneForge AI containers...${NC}"
docker compose down --remove-orphans 2>/dev/null || true
docker compose up --build -d

echo ""
echo -e "${CYAN}Waiting for services to become healthy...${NC}"

# 6. Health probe loop
MAX_RETRIES=30
RETRY_COUNT=0
BACKEND_HEALTHY=0
MCP_HEALTHY=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))

    if [ $BACKEND_HEALTHY -eq 0 ]; then
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            BACKEND_HEALTHY=1
            echo -e "${GREEN}✓ FastAPI Backend is healthy on port 8000${NC}"
        fi
    fi

    if [ $MCP_HEALTHY -eq 0 ]; then
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            MCP_HEALTHY=1
            echo -e "${GREEN}✓ MCP Tool Server is healthy on port 8001${NC}"
        fi
    fi

    if [ $BACKEND_HEALTHY -eq 1 ] && [ $MCP_HEALTHY -eq 1 ]; then
        break
    fi
done

echo ""
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}          SceneForge AI Docker Stack Successfully Deployed!           ${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo ""
echo -e "  🌐 ${BOLD}Interactive 3D Studio:${NC}  http://localhost:3000"
echo -e "  ⚙️  ${BOLD}FastAPI Backend API:${NC}     http://localhost:8000"
echo -e "  📖 ${BOLD}Backend OpenAPI Docs:${NC}    http://localhost:8000/docs"
echo -e "  🛠️  ${BOLD}MCP Tool Server API:${NC}     http://localhost:8001"
echo -e "  🐘 ${BOLD}PostgreSQL Database:${NC}     localhost:5432 (sceneforge)"
echo -e "  ⚡ ${BOLD}Redis Cache/PubSub:${NC}      localhost:6379"
echo ""
echo -e "${CYAN}View live container logs:${NC}  docker compose logs -f"
echo -e "${CYAN}Tear down stack:${NC}           docker compose down"
echo ""
