FROM ubuntu:24.04

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
    python-is-python3 \
    python3-venv \
    pipenv \
    ca-certificates \
    gnupg \
    ripgrep \
    jq \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Add NodeSource repository and install Node.js 20.x
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Update npm to latest version and install claude CLI globally
RUN npm install -g npm@latest && \
    npm install -g @anthropic-ai/claude-code && \
# Install gemini globally    
    npm install -g @google/gemini-cli

# Give the ubuntu user sudo privileges (since host UID 1000 maps to ubuntu)
RUN mkdir -p /etc/sudoers.d && \
    echo ubuntu ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/ubuntu && \
    chmod 0440 /etc/sudoers.d/ubuntu

# Install aider as the ubuntu user
USER 1000:1000
RUN curl -LsSf https://aider.chat/install.sh | sh

# Set working directory (will be overridden at runtime)
WORKDIR /workspace

# Add .way/commands and user's local bin to system PATH
ENV PATH="/workspace/.way/commands:/home/ubuntu/.local/bin:$PATH"

# Set default shell
SHELL ["/bin/bash", "-c"]

# Set git config (will be overridden by dev.sh)
RUN git config --global user.email "developer@example.com"
RUN git config --global user.name "Developer"

# Command to run when container starts
#ENTRYPOINT ["/usr/local/bin/fix-permissions.sh"]
CMD ["/bin/bash"] 
