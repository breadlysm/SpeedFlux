# speedtest-influx

This is a small Python script that will continuously run the OOKLA Speedtest CLI application, reformat the data output and forward it on to an InfluxDB database.

You may want to do this so that you can track your internet connections consistency over time. Using Grafana you can view and explore this data easily.

![Grafana Dashboard](https://i.imgur.com/8cUdMy7.png)

## Using the script

### Option 1 - No Container

1. [Install the OOKA Speedtest CLI application.](https://www.speedtest.net/apps/cli)

2. Install the InfluxDB client for library from Python.

    `pip install influxdb`

3. Run the script.

    `python3 ./main.py`

### Option 2 - Run with Docker/Podman

1. Build the container.

    `docker build -t aidengilmartin/speedtest-influx ./`

    `podman build -t aidengilmartin/speedtest-influx ./`

2. Run the container.

    `docker run -d --name speedtest-influx aidengilmartin/speedtest-influx`

    `podman run -d --name speedtest-influx aidengilmartin/speedtest-influx`
