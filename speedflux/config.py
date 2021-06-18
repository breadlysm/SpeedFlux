import os
import re

# import speedflux


_CONFIG_DEFAULTS = {
    'NAMESPACE': (str, 'Database', None),
    'DB_ADDRESS': (str, 'Database', 'influxdb'),
    'DB_PORT': (int, 'Database', 8086),
    'DB_USER': (str, 'Database', None),
    'DB_PASSWORD': (str, 'Database', None),
    'DB_DATABASE': (str, 'Database', 'speedtests'),
    'DB_TAGS': (str, 'Database', None),
    'TEST_INTERVAL': (int, 'SpeedTest', 180),
    'SERVER_ID': (str, 'SpeedTest', None),
    'PING_TARGETS': (str, 'PingTest', '1.1.1.1, 8.8.8.8'),
    'PING_INTERVAL': (int, 'PingTest', 120),
    'LOG_TYPE': (str, 'Logs', 'info'),
}


class Config:

    def get_setting(self, key):
        """ Cast any value in the config to the right type or use the default
        """
        key, definition_type, section, default = self._define(key)
        my_val = definition_type(os.getenv(key, default))
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
