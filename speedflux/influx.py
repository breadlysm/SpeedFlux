from influxdb import InfluxDBClient
from speedflux.logs import log

class Influx:
    def __init__(self, config):
        self.config = config
        self.client = InfluxDBClient(self.config['db_host'], 
                                    self.config['db_port'], 
                                    self.config['db_user'], 
                                    self.config['db_pass'], 
                                    None)
        self.init_db()

    def init_db(self):
        databases = self.client.get_list_database()

        if len(list(filter(lambda x: x['name'] == self.config['db_name'], databases))) == 0:
            self.client.create_database(
                self.config['db_name'])  # Create if does not exist.
        else:
            # Switch to if does exist.
            self.client.switch_database(self.config['db_name'])

    def format_data(self, data):
        # There is additional data in the speedtest-cli output but it is likely not necessary to store.
        influx_data = [
            {
                'measurement': 'ping',
                'time': data['timestamp'],
                'fields': {
                    'jitter': data['ping'].get('jitter', 0),
                    'latency': data['ping'].get('latency',0)
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
                    'latency': data['ping'].get('latency',0),
                    'packetLoss': int(data.get('packetLoss', 0)),
                    # Byte to Megabit
                    'bandwidth_down': data['download'].get('bandwidth', 0) / 125000,
                    'bytes_down': data['download'].get('bytes', 0),
                    'elapsed_down': data['download']['elapsed'],
                    # Byte to Megabit
                    'bandwidth_up': data['upload'].get('bandwidth', 0) / 125000,
                    'bytes_up': data['upload'].get('bytes', 0),
                    'elapsed_up': data['upload']['elapsed']
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
            'vpn_enabled': (False if data['interface']['isVpn'] == 'false' else True),
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
            # split the tag string, strip and add selected tags to {options} with corresponding tag_switch data
            tag = tag.strip()
            options[tag] = tag_switch[tag]
        return options

    def process_data(self, data):
        data = self.format_data(data)
        self.write(data)


        

