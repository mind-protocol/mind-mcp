#!/bin/bash
set -e

echo "[entrypoint] Starting Mind Home container setup..."

DATA_DIR="/data"
APP_DIR="/app"

# ── 1. Persistent shrine/state ──────────────────────────────────────────
PERSIST_STATE="$DATA_DIR/shrine/state"
REPO_STATE="$APP_DIR/shrine/state"

mkdir -p "$PERSIST_STATE"

if [ -d "$REPO_STATE" ] && [ ! -f "$PERSIST_STATE/.initialized" ]; then
    echo "[entrypoint] First run: seeding persistent state from repo..."
    cp -rn "$REPO_STATE/." "$PERSIST_STATE/" 2>/dev/null || true
    touch "$PERSIST_STATE/.initialized"
fi

# Symlink repo state to persistent
mkdir -p "$(dirname "$REPO_STATE")"
rm -rf "$REPO_STATE"
ln -sf "$PERSIST_STATE" "$REPO_STATE"

# ── 2. Claude account credentials ───────────────────────────────────────
CLAUDE_SETTINGS="$DATA_DIR/.claude-config/settings.json"
mkdir -p "$DATA_DIR/.claude-config"

# Default Claude settings for cloud (dangerously-skip-permissions enabled)
if [ ! -f "$CLAUDE_SETTINGS" ]; then
    cat > "$CLAUDE_SETTINGS" << 'SETTINGS'
{
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)", "Glob(*)", "Grep(*)"],
    "deny": []
  }
}
SETTINGS
fi

for account in a b c; do
    ACCT_CLAUDE="$DATA_DIR/.claude-accounts/$account/.claude"
    mkdir -p "$ACCT_CLAUDE"

    # Link shared settings
    if [ ! -L "$ACCT_CLAUDE/settings.json" ]; then
        ln -sf "$CLAUDE_SETTINGS" "$ACCT_CLAUDE/settings.json"
    fi

    # Seed credentials from env var (CLAUDE_CREDS_A, CLAUDE_CREDS_B, CLAUDE_CREDS_C)
    UPPER=$(echo "$account" | tr '[:lower:]' '[:upper:]')
    ENV_VAR="CLAUDE_CREDS_${UPPER}"
    ENV_VALUE=$(printenv "$ENV_VAR" 2>/dev/null || true)
    if [ -n "$ENV_VALUE" ]; then
        echo "$ENV_VALUE" > "$ACCT_CLAUDE/.credentials.json"
        echo "[entrypoint] Account $account: credentials SEEDED from $ENV_VAR"
    else
        echo "[entrypoint] Account $account: $([ -f "$ACCT_CLAUDE/.credentials.json" ] && echo 'present' || echo 'MISSING')"
    fi
done

# Main .claude dir for CLI
mkdir -p "$DATA_DIR/.claude"
if [ ! -L "$DATA_DIR/.claude/settings.json" ]; then
    ln -sf "$CLAUDE_SETTINGS" "$DATA_DIR/.claude/settings.json"
fi

# ── 3. Set environment ──────────────────────────────────────────────────
export HOME="$DATA_DIR"
export PORT="${PORT:-8765}"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
export PYTHONUNBUFFERED=1

# Verify claude is available
if command -v claude &>/dev/null; then
    echo "[entrypoint] Claude Code: $(claude --version 2>/dev/null || echo 'installed')"
else
    echo "[entrypoint] WARNING: claude not found in PATH=$PATH"
fi

# ── 4. Generate .env from Render environment ────────────────────────────
ENV_FILE="$APP_DIR/.env"
echo "# Auto-generated from Render env vars at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ENV_FILE"
for var in ANTHROPIC_API_KEY OPENAI_API_KEY GEMINI_API_KEY ELEVENLABS_API_KEY \
    ELEVENLABS_VOICE_ID DISCORD_BOT_TOKEN TELEGRAM_BOT_TOKEN \
    WAHA_URL WAHA_API_KEY WAHA_SESSION \
    MIND_PUBLIC_URL HOME_ID CLOUD_MODE RENDER MAX_PARALLEL \
    DATABASE_BACKEND FALKORDB_HOST FALKORDB_PORT FALKORDB_GRAPH CITIZEN_GRAPH \
    EMBEDDING_PROVIDER OPENAI_EMBEDDING_MODEL SELECTED_MODEL \
    HELIUS_API_KEY STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET \
    RENDER_API_KEY ADMIN_API_KEY; do
    val=$(printenv "$var" 2>/dev/null || true)
    if [ -n "$val" ]; then
        echo "${var}=${val}" >> "$ENV_FILE"
    fi
done
echo "[entrypoint] Generated .env with $(grep -c '=' "$ENV_FILE") vars"

# ── 5. Patch .mcp.json paths for Render ─────────────────────────────────
MCP_JSON="$APP_DIR/.mcp.json"
if [ -f "$MCP_JSON" ]; then
    sed -i 's|/home/mind-protocol/[^"]*/\.mind/runtime|/app/.mind/runtime|g' "$MCP_JSON"
    sed -i 's|/home/mind-protocol/[^"]*/|/app/|g' "$MCP_JSON"
    echo "[entrypoint] Patched .mcp.json paths for Render"
fi

# ── 6. Create log directory ─────────────────────────────────────────────
mkdir -p "$APP_DIR/logs"

echo "[entrypoint] Setup complete. Starting uvicorn on port $PORT..."
exec python3 -m uvicorn home_server:app --host 0.0.0.0 --port "$PORT" --log-level info
