FROM python:3.8-slim-buster
LABEL maintainer="Breadlysm" \
    description="Original by Aiden Gilmartin. Maintained by Breadlysm"

ENV DEBIAN_FRONTEND=noninteractive

RUN true &&\
\
# Install dependencies
apt-get update && \
apt-get -q -y install --no-install-recommends apt-utils gnupg1 apt-transport-https dirmngr && \
\
# Install Python packages
pip3 install pythonping influxdb && \
\
# Clean up
apt-get -q -y autoremove && apt-get -q -y clean && \
rm -rf /var/lib/apt/lists/*

# Final setup & execution
ADD . /app
WORKDIR /app
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["main.py"]
