import subprocess

from pythonping import ping
import json
import datetime
import speedflux

# Module-level state for server rotation
_server_index = 0


def _get_next_server():
    """Get the next server ID from the rotation list.

    Returns:
        Server ID string or None for automatic selection
    """
    global _server_index

    server_ids = speedflux.CONFIG.SPEEDTEST_SERVER_ID
    if not server_ids:
        return None

    # Split comma-separated server IDs
    servers = [s.strip() for s in server_ids.split(',') if s.strip()]
    if not servers:
        return None

    # Get current server and advance index
    server = servers[_server_index % len(servers)]
    _server_index += 1

    return server


def _build_speedtest_command():
    """Build the speedtest command with appropriate arguments.

    Returns:
        List of command arguments
    """
    cmd = ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"]

    # Add country filter if specified
    country = speedflux.CONFIG.SPEEDTEST_COUNTRY
    if country:
        cmd.extend(["--server-selection-method", "nearest"])

    # Add server ID if specified (takes precedence)
    server_id = _get_next_server()
    if server_id:
        cmd.append(f"--server-id={server_id}")
        speedflux.LOG.info(f"Using server ID: {server_id}")
    elif country:
        # Country filter only applies when no specific server is set
        # Note: speedtest CLI doesn't have direct --country flag,
        # but we can log the intent for clarity
        speedflux.LOG.info(f"Server selection with country preference: {country}")
    else:
        speedflux.LOG.info("Automatic server choice")

    return cmd


def speedtest():
    cmd = _build_speedtest_command()
    speedtest_result = subprocess.run(cmd, capture_output=True)

    if speedtest_result.returncode == 0:  # Speedtest was successful.
        speedflux.LOG.info("Speedtest Successful...Writing to database(s)")
        data_json = json.loads(speedtest_result.stdout)
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
        speedflux.LOG.debug(speedtest_result.stderr)
        speedflux.LOG.debug(speedtest_result.stdout)


def pingtest():
    timestamp = datetime.datetime.utcnow()
    for target in speedflux.CONFIG.PING_TARGETS.split(','):
        target = target.strip()
        speedflux.LOG.debug('Running ping test...')
        pingtest_result = ping(target, verbose=False, timeout=1, count=1, size=128)
        data = [
            {
                'measurement': 'pings',
                'time': timestamp,
                'tags': {
                    'target': target
                },
                'fields': {
                    'success': int(
                        pingtest_result._responses[0].error_message is None),
                    'rtt': float(
                        0 if pingtest_result._responses[0].error_message is
                        not None else pingtest_result.rtt_avg_ms)
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
