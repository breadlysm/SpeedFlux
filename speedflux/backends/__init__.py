"""SpeedFlux database backends.

Supports multiple database backends:
- InfluxDB 1.x (original)
- VictoriaMetrics (using InfluxDB line protocol)
- Prometheus (exposes /metrics endpoint)
"""
from .base import BaseBackend
from .influxdb_backend import InfluxDBBackend
from .victoriametrics_backend import VictoriaMetricsBackend
from .prometheus_backend import PrometheusBackend

__all__ = [
    'BaseBackend',
    'InfluxDBBackend',
    'VictoriaMetricsBackend',
    'PrometheusBackend',
]
