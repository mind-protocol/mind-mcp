FROM python:3.11-slim-bookworm

# System dependencies: Node.js 22 (for Claude CLI), ffmpeg (voice), gcc (native deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    gnupg \
    gcc \
    libffi-dev \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI — citizens invoke this for full tool/MCP/repo access
RUN npm install -g @anthropic-ai/claude-code@latest && \
    which claude && claude --version

ENV PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# App user
RUN useradd -m -u 1000 -s /bin/bash mind

WORKDIR /app

# Python dependencies (cached layer)
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]" uvicorn python-dotenv

# Application code
COPY --chown=mind:mind . /app/

# Persistent data directory structure
RUN mkdir -p /data/shrine/state \
    /data/.claude-accounts/a/.claude \
    /data/.claude-accounts/b/.claude \
    /data/.claude-accounts/c/.claude \
    /data/.claude-config \
    /data/.claude \
    /app/logs \
    && chown -R mind:mind /data /app

# Entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER mind

EXPOSE 8765

ENTRYPOINT ["/entrypoint.sh"]
