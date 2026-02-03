"""InfluxDB 1.x backend for SpeedFlux."""
import sys
from urllib3.exceptions import NewConnectionError

from influxdb import InfluxDBClient
import speedflux
from requests.exceptions import ConnectionError

from .base import BaseBackend


class InfluxDBBackend(BaseBackend):
    """InfluxDB 1.x database backend."""

    def __init__(self, config):
        self._client = None
        super().__init__(config)
        self.init_db()

    @property
    def client(self):
        if not self._client:
            self._client = InfluxDBClient(
                self.config.INFLUX_DB_ADDRESS,
                self.config.INFLUX_DB_PORT,
                self.config.INFLUX_DB_USER,
                self.config.INFLUX_DB_PASSWORD,
                None)
            speedflux.LOG.debug("InfluxDB client established")
        return self._client

    def init_db(self):
        try:
            speedflux.LOG.debug("Initializing InfluxDB Database")
            databases = self.client.get_list_database()
            if len(list(filter(
                    lambda x: x['name'] ==
                        self.config.INFLUX_DB_DATABASE, databases))) == 0:
                self.client.create_database(
                    self.config.INFLUX_DB_DATABASE)
            else:
                self.client.switch_database(self.config.INFLUX_DB_DATABASE)
            self.initialized = True
        except (ConnectionError, NewConnectionError) as bad_host:
            if self.retries == self.max_retries:
                speedflux.LOG.error(
                    f"InfluxDB init failed for {self.max_retries} time(s). Exiting")
                sys.exit()
            self.retries += 1
            speedflux.LOG.error(
                "Connection to InfluxDB host was refused. This likely "
                "means that the DB is down or INFLUX_DB_ADDRESS is "
                f"incorrect. It's currently '{self.config.INFLUX_DB_ADDRESS}'")
            speedflux.LOG.error("Full Error follows\n")
            speedflux.LOG.error(bad_host)
            speedflux.LOG.error(f"Retry {self.retries}: Initializing DB.")
            self.init_db()

    def format_data(self, data):
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
                    'bandwidth': data['download'].get('bandwidth', 0) / 125000,
                    'bytes': data['download'].get('bytes', 0),
                    'elapsed': data['download']['elapsed']
                }
            },
            {
                'measurement': 'upload',
                'time': data['timestamp'],
                'fields': {
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
                    'bandwidth_down': data['download'].get(
                        'bandwidth', 0) / 125000,
                    'bytes_down': data['download'].get(
                        'bytes', 0),
                    'elapsed_down': data['download'].get(
                        'elapsed'),
                    'bandwidth_up': data['upload'].get(
                        'bandwidth', 0) / 125000,
                    'bytes_up': data['upload'].get(
                        'bytes', 0),
                    'elapsed_up': data['upload'].get(
                        'elapsed')
                }
            }
        ]
        tags = self.tag_selection(data)
        if tags is not None:
            for measurement in influx_data:
                measurement['tags'] = tags

        return influx_data

    def write(self, data, data_type='Speedtest'):
        try:
            if self.client.write_points(data):
                speedflux.LOG.info(f"{data_type} data written to InfluxDB")
                speedflux.LOG.debug(f"Wrote `{data}` to InfluxDB")
                self.retries = 0
            else:
                raise Exception(f"{data_type} write points did not complete")
        except (ConnectionError, NewConnectionError, Exception) as \
                bad_connection:
            if self.retries == self.max_retries:
                speedflux.LOG.error(
                    'Max retries exceeded for InfluxDB write. Check that database'
                    ' is on and can receive data')
                speedflux.LOG.error('Exiting')
                sys.exit()

            speedflux.LOG.error("Connection error occurred during InfluxDB write")
            speedflux.LOG.error(bad_connection)
            self.retries += 1
            speedflux.LOG.error("Reinitiating database and retrying.")
            self.init_db()
            self.write(data, data_type)

        except Exception as err:
            speedflux.LOG.error(f"{err}")
