



# SpeedFlux <img src='https://user-images.githubusercontent.com/3665468/119735610-974a0500-be4a-11eb-9149-dd12ceee03df.png' width='75'>
---

SpeedFlux will monitor your internet speeds at a regular interval and export all of the data to your chosen database backend.

It is mostly written in Python but, uses Ookla's SpeedTest CLI. This is a CLI app. We use Python subprocess to utilize this tool.

There are other Python packages out there that can use Ookla's systems but they are not official and don't provide the same data. This method is consistent and also provides several additional pieces of info. That extra info allows us to tag the data we send to the database many different ways.

You can see on the Grafana image below some examples of those tags such as averageing the speeds of different testing sites and rank them.
Other uses may tagging different interfaces and running an instance for each. [You can view those tagging options below](https://github.com/breadlysm/speedtest-to-influxdb/blob/master/README.md#tag-options)

 The grafana image below is a prebuilt dashboard you can find at https://grafana.com/grafana/dashboards/13053. The json is also available in the report named `speedflux-grafana.json`. Additionally, other contributors have modified this dash and included a JSON file of those modifications. Use `GrafanaDash-SpeedTests.json` to import that dash into Grafana.

![OriginalDash](https://user-images.githubusercontent.com/3665468/116284820-8038ca00-a75b-11eb-9b30-4a9d26434f8d.png)

## Supported Backends

SpeedFlux supports multiple database backends. You can use one or more simultaneously:

| Backend | Description |
|---------|-------------|
| **InfluxDB** | Original backend, InfluxDB 1.x support (default) |
| **VictoriaMetrics** | High-performance, cost-effective monitoring solution |
| **Prometheus** | Exposes metrics endpoint for Prometheus scraping |

### Selecting Backends

Use the `SPEEDFLUX_BACKENDS` environment variable to select which backends to use:

```bash
# Single backend (default behavior)
SPEEDFLUX_BACKENDS=influxdb

# Multiple backends
SPEEDFLUX_BACKENDS=influxdb,victoriametrics

# All three backends
SPEEDFLUX_BACKENDS=influxdb,victoriametrics,prometheus
```

## Docker
I have enabled GitHub containers for the app. You can use GitHub or DockerHub.
#### GitHub Containers
```shell
docker pull ghcr.io/breadlysm/speedflux:latest
```
#### Docker Hub
```shell
docker pull breadlysm/speedtest-to-influxdb
```

Also see [Using docker run](https://github.com/breadlysm/speedtest-to-influxdb#docker-run) you can replace the container with `breadlysm/speedtest-to-influxdb` with `ghcr.io/breadlysm/speedflux` and that command will work the same.

## Configuring the script

The connection settings are controlled by environment variables.

### General Settings
| Variable | Default | Description |
|----------|---------|-------------|
| NAMESPACE | None | Used to identify data from multiple instances |
| SPEEDFLUX_BACKENDS | influxdb | Comma-separated list of backends (influxdb, victoriametrics, prometheus) |
| LOG_TYPE | info | Logging level |

### InfluxDB Settings
| Variable | Default | Description |
|----------|---------|-------------|
| INFLUX_DB_ADDRESS | influxdb | InfluxDB server address |
| INFLUX_DB_PORT | 8086 | InfluxDB server port |
| INFLUX_DB_USER | {blank} | InfluxDB username |
| INFLUX_DB_PASSWORD | {blank} | InfluxDB password |
| INFLUX_DB_DATABASE | speedtests | InfluxDB database name |
| INFLUX_DB_TAGS | None | Tags to apply to data (see Tag Options below) |

### VictoriaMetrics Settings
| Variable | Default | Description |
|----------|---------|-------------|
| VICTORIAMETRICS_ADDRESS | victoriametrics | VictoriaMetrics server address |
| VICTORIAMETRICS_PORT | 8428 | VictoriaMetrics server port |
| VICTORIAMETRICS_DATABASE | speedtests | Database name (used in write URL) |

### Prometheus Settings
| Variable | Default | Description |
|----------|---------|-------------|
| PROMETHEUS_PORT | 9091 | Port to expose /metrics endpoint |

When using the Prometheus backend, metrics are available at `http://localhost:9091/metrics`.

### SpeedTest Settings
| Variable | Default | Description |
|----------|---------|-------------|
| SPEEDTEST_INTERVAL | 180 | Minutes between speedtest runs |
| SPEEDTEST_SERVER_ID | {blank} | Server ID(s) to test against (comma-separated for rotation) |
| SPEEDTEST_COUNTRY | {blank} | Country code for server selection (e.g., US, GB, DE) |

### Ping Settings
| Variable | Default | Description |
|----------|---------|-------------|
| PING_INTERVAL | 120 | Seconds between ping tests |
| PING_TARGETS | 1.1.1.1, 8.8.8.8 | Comma-separated list of hosts to ping |

### Variable Notes
- Speedtest interval is in minutes. Ping interval is in seconds.
- If any variables are not needed, don't declare them. Functions will operate with or without most variables.
- Tags should be input without quotes. *INFLUX_DB_TAGS = isp, interface, external_ip, server_name, speedtest_url*
- NAMESPACE is used to collect data from multiple instances of the container into one database and select which you wish to view in Grafana. i.e. I have one monitoring my Starlink, the other my TELUS connection.

### Multiple Server Testing
You can specify multiple speedtest server IDs to rotate through:
```bash
SPEEDTEST_SERVER_ID=1234,5678,9012
```
Each test will use the next server in the list, allowing you to compare results from different servers (e.g., your ISP's server vs external servers).

Find server IDs at: https://c.speedtest.net/speedtest-servers-static.php

### Tag Options
The Ookla speedtest app provides a nice set of data beyond the upload and download speed. The list is below.

| Tag Name 	| Description 	|
|-	|-	|
| isp 	| Your connections ISP 	|
| interface 	| Your devices connection interface 	|
| internal_ip 	| Your container or devices IP address 	|
| interface_mac 	| Mac address of your devices interface 	|
| vpn_enabled 	| Determines if VPN is enabled or not? I wasn't sure what this represented 	|
| external_ip 	| Your devices external IP address 	|
| server_id 	| The Speedtest ID of the server that  was used for testing 	|
| server_name 	| Name of the Speedtest server used  for testing 	|
| server_country 	| Country where the Speedtest server  resides 	|
| server_location | Location where the Speedtest server  resides  |
| server_host 	| Hostname of the Speedtest server 	|
| server_port 	| Port used by the Speedtest server 	|
| server_ip 	| Speedtest server's IP address 	|
| speedtest_id 	| ID of the speedtest results. Can be  used on their site to see results 	|
| speedtest_url 	| Link to the testing results. It provides your results as it would if you tested on their site.  	|

### Additional Notes
Be aware that this script will automatically accept the license and GDPR statement so that it can run non-interactively. Make sure you agree with them before running.

## Running the Script

### Docker Compose
If you already have Docker and Docker Compose installed, you can use the included docker compose file.
1. clone the github repo
2. navigate to the folder
3. edit the `docker-compose.yml` file with your settings
4. then run `docker compose up`

### Docker Run (InfluxDB)

```bash
docker run -d -t --name speedflux \
  -e 'NAMESPACE'='None' \
  -e 'INFLUX_DB_ADDRESS'='influxdb' \
  -e 'INFLUX_DB_PORT'='8086' \
  -e 'INFLUX_DB_USER'='_influx_user_' \
  -e 'INFLUX_DB_PASSWORD'='_influx_pass_' \
  -e 'INFLUX_DB_DATABASE'='speedtests' \
  -e 'SPEEDTEST_INTERVAL'='5' \
  -e 'SPEEDTEST_SERVER_ID'='12746' \
  -e 'LOG_TYPE'='info' \
  breadlysm/speedtest-to-influxdb
```

### Docker Run (VictoriaMetrics)

```bash
docker run -d -t --name speedflux \
  -e 'SPEEDFLUX_BACKENDS'='victoriametrics' \
  -e 'VICTORIAMETRICS_ADDRESS'='victoriametrics' \
  -e 'VICTORIAMETRICS_PORT'='8428' \
  -e 'SPEEDTEST_INTERVAL'='5' \
  -e 'LOG_TYPE'='info' \
  breadlysm/speedtest-to-influxdb
```

### Docker Run (Prometheus)

```bash
docker run -d -t --name speedflux \
  -e 'SPEEDFLUX_BACKENDS'='prometheus' \
  -e 'PROMETHEUS_PORT'='9091' \
  -e 'SPEEDTEST_INTERVAL'='5' \
  -e 'LOG_TYPE'='info' \
  -p 9091:9091 \
  breadlysm/speedtest-to-influxdb
```

Then configure Prometheus to scrape `http://speedflux:9091/metrics`.

- You can also use `ghcr.io/breadlysm/speedflux` as GitHub containers is enabled.
<br>
<br>

<sup><sub>**Pull Requests**</sub></sup>

<sub><sup>I will accept pull requests as long as core functionality and settings remain the same. Changes should be in addition to corefunctionality. I don't want a situation where a script auto-updates and ruins months/years of data or causes other headaches. Feel free to add yourself as contributing but I ask that links to containers do not change.</sub></sup>

---

This script looks to have been originally written by https://github.com/aidengilmartin/speedtest-to-influxdb/blob/master/main.py and I forked it from https://github.com/breadlysm/speedtest-to-influxdb. They did the hard work, I've continued to modify it though to fit my needs.
