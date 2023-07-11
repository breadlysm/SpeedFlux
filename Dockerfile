FROM python:3.8-slim-buster
LABEL maintainer="Breadlysm" \
    description="Original by Aiden Gilmartin. Maintained by Breadlysm"

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update 
RUN apt-get -q -y install --no-install-recommends apt-utils gnupg1 apt-transport-https dirmngr curl

# Install Speedtest
#Option 0 - Install from apt (not working or bad source)
# RUN curl -s https://install.speedtest.net/app/cli/install.deb.sh --output /opt/install.deb.sh
# RUN bash /opt/install.deb.sh
# RUN apt-get update && apt-get -q -y install speedtest
# RUN rm /opt/install.deb.sh

#Option 1 - Install from source
# Download https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz
# and place the binary in /usr/bin/speedtest (per https://github.com/breadlysm/SpeedFlux/issues/36#issuecomment-1609954934)
# RUN curl -s https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz --output /opt/speedtest.tgz
# RUN tar -xvf /opt/speedtest.tgz -C /opt
# RUN mv /opt/speedtest /usr/bin/speedtest
# RUN rm /opt/speedtest.tgz

#Option 2 - Install from apt
# This is the suggested method from https://www.speedtest.net/apps/cli just dockerized
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash
RUN apt-get -q -y install speedtest

# Clean up
RUN apt-get -q -y autoremove && apt-get -q -y clean 
RUN rm -rf /var/lib/apt/lists/*

# Copy and final setup
ADD . /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 
COPY . .

# Excetution
CMD ["python", "main.py"]
