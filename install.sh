#!/usr/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║        PuterAI Gateway — Startup Script              ║
# ║  Free OpenAI-compatible API via Puter.js             ║
# ╚══════════════════════════════════════════════════════╝
set -e

# check Docker is installed
if ! command -v docker &>/dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

mkdir -p puter_ai_gateway
wget -q https://raw.githubusercontent.com/Mr-DS-ML-85/PuterAI-Gateway/main/.env -O puter_ai_gateway/.env
wget -q https://raw.githubusercontent.com/Mr-DS-ML-85/PuterAI-Gateway/main/docker-compose.yml -O puter_ai_gateway/docker-compose.yml
cd puter_ai_gateway
docker-compose up -d

if [ -f .env ]; then
    set -a            # Turn on automatic exporting
    source .env       # Read the file
    set +a  


echo -e "\n${GREEN}✅ PuterAI Gateway is now running!${NC}"
else
    echo "Warning: .env file not found"
fi
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
