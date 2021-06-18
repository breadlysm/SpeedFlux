from speedflux import config, logs, influx

# Speedflux
CONFIG = None
DB_TYPE = None
LOG = None
INFLUXDB = None


def initialize():
    global CONFIG
    global LOG
    global INFLUXDB

    try:
        CONFIG = config.Config()
    except Exception as err:
        raise SystemExit("Unable to initialize SpeedFlux", err)
    try:
        LOG = logs.Log(CONFIG)
    except Exception as err:
        raise SystemExit("Couldn't initiate logging", err)
    try:
        INFLUXDB = influx.Influx(CONFIG)
    except Exception as err:
        raise SystemExit("Couldn't initiate InfluxDB <2", err)
