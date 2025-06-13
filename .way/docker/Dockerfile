FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic development tools and utilities
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    wget \
    python3 \
    python3-pip \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add NodeSource repository and install Node.js 20.x
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Update npm to latest version
RUN npm install -g npm@latest

# Set working directory
WORKDIR /workspace

# Configure claude-code to store credentials in workspace
ENV CLAUDE_CODE_CONFIG_DIR=/workspace/.claude-code

# Ensure /usr/local/bin exists and has correct permissions
RUN mkdir -p /usr/local/bin && chmod 777 /usr/local/bin

# Create a non-root user
RUN useradd -m -s /bin/bash developer && \
    chown -R developer:developer /workspace

# Set default shell
SHELL ["/bin/bash", "-c"]

# Switch to non-root user
USER developer

# Command to run when container starts
CMD ["/bin/bash"] 