import sys
from urllib3.exceptions import NewConnectionError

from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import speedflux
from requests.exceptions import ConnectionError


username = 'username'
password = 'password'

database = 'telegraf'
retention_policy = 'autogen'

bucket = f'{database}/{retention_policy}'

with InfluxDBClient(url='http://localhost:8086', token=f'{username}:{password}', org='-') as client:
 
class Influx2:
    def __init__(self, config):
        self.config = config
        self._client = None
        self.retries = 0

    
    @property
    def client(self):
        if not self._client:
            self._client = InfluxDBClient(
                url=self.config.INFLUX_DB_2_ADDRESS,
                token=self.config.INFLUX_DB_2_TOKEN,
                org=self.config.INFLUX_DB_2_ORG,
                debug=False
                )
            speedflux.LOG.debug("Client extablished")
        return self._client

    def write(self, data, data_type='Speedtest'):
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=self.config.INFlUX_DB_2_BUCKET, record=data)


    class Influx:
    def __init__(self, config):
        self.config = config
        self._client = None
        self.retries = 0
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
            speedflux.LOG.debug("Client extablished")
        return self._client

    def init_db(self):

        try:
            speedflux.LOG.debug("Intitializing Influx Database")
            databases = self.client.get_list_database()
            if len(list(filter(
                    lambda x: x['name'] ==
                        self.config.INFLUX_DB_DATABASE, databases))) == 0:
                self.client.create_database(
                    self.config.INFLUX_DB_DATABASE)  # Create if
            else:
                # Switch to if does exist.
                self.client.switch_database(self.config.INFLUX_DB_DATABASE)
            self.initilized = True
        except (ConnectionError, NewConnectionError) as bad_host:
            if self.retries == 3:
                speedflux.LOG.error(
                    "Database Init failed for 3rd time. Exiting")
                sys.exit()
            self.retries += 1
            speedflux.LOG.error(
                "Connection to influx host was refused. This likely "
                "means that the DB is down or INFLUX_DB_ADDRESS is "
                f"incorrect. It's currently '{self.config.INFLUX_DB_ADDRESS}'")
            speedflux.LOG.error("Full Error follows\n")
            speedflux.LOG.error(bad_host)
            speedflux.LOG.error(f"Retry {self.retries}: Initiliazing DB.")
            self.init_db()

    def write(self, data, data_type='Speedtest'):
        try:
            if self.client.write_points(data):
                speedflux.LOG.info(F"{data_type} data written successfully")
                speedflux.LOG.debug(F"Wrote `{data}` to Influx")
                self.retries = 0
            else:
                raise Exception(F"{data_type} write points did not complete")
        except (ConnectionError, NewConnectionError, Exception) as \
                bad_connection:
            if self.retries == 3:
                speedflux.LOG.error(
                    'Max retries exceeded for write. Check that database'
                    ' is on and can receive data')
                speedflux.LOG.error('Exiting')
                sys.exit()

            speedflux.LOG.error("Connection error occurred during write")
            speedflux.LOG.error(bad_connection)
            self.retries += 1
            speedflux.LOG.error("Reinitiating database and retrying.")
            self.init_db()
            self.write(data, data_type)

        except Exception as err:
            speedflux.LOG.error(F"{err}")

    def process_data(self, data):
        data = self.format_data(data)
        self.write(data)
