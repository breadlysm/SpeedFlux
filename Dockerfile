FROM python:3.11-slim-bookworm
LABEL maintainer="Breadlysm" \
    description="Original by Aiden Gilmartin. Maintained by Breadlysm"

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get -q -y install --no-install-recommends curl ca-certificates && \
    apt-get -q -y autoremove && apt-get -q -y clean && \
    rm -rf /var/lib/apt/lists/*

# Install Speedtest CLI via direct download (package manager doesn't support Bookworm yet)
RUN curl -sL https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz -o /tmp/speedtest.tgz && \
    tar -xzf /tmp/speedtest.tgz -C /usr/local/bin speedtest && \
    rm /tmp/speedtest.tgz && \
    chmod +x /usr/local/bin/speedtest

# Copy and final setup
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Execution
CMD ["python", "main.py"]
