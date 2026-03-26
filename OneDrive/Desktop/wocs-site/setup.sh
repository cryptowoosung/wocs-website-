#!/bin/bash
# ============================================
# WOCS 프로젝트 초기 설정 스크립트
# 새 컴퓨터에서 실행: bash setup.sh
# ============================================

set -e
echo "=== WOCS 프로젝트 설정 시작 ==="

# 1. npm 패키지 설치
echo ""
echo "[1/5] npm 패키지 설치..."
if [ -f package.json ]; then
    npm install
else
    echo "  package.json 없음 — 스킵"
fi

# 2. pip 패키지 설치
echo ""
echo "[2/5] Python 패키지 설치..."
pip install google-generativeai python-dotenv requests 2>/dev/null || echo "  pip 설치 실패 — 수동 설치 필요"

# 3. .env 파일 생성
echo ""
echo "[3/5] .env 파일 확인..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  .env.example → .env 복사 완료"
    echo "  ※ .env 파일을 열어서 API 키를 입력하세요"
else
    echo "  .env 이미 존재 — 스킵"
fi

# 4. Claude Code 스킬 설치
echo ""
echo "[4/5] Claude Code 스킬 설치..."

# Gemini (Google)
echo "  → Gemini 스킬..."
npx -y skills add google-gemini/gemini-skills --skill gemini-api-dev --global -y 2>/dev/null && echo "    ✓ gemini-api-dev" || echo "    ✗ gemini-api-dev"
npx -y skills add google-gemini/gemini-skills --skill vertex-ai-api-dev --global -y 2>/dev/null && echo "    ✓ vertex-ai-api-dev" || echo "    ✗ vertex-ai-api-dev"
npx -y skills add google-gemini/gemini-skills --skill gemini-live-api-dev --global -y 2>/dev/null && echo "    ✓ gemini-live-api-dev" || echo "    ✗ gemini-live-api-dev"
npx -y skills add google-gemini/gemini-skills --skill gemini-interactions-api --global -y 2>/dev/null && echo "    ✓ gemini-interactions-api" || echo "    ✗ gemini-interactions-api"

# Vercel
echo "  → Vercel 스킬..."
npx -y skills add vercel-labs/agent-skills --skill vercel-react-best-practices --global -y 2>/dev/null && echo "    ✓ vercel-react-best-practices" || echo "    ✗ vercel-react-best-practices"
npx -y skills add vercel-labs/agent-skills --skill web-design-guidelines --global -y 2>/dev/null && echo "    ✓ web-design-guidelines" || echo "    ✗ web-design-guidelines"
npx -y skills add vercel-labs/agent-skills --skill deploy-to-vercel --global -y 2>/dev/null && echo "    ✓ deploy-to-vercel" || echo "    ✗ deploy-to-vercel"

# OpenAI
echo "  → OpenAI 스킬..."
npx -y skills add openai/skills --skill imagegen --global -y 2>/dev/null && echo "    ✓ imagegen" || echo "    ✗ imagegen"
npx -y skills add openai/skills --skill doc --global -y 2>/dev/null && echo "    ✓ doc" || echo "    ✗ doc"
npx -y skills add openai/skills --skill gh-fix-ci --global -y 2>/dev/null && echo "    ✓ gh-fix-ci" || echo "    ✗ gh-fix-ci"
npx -y skills add openai/skills --skill netlify-deploy --global -y 2>/dev/null && echo "    ✓ netlify-deploy" || echo "    ✗ netlify-deploy"

# 커뮤니티 스킬 (git clone)
echo "  → 커뮤니티 스킬..."
SKILL_DIR="$HOME/.claude/skills"
mkdir -p "$SKILL_DIR"

[ ! -d "$SKILL_DIR/n8n-skills" ] && git clone https://github.com/czlonkowski/n8n-skills.git "$SKILL_DIR/n8n-skills" 2>/dev/null && echo "    ✓ n8n-skills" || echo "    · n8n-skills (이미 설치됨)"
[ ! -d "$SKILL_DIR/prompt-master" ] && git clone https://github.com/nidhinjs/prompt-master.git "$SKILL_DIR/prompt-master" 2>/dev/null && echo "    ✓ prompt-master" || echo "    · prompt-master (이미 설치됨)"
[ ! -d "$SKILL_DIR/claude-seo" ] && git clone https://github.com/AgriciDaniel/claude-seo.git "$SKILL_DIR/claude-seo" 2>/dev/null && echo "    ✓ claude-seo" || echo "    · claude-seo (이미 설치됨)"
[ ! -d "$SKILL_DIR/ai-marketing-skills" ] && git clone https://github.com/BrianRWagner/ai-marketing-skills.git "$SKILL_DIR/ai-marketing-skills" 2>/dev/null && echo "    ✓ ai-marketing-skills" || echo "    · ai-marketing-skills (이미 설치됨)"

# 5. n8n MCP 서버 등록
echo ""
echo "[5/5] n8n MCP 서버 등록..."
if [ -f .env ]; then
    N8N_MCP_TOKEN=$(grep '^N8N_MCP_TOKEN=' .env | cut -d'=' -f2-)
    if [ -n "$N8N_MCP_TOKEN" ]; then
        claude mcp add n8n-mcp "https://wocs.app.n8n.cloud/mcp-server/http" \
            -t http -s user \
            -H "Authorization: Bearer $N8N_MCP_TOKEN" 2>/dev/null \
            && echo "  ✓ n8n MCP 등록 완료" \
            || echo "  ✗ n8n MCP 등록 실패 — claude CLI 확인 필요"
    else
        echo "  ✗ .env에 N8N_MCP_TOKEN 값이 없음 — 입력 후 재실행"
    fi
else
    echo "  ✗ .env 파일 없음 — 먼저 .env 생성 필요"
fi

echo ""
echo "=== 설정 완료 ==="
echo ""
echo "다음 단계:"
echo "  1. .env 파일을 열어서 API 키 입력"
echo "  2. Claude Code 재시작하면 스킬 활성화"
echo ""
