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
    python-is-python3 \
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

# Update npm to latest version and install claude CLI globally
RUN npm install -g npm@latest && \
    npm install -g @anthropic-ai/claude-code

# Set working directory
WORKDIR /workspace

# Add .way/commands to system PATH
ENV PATH="/workspace/.way/commands:$PATH"

# Create a user that matches the host user
ARG USERNAME=riaz
ARG USER_UID=1001
ARG USER_GID=$USER_UID

# Create the user with the exact UID/GID
RUN groupadd --gid $USER_GID $USERNAME || true && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME || true && \
    apt-get update && \
    apt-get install -y sudo python3.10-venv && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Create a script to fix permissions
#RUN echo '#!/bin/bash\n\
#if [ -d "/workspace" ]; then\n\
#    sudo chown -R $USER_UID:$USER_GID /workspace\n\
#fi\n\
#exec "$@"' > /usr/local/bin/fix-permissions.sh \
#    && chmod +x /usr/local/bin/fix-permissions.sh

# Set default shell
SHELL ["/bin/bash", "-c"]

# Switch to non-root user
USER $USER_UID:$USER_GID

# Command to run when container starts
#ENTRYPOINT ["/usr/local/bin/fix-permissions.sh"]
CMD ["/bin/bash"] 