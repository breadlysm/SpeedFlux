


# SpeedFlux <img src='https://user-images.githubusercontent.com/3665468/119735610-974a0500-be4a-11eb-9149-dd12ceee03df.png' width='75'>
---

SpeedFlux will monitor your internet speeds at a regular interval and export all of the data to InfluxDB. 

It is mostly written in Python but, uses Ookla's SpeedTest CLI. This is a CLI app. We use Python subprocess to utilize this tool.

There are other Python packages out there that can use Ookla's systems but they are not official and don't provide the same data. This method is consistent and also provides several additional pieces of info. That extra info allows us to tag the data we send to InfluxDB many different ways. 

You can see on the Grafana image below some examples of those tags such as averageing the speeds of different testing sites and rank them. 
Other uses may tagging different interfaces and running an instance for each. [You can view those tagging options below](https://github.com/breadlysm/speedtest-to-influxdb/blob/master/README.md#tag-options) 

 The grafana image below is a prebuilt dashboard you can find at https://grafana.com/grafana/dashboards/13053. The json is also available in the report named `speedflux-grafana.json`. Additionally, other contributors have modified this dash and included a JSON file of those modifications. Use `GrafanaDash-SpeedTests.json` to import that dash into Grafana.

![OriginalDash](https://user-images.githubusercontent.com/3665468/116284820-8038ca00-a75b-11eb-9b30-4a9d26434f8d.png)

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

The InfluxDB connection settings are controlled by environment variables.

The variables available are:
- NAMESPACE = default - None
- INFLUX_DB_ADDRESS = default - influxdb
- INFLUX_DB_PORT = default - 8086
- INFLUX_DB_USER = default - {blank}
- INFLUX_DB_PASSWORD = default - {blank}
- INFLUX_DB_DATABASE = default - speedtests
- INFLUX_DB_TAGS = default - None * See below for options, '*' widcard for all *
- SPEEDTEST_INTERVAL = default - 5 (minutes)
- SPEEDTEST_SERVER_ID = default - {blank} * id from https://c.speedtest.net/speedtest-servers-static.php *
- PING_INTERVAL = default - 5 (seconds)
- PING_TARGETS = default - 1.1.1.1, 8.8.8.8 (csv of hosts to ping)
- LOG_TYPE = info

### Variable Notes
- Intervals are in minutes. *Script will convert it to seconds.*
- If any variables are not needed, don't declare them. Functions will operate with or without most variables. 
- Tags should be input without quotes. *INFLUX_DB_TAGS = isp, interface, external_ip, server_name, speedtest_url*
- NAMESPACE is used to collect data from multiple instances of the container into one database and select which you wish to view in Grafana. i.e. I have one monitoring my Starlink, the other my TELUS connection.
  
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
### Docker Run 

1. Run the container.
    ```
     docker run -d -t --name speedflux \
    -e 'NAMESPACE'='None' \
    -e 'INFLUX_DB_ADDRESS'='influxdb' \
    -e 'INFLUX_DB_PORT'='8086' \
    -e 'INFLUX_DB_USER'='_influx_user_' \
    -e 'INFLUX_DB_PASSWORD'='_influx_pass_' \
    -e 'INFLUX_DB_DATABASE'='speedtests' \
    -e 'SPEEDTEST_INTERVAL'='5' \
    -e 'SPEEDTEST_FAIL_INTERVAL'='5'  \
    -e 'SPEEDTEST_SERVER_ID'='12746' \
    -e 'LOG_TYPE'='info' \
    breadlysm/speedtest-to-influxdb
    ```
- You can also use `ghcr.io/breadlysm/speedflux` as GitHub containers is enabled. 
<br>
<br>

<sup><sub>**Pull Requests**</sub></sup>

<sub><sup>I will accept pull requests as long as core functionality and settings remain the same. Changes should be in addition to corefunctionality. I don't want a situation where a script auto-updates and ruins months/years of data or causes other headaches. Feel free to add yourself as contributing but I ask that links to containers do not change.</sub></sup>

---

This script looks to have been originally written by https://github.com/aidengilmartin/speedtest-to-influxdb/blob/master/main.py and I forked it from https://github.com/breadlysm/speedtest-to-influxdb. They did the hard work, I've continued to modify it though to fit my needs.
