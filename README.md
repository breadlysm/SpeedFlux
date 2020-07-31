# Speedtest to InfluxDB

This is a Python script that will continuously run the official Speedtest CLI application by Ookla, takes input from environment variables, formats data and writes it to an InfluxDB database.

This script will allow you to measure your internet connections speed and consistency over time. It uses env variables as configuration. It's as easy to use as telling your Docker server a 1 line command and you'll be set. Using Grafana you can start exploring this data easily. 

![Grafana Dashboard](https://i.imgur.com/8cUdMy7.png)

There are some added features to allow some additional details that Ookla provides as tags on your data. Some examples are your current ISP, the interface being used, the server who hosted the test. Overtime, you could identify if some serers are performing better than others. 

## Configuring the script

The InfluxDB connection settings are controlled by environment variables.

The variables available are:
- INFLUX_DB_ADDRESS = 192.168.1.xxx
- INFLUX_DB_PORT = 8086
- INFLUX_DB_USER = user
- INFLUX_DB_PASSWORD = pass
- INFLUX_DB_DATABASE = speedtest
- INFLUX_DB_TAGS = *comma seperated list of tags. See below for options*
- SPEEDTEST_INTERVAL = 60
- SPEEDTEST_FAIL_INTERVAL = 5

### Variable Notes
- Intervals are in minutes. *Script will convert it to seconds.*
- If any variables are not needed, don't declare them. Functions will operate with or without most variables. 
- Tags should be input without quotes. *INFLUX_DB_TAGS = isp, interface, external_ip, server_name, speedtest_url*
  
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
| server_host 	| Hostname of the Speedtest server 	|
| server_port 	| Port used by the Speedtest server 	|
| server_ip 	| Speedtest server's IP address 	|
| speedtest_id 	| ID of the speedtest results. Can be  used on their site to see results 	|
| speedtest_url 	| Link to the testing results. It provides your results as it would if you tested on their site.  	|

### Additional Notes
Be aware that this script will automatically accept the license and GDPR statement so that it can run non-interactively. Make sure you agree with them before running.

## Running the Script

### Ideal option, run as a Docker container. 

1. Build the container.

    `docker build -t breadlysm/speedtest-to-influxdb ./`

2. Run the container.
    ```
    docker run -d --name speedtest-influx \
    -e 'INFLUX_DB_ADDRESS'='_influxdb_host_' \
    -e 'INFLUX_DB_PORT'='8086' \
    -e 'INFLUX_DB_USER'='_influx_user_' \
    -e 'INFLUX_DB_PASSWORD'='_influx_pass_' \
    -e 'INFLUX_DB_DATABASE'='speedtest' \
    -e 'SPEEDTEST_INTERVAL'='1800' \
    -e 'SPEEDTEST_FAIL_INTERVAL'='60'  \
    breadlysm/speedtest-to-influxdb
    ```
### No Container

1. Clone the repo 

    `git clone https://github.com/breadlysm/speedtest-to-influxdb.git`   

2. Configure the .env file in the repo or set the environment variables on your device. 

3. [Install the Speedtest CLI application by Ookla.](https://www.speedtest.net/apps/cli)

    NOTE: The `speedtest-cli` package in distro repositories is an unofficial client. It will need to be uninstalled before installing the Ookla Speedtest CLI application with the directions on their website.

4. Install the InfluxDB client for library from Python.

    `pip install influxdb`

5. Run the script.

    `python3 ./main.py`



This script looks to have been originally written by https://github.com/aidengilmartin/speedtest-to-influxdb/blob/master/main.py and I forked it from https://github.com/martinfrancois/speedtest-to-influxdb. They did the hard work, I've continued to modify it though to fit my needs.