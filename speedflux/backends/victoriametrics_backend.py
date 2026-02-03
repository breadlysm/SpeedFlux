"""VictoriaMetrics backend for SpeedFlux.

VictoriaMetrics supports InfluxDB line protocol, making migration seamless.
Data is sent via HTTP POST to the /write endpoint.
"""
import sys
import requests
from requests.exceptions import ConnectionError, Timeout

import speedflux
from .base import BaseBackend


class VictoriaMetricsBackend(BaseBackend):
    """VictoriaMetrics database backend using InfluxDB line protocol."""

    def __init__(self, config):
        super().__init__(config)
        self._session = None
        self.init_db()

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            speedflux.LOG.debug("VictoriaMetrics session established")
        return self._session

    @property
    def write_url(self):
        """Construct the VictoriaMetrics write URL."""
        address = self.config.VICTORIAMETRICS_ADDRESS
        port = self.config.VICTORIAMETRICS_PORT
        database = self.config.VICTORIAMETRICS_DATABASE
        return f"http://{address}:{port}/write?db={database}"

    def init_db(self):
        """Initialize connection to VictoriaMetrics.

        VictoriaMetrics doesn't require database creation - it accepts
        data immediately. We just verify connectivity.
        """
        try:
            speedflux.LOG.debug("Initializing VictoriaMetrics connection")
            address = self.config.VICTORIAMETRICS_ADDRESS
            port = self.config.VICTORIAMETRICS_PORT

            # Health check endpoint
            health_url = f"http://{address}:{port}/health"
            response = self.session.get(health_url, timeout=5)

            if response.status_code == 200:
                speedflux.LOG.info("VictoriaMetrics connection verified")
                self.initialized = True
            else:
                raise ConnectionError(
                    f"VictoriaMetrics health check failed: {response.status_code}")

        except (ConnectionError, Timeout) as err:
            if self.retries == self.max_retries:
                speedflux.LOG.error(
                    f"VictoriaMetrics init failed {self.max_retries} time(s). Exiting")
                sys.exit()
            self.retries += 1
            speedflux.LOG.error(
                "Connection to VictoriaMetrics was refused. "
                f"Address: '{self.config.VICTORIAMETRICS_ADDRESS}:{self.config.VICTORIAMETRICS_PORT}'")
            speedflux.LOG.error(f"Error: {err}")
            speedflux.LOG.error(f"Retry {self.retries}: Initializing VictoriaMetrics.")
            self.init_db()

    def _escape_line_protocol_value(self, value):
        """Escape a value for InfluxDB line protocol.
        
        In InfluxDB line protocol, tag and field values must escape:
        - Commas as \,
        - Spaces as \ 
        - Equals signs as \=
        
        Args:
            value: The value to escape (will be converted to string)
            
        Returns:
            Escaped string value
        """
        if value is None:
            return ''
        str_value = str(value)
        # Escape special characters: comma, space, equals
        return str_value.replace('\\', '\\\\').replace(',', '\\,').replace(' ', '\\ ').replace('=', '\\=')
    
    def format_data(self, data):
        """Format data as InfluxDB line protocol.

        VictoriaMetrics accepts InfluxDB line protocol format:
        measurement,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp
        """
        tags = self.tag_selection(data)
        if tags:
            tag_str = ','.join([f'{self._escape_line_protocol_value(k)}={self._escape_line_protocol_value(v)}' for k, v in tags.items()])
        else:
            tag_str = ''

        # Convert timestamp to nanoseconds
        timestamp = data['timestamp']

        lines = []

        # Ping measurement
        ping_fields = f"jitter={data['ping'].get('jitter', 0)},latency={data['ping'].get('latency', 0)}"
        lines.append(self._build_line('ping', tag_str, ping_fields, timestamp))

        # Download measurement
        download_bw = data['download'].get('bandwidth', 0) / 125000
        download_fields = f"bandwidth={download_bw},bytes={data['download'].get('bytes', 0)}i,elapsed={data['download']['elapsed']}i"
        lines.append(self._build_line('download', tag_str, download_fields, timestamp))

        # Upload measurement
        upload_bw = data['upload'].get('bandwidth', 0) / 125000
        upload_fields = f"bandwidth={upload_bw},bytes={data['upload']['bytes']}i,elapsed={data['upload']['elapsed']}i"
        lines.append(self._build_line('upload', tag_str, upload_fields, timestamp))

        # Packet loss measurement
        packet_loss = int(data.get('packetLoss', 0))
        lines.append(self._build_line('packetLoss', tag_str, f"packetLoss={packet_loss}i", timestamp))

        # Combined speeds measurement
        speeds_fields = (
            f"jitter={data['ping'].get('jitter', 0)},"
            f"latency={data['ping'].get('latency', 0)},"
            f"packetLoss={packet_loss}i,"
            f"bandwidth_down={download_bw},"
            f"bytes_down={data['download'].get('bytes', 0)}i,"
            f"elapsed_down={data['download'].get('elapsed')}i,"
            f"bandwidth_up={upload_bw},"
            f"bytes_up={data['upload'].get('bytes', 0)}i,"
            f"elapsed_up={data['upload'].get('elapsed')}i"
        )
        lines.append(self._build_line('speeds', tag_str, speeds_fields, timestamp))

        return '\n'.join(lines)

    def _build_line(self, measurement, tags, fields, timestamp):
        """Build a single line protocol entry."""
        if tags:
            return f"{measurement},{tags} {fields} {timestamp}"
        return f"{measurement} {fields} {timestamp}"

    def write(self, data, data_type='Speedtest'):
        """Write data to VictoriaMetrics using InfluxDB line protocol."""
        try:
            response = self.session.post(
                self.write_url,
                data=data,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )

            if response.status_code == 204:
                speedflux.LOG.info(f"{data_type} data written to VictoriaMetrics")
                speedflux.LOG.debug(f"Wrote to VictoriaMetrics: {data[:200]}...")
                self.retries = 0
            else:
                raise Exception(
                    f"VictoriaMetrics write failed: {response.status_code} - {response.text}")

        except (ConnectionError, Timeout) as err:
            if self.retries == self.max_retries:
                speedflux.LOG.error(
                    'Max retries exceeded for VictoriaMetrics write.')
                speedflux.LOG.error('Exiting')
                sys.exit()

            speedflux.LOG.error("Connection error during VictoriaMetrics write")
            speedflux.LOG.error(err)
            self.retries += 1
            speedflux.LOG.error("Retrying VictoriaMetrics write.")
            self.init_db()
            self.write(data, data_type)

        except Exception as err:
            speedflux.LOG.error(f"VictoriaMetrics error: {err}")

    def write_ping(self, data):
        """Write ping data to VictoriaMetrics.

        Args:
            data: List containing ping measurement dict
        """
        measurement = data[0]
        tags = measurement.get('tags', {})
        if tags:
            tag_str = ','.join([f'{self._escape_line_protocol_value(k)}={self._escape_line_protocol_value(v)}' for k, v in tags.items()])
        else:
            tag_str = ''

        fields = f"success={measurement['fields']['success']}i,rtt={measurement['fields']['rtt']}"
        timestamp = measurement['time'].isoformat() if hasattr(measurement['time'], 'isoformat') else measurement['time']

        line = self._build_line('pings', tag_str, fields, timestamp)
        self.write(line, data_type='Ping')
