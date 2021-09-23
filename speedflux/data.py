import subprocess

from pythonping import ping
import json
import datetime
import speedflux
from influxdb_client import Point


def speedtest():
    if not speedflux.CONFIG.SPEEDTEST_SERVER_ID:
        speedtest = subprocess.run(
            ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"],
            capture_output=True)
        speedflux.LOG.info("Automatic server choice")
    else:
        speedtest = subprocess.run(
            ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json",
                f"--server-id={speedflux.CONFIG.SPEEDTEST_SERVER_ID}"],
            capture_output=True)
        speedflux.LOG.info("Manual server choice : "
                           f"ID = {speedflux.CONFIG.SPEEDTEST_SERVER_ID}")

    if speedtest.returncode == 0:  # Speedtest was successful.
        speedflux.LOG.info("Speedtest Successful...Writing to Influx")
        data_json = json.loads(speedtest.stdout)
        speedflux.LOG.info(F"""Speedtest Data:
            time: {data_json['timestamp']}
            ping: {data_json['ping']['latency']}ms
            download: {data_json['download']['bandwidth']/125000}Mb/s
            upload: {data_json['upload']['bandwidth'] / 125000}Mb/s
            isp: {data_json['isp']}
            ext. IP: {data_json['interface']['externalIp']}
            server id: {data_json['server']['id']}
            server location: ({data_json['server']['name']} @ \
                {data_json['server']['location']})
            """)
        points = format_speedtest(data_json)
        for measurement in points:
            speedflux.INFLUXDB.write(measurement)
    else:  # Speedtest failed.
        speedflux.LOG.info("Speedtest Failed :")
        speedflux.LOG.debug(speedtest.stderr)
        speedflux.LOG.debug(speedtest.stdout)


def pingtest():
    timestamp = datetime.datetime.utcnow()
    for target in speedflux.CONFIG.PING_TARGETS.split(','):
        target = target.strip()
        speedflux.LOG.debug('Running ping test...')
        pingtest = ping(target, verbose=False, timeout=1, count=1, size=128)
        data = [
            {
                'measurement': 'pings',
                'time': timestamp,
                'tags': {
                    'target': target
                },
                'fields': {
                    'success': int(
                        pingtest._responses[0].error_message is None),
                    'rtt': float(
                        0 if pingtest._responses[0].error_message is
                        not None else pingtest.rtt_avg_ms)
                }
            }
        ]
        if speedflux.CONFIG.NAMESPACE:
            data[0]['tags']['namespace'] = speedflux.CONFIG.NAMESPACE
        point = Point.from_dict(data[0])
        speedflux.INFLUXDB.write(point)


def format_speedtest(data):
    influx_data = [
        {
            'measurement': 'ping',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping'].get('jitter', 0),
                'latency': data['ping'].get('latency', 0)
            }
        },
        {
            'measurement': 'download',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['download'].get('bandwidth', 0) / 125000,
                'bytes': data['download'].get('bytes', 0),
                'elapsed': data['download']['elapsed']
            }
        },
        {
            'measurement': 'upload',
            'time': data['timestamp'],
            'fields': {
                # Byte to Megabit
                'bandwidth': data['upload'].get('bandwidth', 0) / 125000,
                'bytes': data['upload']['bytes'],
                'elapsed': data['upload']['elapsed']
            }
        },
        {
            'measurement': 'packetLoss',
            'time': data['timestamp'],
            'fields': {
                'packetLoss': int(data.get('packetLoss', 0))
            }
        },
        {
            'measurement': 'speeds',
            'time': data['timestamp'],
            'fields': {
                'jitter': data['ping'].get('jitter', 0),
                'latency': data['ping'].get('latency', 0),
                'packetLoss': int(data.get('packetLoss', 0)),
                # Byte to Megabit
                'bandwidth_down': data['download'].get(
                    'bandwidth', 0) / 125000,
                'bytes_down': data['download'].get(
                    'bytes', 0),
                'elapsed_down': data['download'].get(
                    'elapsed'),
                # Byte to Megabit
                'bandwidth_up': data['upload'].get(
                    'bandwidth', 0) / 125000,
                'bytes_up': data['upload'].get(
                    'bytes', 0),
                'elapsed_up': data['upload'].get(
                    'elapsed')
            }
        }
    ]
    tags = tag_selection(data)
    if tags is not None:
        for measurement in influx_data:
            measurement['tags'] = tags
    influx_data = json_to_point(influx_data)
    return influx_data


def json_to_point(data):
    points = []
    for stat in data:
        print(stat['measurement'])
        point = Point.from_dict(stat)
        points.append(point)
    return points


def tag_selection(data):
    tags = speedflux.CONFIG.INFLUX_DB_TAGS
    options = {}

    # tag_switch takes in _data and attaches CLIoutput to more readable ids
    tag_switch = {
        'namespace': speedflux.CONFIG.NAMESPACE,
        'isp': data['isp'],
        'interface': data['interface']['name'],
        'internal_ip': data['interface']['internalIp'],
        'interface_mac': data['interface']['macAddr'],
        'vpn_enabled': (
            False if data['interface']['isVpn'] == 'false' else True),
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
        # split the tag string, strip and add selected tags to {options}
        # with corresponding tag_switch data
        tag = tag.strip()
        options[tag] = tag_switch[tag]
    return options
