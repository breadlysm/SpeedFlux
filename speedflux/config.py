import os
import re

# import speedflux


_CONFIG_DEFAULTS = {
    'NAMESPACE': (str, 'Influx DB', None),
    'INFLUX_DB_ADDRESS': (str, 'Influx DB', 'influxdb'),
    'INFLUX_DB_PORT': (int, 'Influx DB', 8086),
    'INFLUX_DB_USER': (str, 'Influx DB', None),
    'INFLUX_DB_PASSWORD': (str, 'Influx DB', None),
    'INFLUX_DB_DATABASE': (str, 'Influx DB', 'speedtests'),
    'INFLUX_DB_TAGS': (str, 'Influx DB', None),
    'SPEEDTEST_INTERVAL': (int, 'SpeedTest', 180),
    'SPEEDTEST_SERVER_ID': (str, 'SpeedTest', None),
    'PING_TARGETS': (str, 'PingTest', '1.1.1.1, 8.8.8.8'),
    'PING_INTERVAL': (int, 'PingTest', 120),
    'LOG_TYPE': (str, 'General', 'info'),
    'USE_INFLUX_ONE': (bool, 'General', True),
    'USE_INFLUX_TWO': (bool, 'General', False),
    'INFLUX_TWO_TOKEN': (str, 'Influx DB', None),
    'INFLUX_TWO_ORG': (str, 'Influx DB', 'SpeedTest'),
    'INFLUX_TWO_BUCKET': (str, 'Influx DB', 'speedtests'),
    'INFLUX_TWO_ADDRESS': (str, 'Influx DB', 'influxdb2'),
    'INFLUX_TWO_PORT': (int, 'Influx DB', 8086),
    'INFLUX_TWO_USER': (str, 'Influx DB', None),
    'INFLUX_TWO_PASSWORD': (str, 'Influx DB', None)
}


class Config:

    def get_setting(self, key):
        """ Cast any value in the config to the right type or use the default
        """
        key, definition_type, section, default = self._define(key)
        if definition_type == bool:
            my_val = os.getenv(key, default)
            if isinstance(my_val, bool):
                return my_val
            else:
                return my_val.lower() == 'true'
        my_val = definition_type(os.getenv(key, default))
        if my_val == 'None' and not default:
            my_val = None
        return my_val

    def _define(self, name):
        key = name.upper()
        definition = _CONFIG_DEFAULTS[key]
        if len(definition) == 3:
            definition_type, section, default = definition
        else:
            definition_type, section, _, default = definition
        return key, definition_type, section, default

    def __getattr__(self, name):
        """
        Retrieves config value for the setting
        """
        if not re.match(r'[A-Z_]+$', name):
            return super(Config, self).__getattr__(name)
        else:
            return self.get_setting(name)
