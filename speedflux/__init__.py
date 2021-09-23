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
        # print(CONFIG.INFLUX_TWO_ADDRESS)
    except Exception as err:
        raise SystemExit("Couldn't initiate logging", err)
    if CONFIG.USE_INFLUX_ONE:
        try:
            INFLUXDB = influx.Influx1()
        except Exception as err:
            raise SystemExit("Couldn't initiate InfluxDB <2", err)
    elif CONFIG.USE_INFLUX_TWO:
        try:
            INFLUXDB = influx.Influx2()
        except Exception as err:
            raise SystemExit("Couldn't initiate InfluxDB 2+", err)
    else:
        raise SystemExit("You must setup a Bool ENV specifying Influx"
                         " USE_INFLUX_ONE or USE_INFLUX_TWO")
