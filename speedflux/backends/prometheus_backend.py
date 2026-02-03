"""Prometheus backend for SpeedFlux.

Exposes metrics via HTTP endpoint for Prometheus to scrape.
Uses the prometheus_client library to manage metrics and serve them.
"""
import threading

from prometheus_client import Gauge, CollectorRegistry, start_http_server, REGISTRY

import speedflux
from .base import BaseBackend


class PrometheusBackend(BaseBackend):
    """Prometheus metrics backend.

    Exposes speedtest and ping metrics via HTTP endpoint for Prometheus scraping.
    """

    def __init__(self, config):
        super().__init__(config)

        # Use a custom registry to avoid conflicts
        self.registry = REGISTRY

        # Define all metrics with labels for tags
        self._define_metrics()

        # Start the metrics server
        self.init_db()

    def _define_metrics(self):
        """Define all Prometheus metrics."""
        # Common labels that can be applied
        common_labels = ['namespace', 'isp', 'server_name', 'server_location']

        # Ping metrics
        self.ping_latency = Gauge(
            'speedflux_ping_latency_ms',
            'Ping latency in milliseconds',
            common_labels,
            registry=self.registry
        )
        self.ping_jitter = Gauge(
            'speedflux_ping_jitter_ms',
            'Ping jitter in milliseconds',
            common_labels,
            registry=self.registry
        )

        # Download metrics
        self.download_bandwidth = Gauge(
            'speedflux_download_bandwidth_mbps',
            'Download bandwidth in Megabits per second',
            common_labels,
            registry=self.registry
        )
        self.download_bytes = Gauge(
            'speedflux_download_bytes_total',
            'Total bytes downloaded during test',
            common_labels,
            registry=self.registry
        )
        self.download_elapsed = Gauge(
            'speedflux_download_elapsed_ms',
            'Download test duration in milliseconds',
            common_labels,
            registry=self.registry
        )

        # Upload metrics
        self.upload_bandwidth = Gauge(
            'speedflux_upload_bandwidth_mbps',
            'Upload bandwidth in Megabits per second',
            common_labels,
            registry=self.registry
        )
        self.upload_bytes = Gauge(
            'speedflux_upload_bytes_total',
            'Total bytes uploaded during test',
            common_labels,
            registry=self.registry
        )
        self.upload_elapsed = Gauge(
            'speedflux_upload_elapsed_ms',
            'Upload test duration in milliseconds',
            common_labels,
            registry=self.registry
        )

        # Packet loss
        self.packet_loss = Gauge(
            'speedflux_packet_loss_percent',
            'Packet loss percentage',
            common_labels,
            registry=self.registry
        )

        # Ping test metrics (separate from speedtest ping)
        self.ping_success = Gauge(
            'speedflux_ping_success',
            'Ping test success (1) or failure (0)',
            ['namespace', 'target'],
            registry=self.registry
        )
        self.ping_rtt = Gauge(
            'speedflux_ping_rtt_ms',
            'Ping round-trip time in milliseconds',
            ['namespace', 'target'],
            registry=self.registry
        )

    def init_db(self):
        """Start the Prometheus metrics HTTP server."""
        try:
            port = self.config.PROMETHEUS_PORT
            speedflux.LOG.info(f"Starting Prometheus metrics server on port {port}")

            # Start HTTP server in a daemon thread
            start_http_server(port)

            speedflux.LOG.info(f"Prometheus metrics available at http://0.0.0.0:{port}/metrics")
            self.initialized = True

        except Exception as err:
            speedflux.LOG.error(f"Failed to start Prometheus metrics server: {err}")
            if self.retries < self.max_retries:
                self.retries += 1
                speedflux.LOG.error(f"Retry {self.retries}: Starting Prometheus server.")
                self.init_db()

    def format_data(self, data):
        """Format data for Prometheus metrics.

        Returns the raw data with extracted tags - actual metric updates
        happen in write().
        """
        tags = self.tag_selection(data)
        return {
            'tags': tags,
            'data': data
        }

    def _get_label_values(self, tags):
        """Extract label values from tags in correct order."""
        return [
            str(tags.get('namespace', '')),
            str(tags.get('isp', '')),
            str(tags.get('server_name', '')),
            str(tags.get('server_location', ''))
        ]

    def write(self, data, data_type='Speedtest'):
        """Update Prometheus metrics with new data."""
        try:
            if data_type == 'Ping':
                # Handle ping test data
                self._write_ping_data(data)
            else:
                # Handle speedtest data
                self._write_speedtest_data(data)

            speedflux.LOG.info(f"{data_type} metrics updated for Prometheus")
            self.retries = 0

        except Exception as err:
            speedflux.LOG.error(f"Prometheus metrics update error: {err}")

    def _write_speedtest_data(self, formatted_data):
        """Update speedtest metrics."""
        tags = formatted_data['tags']
        data = formatted_data['data']
        labels = self._get_label_values(tags)

        # Update ping metrics
        self.ping_latency.labels(*labels).set(data['ping'].get('latency', 0))
        self.ping_jitter.labels(*labels).set(data['ping'].get('jitter', 0))

        # Update download metrics
        self.download_bandwidth.labels(*labels).set(
            data['download'].get('bandwidth', 0) / 125000)
        self.download_bytes.labels(*labels).set(
            data['download'].get('bytes', 0))
        self.download_elapsed.labels(*labels).set(
            data['download'].get('elapsed', 0))

        # Update upload metrics
        self.upload_bandwidth.labels(*labels).set(
            data['upload'].get('bandwidth', 0) / 125000)
        self.upload_bytes.labels(*labels).set(
            data['upload'].get('bytes', 0))
        self.upload_elapsed.labels(*labels).set(
            data['upload'].get('elapsed', 0))

        # Update packet loss
        self.packet_loss.labels(*labels).set(int(data.get('packetLoss', 0)))

    def _write_ping_data(self, data):
        """Update ping test metrics."""
        measurement = data[0]
        tags = measurement.get('tags', {})
        namespace = str(tags.get('namespace', ''))
        target = str(tags.get('target', ''))

        self.ping_success.labels(namespace, target).set(
            measurement['fields']['success'])
        self.ping_rtt.labels(namespace, target).set(
            measurement['fields']['rtt'])

    def write_ping(self, data):
        """Write ping data - wrapper for compatibility."""
        self.write(data, data_type='Ping')
