import os


def get_config():
    NAMESPACE = os.getenv('NAMESPACE', 'None')
    DB_ADDRESS = os.getenv('INFLUX_DB_ADDRESS', 'influxdb')
    DB_PORT = int(os.getenv('INFLUX_DB_PORT', '8086'))
    DB_USER = os.getenv('INFLUX_DB_USER', '')
    DB_PASSWORD = os.getenv('INFLUX_DB_PASSWORD', '')
    DB_DATABASE = os.getenv('INFLUX_DB_DATABASE', 'speedtests')
    DB_TAGS = os.getenv('INFLUX_DB_TAGS', None)
    PING_TARGETS = os.getenv('PING_TARGETS', '1.1.1.1, 8.8.8.8')
    # Speedtest Settings
    # Time between tests (in minutes, converts to seconds).
    TEST_INTERVAL = int(os.getenv('SPEEDTEST_INTERVAL', '180')) * 60
    # Specific server ID
    SERVER_ID = os.getenv('SPEEDTEST_SERVER_ID', '')
    # Time between ping tests (in seconds).
    PING_INTERVAL = int(os.getenv('PING_INTERVAL', '120'))
    LOG_TYPE = os.getenv('LOG_TYPE', 'info')
    config = {
        'namespace': NAMESPACE,
        'db_host': DB_ADDRESS,
        'db_port': DB_PORT,
        'db_user': DB_USER,
        'db_pass': DB_PASSWORD,
        'db_tags': DB_TAGS,
        'db_name': DB_DATABASE,
        'ping_targets': PING_TARGETS,
        'test_interval': TEST_INTERVAL,
        'ping_interval': PING_INTERVAL,
        'server_id': SERVER_ID,
        'log_level': LOG_TYPE
    }
    return config
