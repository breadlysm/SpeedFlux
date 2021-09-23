from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

import speedflux


class InfluxDB:

    @property
    def client(self):
        if not self._client:
            self._client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                debug=False
                )
            speedflux.LOG.debug("Client extablished")
        return self._client

    def write(self, data):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=self.bucket, record=data)


class Influx1(InfluxDB):
    def __init__(self):
        self._client = None
        self.url = f"{speedflux.CONFIG.INFLUX_DB_ADDRESS}:" \
                   f"{speedflux.CONFIG.INFLUX_DB_PORT}"
        self.token = f"{speedflux.CONFIG.INFLUX_DB_USER}:" \
                     f"{speedflux.CONFIG.INFLUX_DB_PASSWORD}"
        self.org = '-'
        self.bucket = speedflux.CONFIG.INFLUX_DB_DATABASE


class Influx2(InfluxDB):
    def __init__(self):
        self._client = None
        super(InfluxDB, self).__init__()
        self.url = f"{speedflux.CONFIG.INFLUX_TWO_ADDRESS}:" \
                   f"{speedflux.CONFIG.INFLUX_TWO_PORT}"
        self.token = speedflux.CONFIG.INFLUX_TWO_TOKEN
        self.org = speedflux.CONFIG.INFLUX_TWO_ORG
        self.bucket = speedflux.CONFIG.INFLUX_TWO_BUCKET
