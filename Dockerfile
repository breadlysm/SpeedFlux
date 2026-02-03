FROM python:3.11-slim-bookworm
LABEL maintainer="Breadlysm" \
    description="Original by Aiden Gilmartin. Maintained by Breadlysm"

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get -q -y install --no-install-recommends curl ca-certificates gnupg

# Install Speedtest CLI from packagecloud.io (new official repo)
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash && \
    apt-get update && \
    apt-get -q -y install speedtest

# Clean up
RUN apt-get -q -y autoremove && apt-get -q -y clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and final setup
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Execution
CMD ["python", "main.py"]
