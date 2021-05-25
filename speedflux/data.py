import subprocess
from pythonping import ping
from influxdb import InfluxDBClient
from multiprocessing import Process


def speedtest():
    if not SERVER_ID:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], capture_output=True)
        print("Automatic server choice")
    else:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json", "--server-id=" + SERVER_ID], capture_output=True)
        print("Manual server choice : ID = " + SERVER_ID)

    if speedtest.returncode == 0:  # Speedtest was successful.
        print("Speedtest Successful :")
        data_json = json.loads(speedtest.stdout)
        print("time: " + str(data_json['timestamp']) + " - ping: " + str(data_json['ping']['latency']) + " ms - download: " + str(data_json['download']['bandwidth']/125000) + " Mb/s - upload: " + str(data_json['upload']['bandwidth'] / 125000) + " Mb/s - isp: " + data_json['isp'] + " - ext. IP: " + data_json['interface']['externalIp'] + " - server id: " + str(data_json['server']['id']) + " (" + data_json['server']['name'] + " @ " + data_json['server']['location'] + ")")
        data = format_for_influx(data_json)
        if influxdb_client.write_points(data) == True:
            print("Data written to DB successfully")
    else:  # Speedtest failed.
        print("Speedtest Failed :")
        print(speedtest.stderr)
        print(speedtest.stdout)


def pingtest():
    timestamp = datetime.datetime.utcnow()
    for target in PING_TARGETS.split(','):
        target = target.strip()
        pingtest = ping(target, verbose=False, timeout=1, count=1, size=128)
        data = [
            {
                'measurement': 'pings',
                'time': timestamp,
                'tags': {
                    'namespace': NAMESPACE,
                    'target' : target
                },
                'fields': {
                    'success' : int(pingtest._responses[0].error_message is None),
                    'rtt': float(0 if pingtest._responses[0].error_message is not None else pingtest.rtt_avg_ms)
                }
            }
        ]
        if influxdb_client.write_points(data) == True:
            print("Ping data written to DB successfully")
        else:  # Speedtest failed.
            print("Ping Failed.")