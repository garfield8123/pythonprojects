# Use the official Python 3.11 slim image
FROM python:3.11-slim AS runtime-base

# Declare the argument at the top of your Dockerfile
ARG DISCORD_TOKEN
ENV DISCORD_TOKEN=$DISCORD_TOKEN

# 1. Install system dependencies required by Chrome/Chromium, Selenium, and Git LFS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    git-lfs \
    wget \
    curl \
    unzip \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup environment variables for the virtual environment
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /discord

# 3. Create the Python virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Inject the Discord token into the virtual environment's activate script
RUN echo 'export discordtoken="'"$DISCORD_TOKEN"'"' >> $VIRTUAL_ENV/bin/activate

# 4. Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# 5. Install dependencies inside the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project folders and files
COPY . /discord/

RUN chmod +x /discord/installrequirements.sh && \
    /discord/installrequirements.sh

RUN chmod +x /discord/localimagebot/installmodel.sh && \
    /discord/localimagebot/installmodel.sh

RUN chmod +x /discord/gemenichat/installgemeni.sh && \
    /discord/gemenichat/installgemeni.sh

# 7. Run your Python Discord bot module
CMD ["python3", "-m", "discord.bot"]