import subprocess

from pythonping import ping
import json
import datetime
import speedflux


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
        speedflux.LOG.info("Speedtest Successful...Writing to database(s)")
        data_json = json.loads(speedtest.stdout)
        speedflux.LOG.info(f"""Speedtest Data:
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
        # Write to all configured backends
        _write_to_all_backends(data_json, is_speedtest=True)
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
        # Write to all configured backends
        _write_to_all_backends(data, is_speedtest=False)


def _write_to_all_backends(data, is_speedtest=True):
    """Write data to all configured backends.

    Args:
        data: The data to write (speedtest JSON or ping data)
        is_speedtest: True for speedtest data, False for ping data
    """
    for backend in speedflux.BACKENDS:
        try:
            if is_speedtest:
                backend.process_data(data)
            else:
                # Ping data - use write_ping if available, otherwise write
                if hasattr(backend, 'write_ping'):
                    backend.write_ping(data)
                else:
                    backend.write(data, data_type='Ping')
        except Exception as err:
            speedflux.LOG.error(
                f"Error writing to {backend.name}: {err}"
            )
