import os
import time
import json
import datetime
import subprocess
from pythonping import ping
from influxdb import InfluxDBClient
from multiprocessing import Process

# InfluxDB Settings
NAMESPACE = os.getenv('NAMESPACE', 'None')
DB_ADDRESS = os.getenv('INFLUX_DB_ADDRESS', 'influxdb')
DB_PORT = int(os.getenv('INFLUX_DB_PORT', '8086'))
DB_USER = os.getenv('INFLUX_DB_USER', '')
DB_PASSWORD = os.getenv('INFLUX_DB_PASSWORD', '')
DB_DATABASE = os.getenv('INFLUX_DB_DATABASE', 'speedtests')
DB_TAGS = os.getenv('INFLUX_DB_TAGS', None)
PING_TARGETS = os.getenv('PING_TARGETS', '1.1.1.1, 8.8.8.8')

# Speedtest Settings
# Time between tests (in minutes, converts to seconds).
TEST_INTERVAL = int(os.getenv('SPEEDTEST_INTERVAL', '5')) * 60
# Time before retrying a failed Speedtest (in minutes, converts to seconds).
TEST_FAIL_INTERVAL = int(os.getenv('SPEEDTEST_FAIL_INTERVAL', '5')) * 60
# Specific server ID
SERVER_ID = os.getenv('SPEEDTEST_SERVER_ID', '')
# Time between ping tests (in seconds).
PING_INTERVAL = int(os.getenv('PING_INTERVAL', '5'))

influxdb_client = InfluxDBClient(
    DB_ADDRESS, DB_PORT, DB_USER, DB_PASSWORD, None)


def init_db():
    databases = influxdb_client.get_list_database()

    if len(list(filter(lambda x: x['name'] == DB_DATABASE, databases))) == 0:
        influxdb_client.create_database(
            DB_DATABASE)  # Create if does not exist.
    else:
        # Switch to if does exist.
        influxdb_client.switch_database(DB_DATABASE)


def pkt_loss(data):
    if 'packetLoss' in data.keys():
        return int(data['packetLoss'])
    else:
        return 0


def tag_selection(data):
    tags = DB_TAGS
    options = {}

    # tag_switch takes in _data and attaches CLIoutput to more readable ids
    tag_switch = {
        'namespace': NAMESPACE,
        'isp': data['isp'],
        'interface': data['interface']['name'],
        'internal_ip': data['interface']['internalIp'],
        'interface_mac': data['interface']['macAddr'],
        'vpn_enabled': (False if data['interface']['isVpn'] == 'false' else True),
        'external_ip': data['interface']['externalIp'],
        'server_id': data['server']['id'],
        'server_name': data['server']['name'],
        'server_location': data['server']['location'],
        'server_country': data['server']['country'],
        'server_host': data['server']['host'],
        'server_port': data['server']['port'],
        'server_ip': data['server']['ip'],
        'speedtest_id': data['result']['id'],
        'speedtest_url': data['result']['url']
    }

    if tags is None:
        tags = 'namespace'
    elif '*' in tags:
        return tag_switch
    else:
        tags = 'namespace, ' + tags

    tags = tags.split(',')
    for tag in tags:
        # split the tag string, strip and add selected tags to {options} with corresponding tag_switch data
        tag = tag.strip()
        options[tag] = tag_switch[tag]

    return options


def format_for_influx(data):

    # There is additional data in the speedtest-cli output but it is likely not necessary to store.
    influx_data = [
        {
            'measurement': 'ping',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping']['jitter'],
                'latency': data['ping']['latency']
            }
        },
        {
            'measurement': 'download',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['download']['bandwidth'] / 125000,
                'bytes': data['download']['bytes'],
                'elapsed': data['download']['elapsed']
            }
        },
        {
            'measurement': 'upload',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['upload']['bandwidth'] / 125000,
                'bytes': data['upload']['bytes'],
                'elapsed': data['upload']['elapsed']
            }
        },
        {
            'measurement': 'packetLoss',
            'time': data['timestamp'],
            'fields': {
                'packetLoss': pkt_loss(data)
            }
        },
        {
            'measurement': 'speeds',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping']['jitter'],
                'latency': data['ping']['latency'],
                'packetLoss': pkt_loss(data),
                # Byte to Megabit
                'bandwidth_down': data['download']['bandwidth'] / 125000,
                'bytes_down': data['download']['bytes'],
                'elapsed_down': data['download']['elapsed'],
                # Byte to Megabit
                'bandwidth_up': data['upload']['bandwidth'] / 125000,
                'bytes_up': data['upload']['bytes'],
                'elapsed_up': data['upload']['elapsed']
            }
        }
    ]
    tags = tag_selection(data)
    if tags is not None:
        for measurement in influx_data:
            measurement['tags'] = tags

    return influx_data


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
#        time.sleep(TEST_FAIL_INTERVAL)


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

def main():
    pPing = Process(target=pingtest)
    pSpeed = Process(target=speedtest)

    init_db()  # Setup the database if it does not already exist.

    loopcount = 0
    while (1):  # Run a Speedtest and send the results to influxDB indefinitely.
        if loopcount == 0 or loopcount % PING_INTERVAL == 0:
            if pPing.is_alive():
                pPing.terminate()
            pPing = Process(target=pingtest)
            pPing.start()

        if loopcount == 0 or loopcount % TEST_INTERVAL == 0:
            if pSpeed.is_alive():
                pSpeed.terminate()
            pSpeed = Process(target=speedtest)
            pSpeed.start()

        if loopcount % ( PING_INTERVAL * TEST_INTERVAL ) == 0:
            loopcount = 0

        time.sleep(1)
        loopcount += 1

if __name__ == '__main__':
    print('Speedtest CLI data logger to InfluxDB started...')
    main()
