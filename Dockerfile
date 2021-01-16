FROM python:3.8-slim-buster
LABEL maintainer="Team QLUSTOR <team@qlustor.com>" \
    description="Original by Aiden Gilmartin. Speedtest to InfluxDB data bridge"

ENV DEBIAN_FRONTEND=noninteractive

RUN true &&\
\
# Install dependencies
apt-get update && \
apt-get -q -y install --no-install-recommends apt-utils gnupg1 apt-transport-https dirmngr && \
\
# Install Python packages
pip3 install influxdb && \
\
# Clean up
apt-get -q -y autoremove && apt-get -q -y clean && \
rm -rf /var/lib/apt/lists/*

# Final setup & execution
ADD . /app
WORKDIR /app
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["main.py"]
