import subprocess
from pythonping import ping
from multiprocessing import Process
import json
import datetime
from speedflux.logs import log

def speedtest(config):
    if not config['server_id']:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], capture_output=True)
        log.info("Automatic server choice")
    else:
        speedtest = subprocess.run(
        ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json", "--server-id=" + config['server_id']], capture_output=True)
        log.info("Manual server choice : ID = " + config['server_id'])

    if speedtest.returncode == 0:  # Speedtest was successful.
        log.info("Speedtest Successful...Writing to Influx")
        data_json = json.loads(speedtest.stdout)
        log.info(F"""time: {data_json['timestamp']}
            ping: {data_json['ping']['latency']}ms
            download: {data_json['download']['bandwidth']/125000}Mb/s
            upload: {data_json['upload']['bandwidth'] / 125000}Mb/s
            isp: {data_json['isp']}
            ext. IP: {data_json['interface']['externalIp']}
            server id: {data_json['server']['id']} ({data_json['server']['name']} @ {data_json['server']['location']})
            """)
        config['influx'].process_data(data_json)
    else:  # Speedtest failed.
        log.info("Speedtest Failed :")
        log.debug(speedtest.stderr)
        log.debug(speedtest.stdout)


def pingtest(config):
    timestamp = datetime.datetime.utcnow()
    for target in config['ping_targets'].split(','):
        target = target.strip()
        log.debug('Running ping test...')
        pingtest = ping(target, verbose=False, timeout=1, count=1, size=128)
        data = [
            {
                'measurement': 'pings',
                'time': timestamp,
                'tags': {
                    'target' : target
                },
                'fields': {
                    'success' : int(pingtest._responses[0].error_message is None),
                    'rtt': float(0 if pingtest._responses[0].error_message is not None else pingtest.rtt_avg_ms)
                }
            }
        ]
        if config['namespace']:
            data[0]['tags']['namespace'] = config['namespace']
        config['influx'].write(data, data_type='Ping')
        