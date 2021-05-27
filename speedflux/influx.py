from influxdb import InfluxDBClient
from speedflux.logs import log
from requests.exceptions import HTTPError


class Influx:
    def __init__(self, config):
        self.config = config
        self._client = None
        self.init_db()

    @property
    def client(self):
        if not self._client:
            self._client = InfluxDBClient(
                self.config['db_host'],
                self.config['db_port'],
                self.config['db_user'],
                self.config['db_pass'],
                None)
            log.debug("Client extablished")
        return self._client

    def init_db(self):

        try:
            log.debug("Intitializing Influx Database")
            databases = self.client.get_list_database()
            if len(list(filter(
                    lambda x: x['name'] == self.config['db_name'], databases))
                   ) == 0:
                self.client.create_database(
                    self.config['db_name'])  # Create if does not exist.
            else:
                # Switch to if does exist.
                self.client.switch_database(self.config['db_name'])
        except HTTPError as httpe:
            log.error("Error connecting to database. Running a health test")
            health = self.test_connection()
            if not health:
                log.error("Couldn't connect to database. Ensure Influx is "
                          "running and that your credentials are correct")
                log.error(httpe)
            else:
                log.error("We connected to influx okay but, errors still "
                          "occurred. Forcing switch to chosen DB")
                try:
                    self.client.switch_database(self.config['db_name'])
                except Exception:
                    log.error("There are still problems switching to DB")
                    log.error("")

    def test_connection(self):
        health = self.client.health()
        if health.status == "pass":
            print("Connected to database successfully.")
            return True
        else:
            print(f"Connection failure: {health.message}!")
            return False

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
        tags = self.tag_selection(data)
        if tags is not None:
            for measurement in influx_data:
                measurement['tags'] = tags

        return influx_data

    def write(self, data, data_type='Speetest'):
        try:
            if self.client.write_points(data):
                log.info(F"{data_type} data written successfully")
                log.debug(F"Wrote `{data}` to Influx")
            else:
                raise Exception(F"{data_type} write points did not complete")
        except Exception as err:
            log.info(F"{err}")
            log.debug(F"Wrote {data_type} points `{data}` to Influx")

    def tag_selection(self, data):
        tags = self.config['db_tags']
        options = {}

        # tag_switch takes in _data and attaches CLIoutput to more readable ids
        tag_switch = {
            'namespace': self.config['namespace'],
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

    def process_data(self, data):
        data = self.format_data(data)
        self.write(data)
