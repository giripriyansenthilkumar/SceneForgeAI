#!/usr/bin/env bash
set -e

# ==============================================================================
# SceneForge AI - Local Stack Launcher
# Starts FastAPI Backend (8000), MCP Server (8001), and Vite Frontend (3000)
# ==============================================================================

BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "======================================================================"
echo "          SceneForge AI — Local Full-Stack Development Launcher        "
echo "======================================================================"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Ensure virtualenv exists
if [ ! -d "$ROOT_DIR/.venv" ]; then
    echo -e "${RED}[ERROR] Python virtual environment (.venv) not found.${NC}"
    echo "Creating virtualenv..."
    python3 -m venv "$ROOT_DIR/.venv"
    source "$ROOT_DIR/.venv/bin/activate"
    pip install -r "$ROOT_DIR/backend/requirements.txt"
    pip install -r "$ROOT_DIR/mcp-server/requirements.txt"
else
    source "$ROOT_DIR/.venv/bin/activate"
fi

export PYTHONPATH="$ROOT_DIR"
mkdir -p "$ROOT_DIR/storage/exports"
mkdir -p "$ROOT_DIR/storage/scenes"

# Trap exit signals to gracefully terminate child processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all services...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    echo -e "${GREEN}All SceneForge services stopped.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start MCP Tool Server on port 8001
echo -e "${CYAN}Starting MCP Tool Server on port 8001...${NC}"
python3 -m uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001 &
MCP_PID=$!

# 2. Start FastAPI Backend on port 8000
echo -e "${CYAN}Starting FastAPI Backend on port 8000...${NC}"
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 3. Start Vite Frontend on port 3000
echo -e "${CYAN}Starting React 18 / Three.js Frontend on port 3000...${NC}"
cd "$ROOT_DIR/frontend"
npm run dev -- --port 3000 &
FRONTEND_PID=$!

cd "$ROOT_DIR"

sleep 3
echo ""
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}          SceneForge AI Full Stack is Running Locally!                ${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo ""
echo -e "  🌐 ${BOLD}Interactive 3D Studio:${NC}  http://localhost:3000"
echo -e "  ⚙️  ${BOLD}FastAPI Backend API:${NC}     http://localhost:8000"
echo -e "  📖 ${BOLD}API Documentation:${NC}       http://localhost:8000/docs"
echo -e "  🛠️  ${BOLD}MCP Tool Server API:${NC}     http://localhost:8001"
echo ""
echo -e "${YELLOW}Press [CTRL+C] at any time to gracefully stop all services.${NC}"
echo ""

# Wait for background processes
wait
