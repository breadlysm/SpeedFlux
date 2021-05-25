from influxdb import InfluxDBClient
from speedflux import log

class Influx:
    def __init__(self, config):
        self.client = InfluxDBClient(config['db_host'] , config['db_port'], config['db_user'], config['db_pass'], None)

    def init_db():
        databases = influxdb_client.get_list_database()

        if len(list(filter(lambda x: x['name'] == DB_DATABASE, databases))) == 0:
            influxdb_client.create_database(
                DB_DATABASE)  # Create if does not exist.
        else:
            # Switch to if does exist.
            influxdb_client.switch_database(DB_DATABASE)

    def format_data(self, data):
        # There is additional data in the speedtest-cli output but it is likely not necessary to store.
        influx_data = [
            {
                'measurement': 'ping',
                'time': data['timestamp'],
                'fields': {
                    'jitter': data['ping']['jitter'],
                    'latency': data['ping']['latency']
                }
            },
            {
                'measurement': 'download',
                'time': data['timestamp'],
                'fields': {
                    # Byte to Megabit
                    'bandwidth': data['download']['bandwidth'] / 125000,
                    'bytes': data['download']['bytes'],
                    'elapsed': data['download']['elapsed']
                }
            },
            {
                'measurement': 'upload',
                'time': data['timestamp'],
                'fields': {
                    # Byte to Megabit
                    'bandwidth': data['upload']['bandwidth'] / 125000,
                    'bytes': data['upload']['bytes'],
                    'elapsed': data['upload']['elapsed']
                }
            },
            {
                'measurement': 'packetLoss',
                'time': data['timestamp'],
                'fields': {
                    'packetLoss': pkt_loss(data)
                }
            },
            {
                'measurement': 'speeds',
                'time': data['timestamp'],
                'fields': {
                    'jitter': data['ping']['jitter'],
                    'latency': data['ping']['latency'],
                    'packetLoss': pkt_loss(data),
                    # Byte to Megabit
                    'bandwidth_down': data['download']['bandwidth'] / 125000,
                    'bytes_down': data['download']['bytes'],
                    'elapsed_down': data['download']['elapsed'],
                    # Byte to Megabit
                    'bandwidth_up': data['upload']['bandwidth'] / 125000,
                    'bytes_up': data['upload']['bytes'],
                    'elapsed_up': data['upload']['elapsed']
                }
            }
        ]
        tags = tag_selection(data)
        if tags is not None:
            for measurement in influx_data:
                measurement['tags'] = tags

        return influx_data
    
    def write(self, data):
        try:
           if self.client.write_points(data):
               log.info("Data written successfully")
               log.debug(F"Wrote `{data}` to Influx")
            else:
                raise Exception("Write points did not complete")
        except Exception as err:
            log.info(F"{err}")
            log.debug(F"Wrote `{data}` to Influx")
    
    def tag_selection(data):
        tags = DB_TAGS
        options = {}

        # tag_switch takes in _data and attaches CLIoutput to more readable ids
        tag_switch = {
            'namespace': NAMESPACE,
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


        

