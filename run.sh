#!/usr/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║        PuterAI Gateway — Startup Script              ║
# ║  Free OpenAI-compatible API via Puter.js             ║
# ╚══════════════════════════════════════════════════════╝
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colors ─────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

echo ""
echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║        PuterAI Gateway — Starting Up             ║${NC}"
echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo ""
          # Turn off automatic exporting

# ── Check Python ──────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install it first.${NC}"
    exit 1
fi
PYTHON=$(command -v python3)
echo -e "${GREEN}✅ Python: $($PYTHON --version)${NC}"

# ── Install dependencies ───────────────────────────────
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
$PYTHON -m pip install -q -r requirements.txt --break-system-packages
echo -e "${GREEN}✅ Dependencies ready${NC}"

# ── Kill old process on port 8000 ─────────────────────
if lsof -Pi :8000 -sTCP:LISTEN -t &>/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000 in use — stopping old process...${NC}"
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 1
fi

if [ -f .env ]; then
    set -a            # Turn on automatic exporting
    source .env       # Read the file
    set +a            # Turn off automatic exporting
else
    echo "Warning: .env file not found"
fi

# ── Start server ───────────────────────────────────────
echo -e "${CYAN}🚀 Starting server on http://$HOST_IP:$HOST_PORT ...${NC}"
$PYTHON server.py &
SERVER_PID=$!
sleep 2

# Verify server started
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${RED}❌ Server failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server running (PID $SERVER_PID)${NC}"

# ── Open browser ───────────────────────────────────────
BRIDGE_URL="http://${HOST_IP}:${HOST_PORT}/bridge"
CHAT_URL="http://${HOST_IP}:${HOST_PORT}/chat"

echo ""
echo -e "${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  STEP 1: Open the Bridge (keep this tab open!)${NC}"
echo -e "  ${BLUE}${BRIDGE_URL}${NC}"
echo ""
echo -e "${BOLD}  STEP 2: Use the Chatbot UI${NC}"
echo -e "  ${BLUE}${CHAT_URL}${NC}"
echo ""
echo -e "${BOLD}  STEP 3: Use in Python${NC}"
echo -e "  ${CYAN}from openai import OpenAI${NC}"
echo -e "  ${CYAN}client = OpenAI(base_url='http://${HOST_IP}:${HOST_PORT}/v1', api_key='no-key')${NC}"
echo -e "  ${CYAN}r = client.chat.completions.create(${NC}"
echo -e "  ${CYAN}    model='claude-opus-4-7',${NC}"
echo -e "  ${CYAN}    messages=[{'role':'user','content':'Hello!'}]${NC}"
echo -e "  ${CYAN})${NC}"
echo ""
echo -e "${BOLD}  Test API: ${YELLOW}python test_api.py${NC}"
echo -e "${BOLD}══════════════════════════════════════════════════${NC}"

# ── Auto-open browser if possible ─────────────────────
OPEN_CMD=""
if command -v xdg-open &>/dev/null; then OPEN_CMD="xdg-open"
elif command -v open &>/dev/null;    then OPEN_CMD="open"
elif command -v start &>/dev/null;   then OPEN_CMD="start"
fi

if [ -n "$OPEN_CMD" ]; then
    echo -e "${GREEN}🌐 Opening bridge in browser...${NC}"
    $OPEN_CMD "$BRIDGE_URL" 2>/dev/null || true
    sleep 1
    $OPEN_CMD "$CHAT_URL"   2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  Manually open these URLs in your browser:${NC}"
    echo -e "   Bridge: ${BRIDGE_URL}"
    echo -e "   Chat:   ${CHAT_URL}"
fi

echo ""
echo -e "${GREEN}✅ Everything running! Press Ctrl+C to stop.${NC}"
echo ""

# ── Trap Ctrl+C ────────────────────────────────────────
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Stopped. Goodbye!${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Keep alive ─────────────────────────────────────────
wait $SERVER_PID
