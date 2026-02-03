import os
import re

# import speedflux


_CONFIG_DEFAULTS = {
    # General settings
    'NAMESPACE': (str, 'Database', None),

    # Backend selection - comma-separated list: influxdb,victoriametrics,prometheus
    # Default: influxdb (for backward compatibility)
    'SPEEDFLUX_BACKENDS': (str, 'Database', 'influxdb'),

    # InfluxDB settings (original - kept for backward compatibility)
    'INFLUX_DB_ADDRESS': (str, 'Database', 'influxdb'),
    'INFLUX_DB_PORT': (int, 'Database', 8086),
    'INFLUX_DB_USER': (str, 'Database', None),
    'INFLUX_DB_PASSWORD': (str, 'Database', None),
    'INFLUX_DB_DATABASE': (str, 'Database', 'speedtests'),
    'INFLUX_DB_TAGS': (str, 'Database', None),

    # VictoriaMetrics settings
    'VICTORIAMETRICS_ADDRESS': (str, 'Database', 'victoriametrics'),
    'VICTORIAMETRICS_PORT': (int, 'Database', 8428),
    'VICTORIAMETRICS_DATABASE': (str, 'Database', 'speedtests'),

    # Prometheus settings
    'PROMETHEUS_PORT': (int, 'Database', 9091),

    # SpeedTest settings
    'SPEEDTEST_INTERVAL': (int, 'SpeedTest', 180),
    # Comma-separated list of server IDs to rotate through
    'SPEEDTEST_SERVER_ID': (str, 'SpeedTest', None),
    # Country code to filter servers (e.g., 'US', 'GB', 'DE')
    'SPEEDTEST_COUNTRY': (str, 'SpeedTest', None),

    # Ping settings
    'PING_TARGETS': (str, 'PingTest', '1.1.1.1, 8.8.8.8'),
    'PING_INTERVAL': (int, 'PingTest', 120),

    # Logging
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
