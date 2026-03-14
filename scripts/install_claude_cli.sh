#!/bin/bash
# Install Claude Code CLI — called by mind init and at deploy time.
# Idempotent: skips if already installed and up to date.

set -e

echo "[claude-cli] Checking Claude Code CLI..."

# Detect platform
if command -v claude &>/dev/null; then
    version=$(claude --version 2>/dev/null || echo "unknown")
    echo "[claude-cli] Already installed: $version"

    # Update to latest
    if command -v npm &>/dev/null; then
        echo "[claude-cli] Updating to latest..."
        npm install -g @anthropic-ai/claude-code@latest 2>/dev/null || true
    fi
    exit 0
fi

echo "[claude-cli] Not found — installing..."

# Method 1: npm (preferred — works on Node.js services)
if command -v npm &>/dev/null; then
    echo "[claude-cli] Installing via npm..."
    npm install -g @anthropic-ai/claude-code@latest

    # Verify
    if command -v claude &>/dev/null; then
        echo "[claude-cli] Installed: $(claude --version)"
        exit 0
    fi

    # npm global bin might not be in PATH
    NPM_BIN=$(npm bin -g 2>/dev/null || echo "$HOME/.npm-global/bin")
    if [ -x "$NPM_BIN/claude" ]; then
        echo "[claude-cli] Installed at $NPM_BIN/claude — adding to PATH"
        echo "export PATH=\"$NPM_BIN:\$PATH\"" >> ~/.bashrc
        echo "export PATH=\"$NPM_BIN:\$PATH\"" >> ~/.profile
        export PATH="$NPM_BIN:$PATH"
        echo "[claude-cli] Installed: $(claude --version)"
        exit 0
    fi
fi

# Method 2: curl installer (fallback)
echo "[claude-cli] Trying curl installer..."
curl -fsSL https://claude.ai/install.sh | bash || true

# Add to PATH
for bindir in "$HOME/.local/bin" "$HOME/.claude/bin" "/usr/local/bin"; do
    if [ -x "$bindir/claude" ]; then
        echo "export PATH=\"$bindir:\$PATH\"" >> ~/.bashrc
        echo "export PATH=\"$bindir:\$PATH\"" >> ~/.profile
        export PATH="$bindir:$PATH"
        echo "[claude-cli] Installed at $bindir: $(claude --version)"
        exit 0
    fi
done

echo "[claude-cli] WARNING: Could not install Claude CLI"
echo "[claude-cli] Citizens will use degraded API fallback"
exit 0  # Non-fatal — degraded mode still works
