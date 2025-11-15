"""
Prometheus Exporter Module

Exports health metrics in Prometheus format.
"""

from typing import Dict, Any, List
from loguru import logger
from prometheus_client import CollectorRegistry, Gauge, generate_latest


class PrometheusExporter:
    """
    Exports health metrics to Prometheus format.

    Provides metrics in Prometheus exposition format.
    """

    def __init__(self):
        """Initialize Prometheus exporter."""
        self.registry = CollectorRegistry()
        self._setup_metrics()

    def _setup_metrics(self):
        """Setup Prometheus metric gauges."""
        # System metrics
        self.system_status = Gauge(
            'redfish_system_status',
            'System health status (0=Unknown, 1=OK, 2=Warning, 3=Critical)',
            ['device', 'vendor', 'model'],
            registry=self.registry
        )

        # Thermal metrics
        self.temperature = Gauge(
            'redfish_temperature_celsius',
            'Temperature sensor reading in Celsius',
            ['device', 'vendor', 'sensor_name', 'location'],
            registry=self.registry
        )

        self.fan_speed = Gauge(
            'redfish_fan_speed_rpm',
            'Fan speed in RPM',
            ['device', 'vendor', 'fan_name', 'location'],
            registry=self.registry
        )

        # Power metrics
        self.power_consumption = Gauge(
            'redfish_power_consumption_watts',
            'Power consumption in watts',
            ['device', 'vendor', 'model'],
            registry=self.registry
        )

        self.power_capacity = Gauge(
            'redfish_power_capacity_watts',
            'Total power capacity in watts',
            ['device', 'vendor', 'model'],
            registry=self.registry
        )

        self.psu_status = Gauge(
            'redfish_psu_status',
            'Power supply status (0=Unknown, 1=OK, 2=Warning, 3=Critical)',
            ['device', 'vendor', 'psu_name'],
            registry=self.registry
        )

    def export(self, health_data: Dict[str, Any]) -> bytes:
        """
        Export health data to Prometheus format.

        Args:
            health_data: Health metrics from HealthChecker

        Returns:
            Prometheus metrics in exposition format
        """
        logger.info("Exporting metrics to Prometheus format")

        vendor_info = health_data.get("vendor_info", {})
        device_name = vendor_info.get("model", "Unknown")
        vendor = vendor_info.get("vendor", "Unknown")
        model = vendor_info.get("model", "Unknown")

        # Export system status
        system_health = health_data.get("system_health", {})
        status_value = self._status_to_value(system_health.get("status", "Unknown"))
        self.system_status.labels(device=device_name, vendor=vendor, model=model).set(status_value)

        # Export thermal metrics
        thermal_health = health_data.get("thermal_health", {})
        for temp in thermal_health.get("temperatures", []):
            sensor_name = temp.get("name", "Unknown")
            location = temp.get("location", "Unknown")
            reading = temp.get("reading_celsius", 0)

            if reading:
                self.temperature.labels(
                    device=device_name,
                    vendor=vendor,
                    sensor_name=sensor_name,
                    location=location
                ).set(reading)

        for fan in thermal_health.get("fans", []):
            fan_name = fan.get("name", "Unknown")
            location = fan.get("location", "Unknown")
            reading = fan.get("reading_rpm", 0)

            if reading:
                self.fan_speed.labels(
                    device=device_name,
                    vendor=vendor,
                    fan_name=fan_name,
                    location=location
                ).set(reading)

        # Export power metrics
        power_health = health_data.get("power_health", {})
        consumed = power_health.get("total_consumed_watts", 0)
        capacity = power_health.get("total_capacity_watts", 0)

        self.power_consumption.labels(device=device_name, vendor=vendor, model=model).set(consumed)
        self.power_capacity.labels(device=device_name, vendor=vendor, model=model).set(capacity)

        for psu in power_health.get("power_supplies", []):
            psu_name = psu.get("name", "Unknown")
            psu_status = self._status_to_value(psu.get("status", "Unknown"))
            self.psu_status.labels(
                device=device_name,
                vendor=vendor,
                psu_name=psu_name
            ).set(psu_status)

        # Generate Prometheus exposition format
        return generate_latest(self.registry)

    def _status_to_value(self, status: str) -> int:
        """Convert status string to numeric value."""
        status_map = {
            "OK": 1,
            "Warning": 2,
            "Critical": 3,
            "Unknown": 0
        }
        return status_map.get(status, 0)

    def export_to_file(self, health_data: Dict[str, Any], output_file: str):
        """
        Export metrics to file.

        Args:
            health_data: Health metrics from HealthChecker
            output_file: Output file path
        """
        metrics = self.export(health_data)

        with open(output_file, "wb") as f:
            f.write(metrics)

        logger.info(f"Prometheus metrics exported to {output_file}")
