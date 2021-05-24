FROM python:3.8-slim-buster
LABEL maintainer="Breadlysm" \
    description="Original by Aiden Gilmartin. Maintained by Breadlysm"

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update 
RUN apt-get -q -y install --no-install-recommends apt-utils gnupg1 apt-transport-https dirmngr

# Install Speedtest
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
RUN echo "deb https://ookla.bintray.com/debian buster main" | tee  /etc/apt/sources.list.d/speedtest.list
RUN apt-get update && apt-get -q -y install speedtest

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
