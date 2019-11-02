# Speedtest to InfluxDB

This is a small Python script that will continuously run the Speedtest CLI application by Ookla, reformat the data output and forward it on to an InfluxDB database.

You may want to do this so that you can track your internet connections consistency over time. Using Grafana you can view and explore this data easily.

![Grafana Dashboard](https://i.imgur.com/8cUdMy7.png)

## Using the script

Adjust the InfluxDB connection settings at the top of `main.py` to fit your setup and then run with one of the options listed below.

Be aware that this script will automatically accept the license and GDPR statement so that it can run non-interactively. Make sure you agree with them before running.

### 1. No Container

1. [Install the Speedtest CLI application by Ookla.](https://www.speedtest.net/apps/cli)

2. Install the InfluxDB client for library from Python.

    `pip install influxdb`

3. Run the script.

    `python3 ./main.py`

### 2. Run with Docker or Podman

1. Build the container.

    `docker build -t aidengilmartin/speedtest-influx ./`

2. Run the container.

    `docker run -d --name speedtest-influx aidengilmartin/speedtest-influx`

