#!/bin/sh

printenv >> /etc/environment
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install speedtest-cli
if [ ! -e /usr/bin/speedtest ]
then
  apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
  echo "deb https://ookla.bintray.com/debian buster main" | tee  /etc/apt/sources.list.d/speedtest.list
  apt-get update && apt-get -q -y install speedtest
  apt-get -q -y autoremove && apt-get -q -y clean
  rm -rf /var/lib/apt/lists/*
fi

exec /usr/local/bin/python3 $@
