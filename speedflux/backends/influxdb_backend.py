"""InfluxDB 1.x backend for SpeedFlux."""
import sys
from urllib3.exceptions import NewConnectionError

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
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
            speedflux.LOG.debug(
                f"Creating InfluxDB client: {self.config.INFLUX_DB_ADDRESS}:"
                f"{self.config.INFLUX_DB_PORT}")
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
            speedflux.LOG.debug(f"Available databases: {databases}")

            db_name = self.config.INFLUX_DB_DATABASE
            db_exists = any(db['name'] == db_name for db in databases)

            if not db_exists:
                speedflux.LOG.info(f"Creating database: {db_name}")
                self.client.create_database(db_name)

            # Always switch to the target database
            speedflux.LOG.debug(f"Switching to database: {db_name}")
            self.client.switch_database(db_name)

            self.initialized = True
            self.retries = 0
            speedflux.LOG.debug(f"InfluxDB initialized successfully, using database: {db_name}")

        except (ConnectionError, NewConnectionError) as bad_host:
            if self.retries >= self.max_retries:
                speedflux.LOG.error(
                    f"InfluxDB init failed after {self.max_retries} retries. Exiting")
                sys.exit(1)
            self.retries += 1
            speedflux.LOG.error(
                f"Connection to InfluxDB refused. Address: "
                f"'{self.config.INFLUX_DB_ADDRESS}:{self.config.INFLUX_DB_PORT}'")
            speedflux.LOG.error(f"Error: {bad_host}")
            speedflux.LOG.error(f"Retry {self.retries}/{self.max_retries}: Initializing DB.")
            self.init_db()

    def format_data(self, data):
        speedflux.LOG.debug("Formatting speedtest data for InfluxDB")
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

        speedflux.LOG.debug(f"Formatted {len(influx_data)} measurements")
        return influx_data

    def write(self, data, data_type='Speedtest'):
        speedflux.LOG.debug(f"Writing {data_type} data to InfluxDB")
        try:
            result = self.client.write_points(data)
            if result:
                speedflux.LOG.info(f"{data_type} data written to InfluxDB")
                speedflux.LOG.debug(f"Write successful. Data: {data}")
                self.retries = 0
                return True
            else:
                speedflux.LOG.error(f"{data_type} write_points returned False")
                raise Exception(f"{data_type} write points did not complete")

        except (InfluxDBClientError, InfluxDBServerError) as db_error:
            speedflux.LOG.error(f"InfluxDB error during write: {db_error}")
            speedflux.LOG.debug(f"Failed data: {data}")
            self._handle_write_error(data, data_type, db_error)

        except (ConnectionError, NewConnectionError) as conn_error:
            speedflux.LOG.error(f"Connection error during InfluxDB write: {conn_error}")
            self._handle_write_error(data, data_type, conn_error)

        except Exception as err:
            speedflux.LOG.error(f"Unexpected error during InfluxDB write: {err}")
            speedflux.LOG.debug(f"Error type: {type(err).__name__}")
            self._handle_write_error(data, data_type, err)

        return False

    def _handle_write_error(self, data, data_type, error):
        """Handle write errors with retry logic."""
        if self.retries >= self.max_retries:
            speedflux.LOG.error(
                f'Max retries ({self.max_retries}) exceeded for InfluxDB write.')
            speedflux.LOG.error('Exiting')
            sys.exit(1)

        self.retries += 1
        speedflux.LOG.error(
            f"Retry {self.retries}/{self.max_retries}: Reinitializing database and retrying.")

        # Reset client to force reconnection
        self._client = None
        self.init_db()
        self.write(data, data_type)
