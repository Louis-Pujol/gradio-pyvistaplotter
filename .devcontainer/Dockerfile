# ---- Base image with Python 3.11 (>=3.10 requirement) ----
FROM python:3.11-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# ---- System deps ----
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Node.js 20+ (includes npm >= 9) ----
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ---- LibGL and LibOSMesa ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    libosmesa6 \
    libosmesa6-dev \
    libgl1 \
    libglx-mesa0 \
    libegl1 \
    libgl1-mesa-dri \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# ---- Upgrade pip (>=21.3 requirement) ----
RUN python -m pip install --upgrade pip

# ---- Install Gradio 5+ ----
RUN pip install --no-cache-dir --upgrade "gradio>=5"

# Expose common dev port
EXPOSE 7860

# Default shell
CMD ["/bin/bash"]