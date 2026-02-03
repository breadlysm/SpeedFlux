from speedflux import config, logs

# Speedflux globals
CONFIG = None
LOG = None

# Legacy global for backward compatibility
INFLUXDB = None

# New multi-backend support
BACKENDS = []


def initialize():
    global CONFIG
    global LOG
    global INFLUXDB
    global BACKENDS

    try:
        CONFIG = config.Config()
    except Exception as err:
        raise SystemExit("Unable to initialize SpeedFlux", err)

    try:
        LOG = logs.Log(CONFIG)
    except Exception as err:
        raise SystemExit("Couldn't initiate logging", err)

    # Initialize backends based on configuration
    _initialize_backends()


def _initialize_backends():
    """Initialize all configured database backends."""
    global INFLUXDB
    global BACKENDS

    from speedflux.backends import (
        InfluxDBBackend,
        VictoriaMetricsBackend,
        PrometheusBackend
    )

    backends_str = CONFIG.SPEEDFLUX_BACKENDS
    if backends_str is None:
        backends_str = 'influxdb'

    backend_names = [b.strip().lower() for b in backends_str.split(',')]
    LOG.info(f"Initializing backends: {backend_names}")

    for backend_name in backend_names:
        try:
            if backend_name == 'influxdb':
                backend = InfluxDBBackend(CONFIG)
                BACKENDS.append(backend)
                # Set legacy global for backward compatibility
                INFLUXDB = backend
                LOG.info("InfluxDB backend initialized")

            elif backend_name == 'victoriametrics':
                backend = VictoriaMetricsBackend(CONFIG)
                BACKENDS.append(backend)
                LOG.info("VictoriaMetrics backend initialized")

            elif backend_name == 'prometheus':
                backend = PrometheusBackend(CONFIG)
                BACKENDS.append(backend)
                LOG.info("Prometheus backend initialized")

            else:
                LOG.warning(f"Unknown backend '{backend_name}' - skipping")

        except Exception as err:
            LOG.error(f"Failed to initialize {backend_name} backend: {err}")
            raise SystemExit(f"Couldn't initiate {backend_name}", err)

    if not BACKENDS:
        raise SystemExit("No backends were successfully initialized")

    # If InfluxDB is not in the list but INFLUXDB is expected by legacy code,
    # set it to the first backend for compatibility
    if INFLUXDB is None and BACKENDS:
        INFLUXDB = BACKENDS[0]
