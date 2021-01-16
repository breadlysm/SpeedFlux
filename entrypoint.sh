#!/bin/sh

printenv >> /etc/environment
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install speedtest-cli
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
echo "deb https://ookla.bintray.com/debian buster main" | tee  /etc/apt/sources.list.d/speedtest.list
apt-get update && apt-get -q -y install speedtest
#apt-get -q -y autoremove && apt-get -q -y clean
#rm -rf /var/lib/apt/lists/*

exec /usr/local/bin/python3 $@
