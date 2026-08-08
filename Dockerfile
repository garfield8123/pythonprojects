ARG RUNTIME_BASE=quay.io/centos/centos:stream10
FROM $RUNTIME_BASE AS runtime-base

# Declare the argument at the top of your Dockerfile
ARG DISCORD_TOKEN
ENV DISCORD_TOKEN=$DISCORD_TOKEN

# 1. Install Python 3.11 and pip
RUN ln -s /usr/bin/microdnf /usr/bin/dnf 2>/dev/null || echo -n && \
    dnf -y --nodocs install python3.11 python3.11-pip && \
    dnf -y --nodocs update && dnf clean all

# 2. Setup environment variables for the virtual environment
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /discord

# 3. Create the Python virtual environment
RUN python3.11 -m venv $VIRTUAL_ENV

# Inject the Discord token into the virtual environment's activate script
RUN echo 'export discordtoken="'"$DISCORD_TOKEN"'"' >> $VIRTUAL_ENV/bin/activate

# 4. Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# 5. Install dependencies inside the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project folders and files (respecting .dockerignore)
COPY . /discord/

RUN chmod +x /discord/installrequirements.sh && \
    /discord/installrequirements.sh

RUN chmod +x /discord/localimagebot/installmodel.sh && \
    /discord/localimagebot/installmodel.sh

RUN chmod +x /discord/gemenichat/installgemeni.sh && \
    /discord/gemenichat/installgemeni.sh

# 7. Run your Python Discord bot module
CMD ["python3", "-m", "discord.bot"]