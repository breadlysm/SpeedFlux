"""Base interface for all database backends."""
from abc import ABC, abstractmethod


class BaseBackend(ABC):
    """Abstract base class for database backends.

    All database backends must implement these methods to ensure
    consistent behavior across InfluxDB, VictoriaMetrics, Prometheus, etc.
    """

    def __init__(self, config):
        self.config = config
        self.retries = 0
        self.max_retries = 3
        self.initialized = False

    @abstractmethod
    def init_db(self):
        """Initialize the database connection.

        Should handle connection setup and any necessary database/bucket creation.
        """
        pass

    @abstractmethod
    def write(self, data, data_type='Speedtest'):
        """Write data points to the database.

        Args:
            data: Formatted data points to write
            data_type: Type of data being written (for logging)
        """
        pass

    @abstractmethod
    def format_data(self, data):
        """Format raw speedtest data for this backend.

        Args:
            data: Raw speedtest JSON data

        Returns:
            Formatted data ready for writing
        """
        pass

    def process_data(self, data):
        """Process and write speedtest data.

        Args:
            data: Raw speedtest JSON data
        """
        formatted_data = self.format_data(data)
        self.write(formatted_data)

    def tag_selection(self, data):
        """Select tags based on configuration.

        Args:
            data: Raw speedtest JSON data

        Returns:
            Dictionary of selected tags
        """
        tags = self.config.INFLUX_DB_TAGS
        options = {}

        tag_switch = {
            'namespace': self.config.NAMESPACE,
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
            tag = tag.strip()
            options[tag] = tag_switch[tag]
        return options

    @property
    def name(self):
        """Return the backend name for logging."""
        return self.__class__.__name__
