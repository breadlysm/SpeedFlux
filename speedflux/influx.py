"""Legacy InfluxDB module - maintained for backward compatibility.

This module re-exports the InfluxDBBackend class as 'Influx' to maintain
backward compatibility with existing code that imports from speedflux.influx.
"""
from speedflux.backends.influxdb_backend import InfluxDBBackend

# Alias for backward compatibility
Influx = InfluxDBBackend
