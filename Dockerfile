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

# Python dependencies (install directly, no package build needed at runtime)
RUN pip install --no-cache-dir \
    falkordb>=1.0.0 neo4j>=5.0.0 numpy>=1.24.0 httpx>=0.24.0 \
    websockets>=11.0 pydantic>=2.0.0 pyyaml>=6.0 fastapi>=0.100.0 \
    uvicorn>=0.30.0 python-dotenv>=1.0.0 PyJWT>=2.8.0 bcrypt>=4.0.0

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
