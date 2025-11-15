"""
CSV Exporter Module

Exports health metrics to CSV format for Grafana import.
"""

import csv
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
from io import StringIO


class CSVExporter:
    """
    Exports health metrics to CSV format.

    Formats data for easy import into Grafana using CSV datasource plugin.
    """

    def __init__(self):
        """Initialize CSV exporter."""
        self.data_rows: List[Dict[str, Any]] = []

    def export(self, health_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Export health data to CSV format.

        Args:
            health_data: Health metrics dictionary
            output_file: Optional output file path

        Returns:
            CSV content as string
        """
        logger.info("Exporting health data to CSV")

        self.data_rows = []
        timestamp = health_data.get("timestamp", datetime.utcnow().isoformat() + "Z")
        vendor_info = health_data.get("vendor_info", {})

        device_name = vendor_info.get("model", "Unknown")
        vendor = vendor_info.get("vendor", "Unknown")

        # Export system metrics
        self._export_system_metrics(timestamp, device_name, vendor, health_data.get("system_health", {}))

        # Export thermal metrics
        self._export_thermal_metrics(timestamp, device_name, vendor, health_data.get("thermal_health", {}))

        # Export power metrics
        self._export_power_metrics(timestamp, device_name, vendor, health_data.get("power_health", {}))

        # Export storage metrics
        self._export_storage_metrics(timestamp, device_name, vendor, health_data.get("storage_health", {}))

        # Create DataFrame
        df = pd.DataFrame(self.data_rows)

        # Reorder columns
        column_order = ["timestamp", "device_name", "device_type", "vendor",
                       "metric_name", "value", "unit", "status"]
        df = df[column_order]

        # Convert to CSV
        if output_file:
            df.to_csv(output_file, index=False)
            logger.info(f"CSV exported to {output_file}")

        csv_content = df.to_csv(index=False)
        return csv_content

    def _export_system_metrics(self, timestamp: str, device_name: str,
                               vendor: str, system_health: Dict[str, Any]):
        """Export system-level metrics to CSV rows."""
        if not system_health or "error" in system_health:
            return

        self._add_row(timestamp, device_name, "server", vendor,
                     "system_status", self._status_to_value(system_health.get("status")),
                     "status", system_health.get("status"))

        self._add_row(timestamp, device_name, "server", vendor,
                     "power_state", self._power_state_to_value(system_health.get("power_state")),
                     "status", system_health.get("power_state"))

        self._add_row(timestamp, device_name, "server", vendor,
                     "processor_count", system_health.get("processor_count", 0),
                     "count", "OK")

        self._add_row(timestamp, device_name, "server", vendor,
                     "memory_total_gb", system_health.get("memory_total_gb", 0),
                     "gigabytes", "OK")

    def _export_thermal_metrics(self, timestamp: str, device_name: str,
                                vendor: str, thermal_health: Dict[str, Any]):
        """Export thermal metrics to CSV rows."""
        if not thermal_health or "error" in thermal_health:
            return

        # Export temperature sensors
        for temp in thermal_health.get("temperatures", []):
            metric_name = f"temp_{self._sanitize_name(temp['name'])}"
            self._add_row(timestamp, device_name, "server", vendor,
                         metric_name, temp.get("reading_celsius"),
                         "celsius", temp.get("status"))

            # Add threshold metrics
            if temp.get("upper_threshold_critical"):
                self._add_row(timestamp, device_name, "server", vendor,
                             f"{metric_name}_threshold_critical",
                             temp["upper_threshold_critical"],
                             "celsius", "OK")

        # Export fans
        for fan in thermal_health.get("fans", []):
            metric_name = f"fan_{self._sanitize_name(fan['name'])}"
            self._add_row(timestamp, device_name, "server", vendor,
                         metric_name, fan.get("reading_rpm"),
                         "rpm", fan.get("status"))

    def _export_power_metrics(self, timestamp: str, device_name: str,
                             vendor: str, power_health: Dict[str, Any]):
        """Export power metrics to CSV rows."""
        if not power_health or "error" in power_health:
            return

        # Total power consumption
        self._add_row(timestamp, device_name, "server", vendor,
                     "power_consumption", power_health.get("total_consumed_watts"),
                     "watts", power_health.get("status"))

        # Total capacity
        self._add_row(timestamp, device_name, "server", vendor,
                     "power_capacity", power_health.get("total_capacity_watts"),
                     "watts", "OK")

        # Utilization
        self._add_row(timestamp, device_name, "server", vendor,
                     "power_utilization", power_health.get("utilization_percent"),
                     "percent", power_health.get("status"))

        # Individual PSU status
        for i, psu in enumerate(power_health.get("power_supplies", [])):
            psu_name = f"psu{i+1}"
            self._add_row(timestamp, device_name, "server", vendor,
                         f"{psu_name}_status",
                         self._status_to_value(psu.get("status")),
                         "status", psu.get("status"))

            if psu.get("capacity_watts"):
                self._add_row(timestamp, device_name, "server", vendor,
                             f"{psu_name}_capacity",
                             psu["capacity_watts"],
                             "watts", "OK")

    def _export_storage_metrics(self, timestamp: str, device_name: str,
                               vendor: str, storage_health: Dict[str, Any]):
        """Export storage metrics to CSV rows."""
        if not storage_health or "error" in storage_health:
            return

        # Storage status
        self._add_row(timestamp, device_name, "server", vendor,
                     "storage_status",
                     self._status_to_value(storage_health.get("status")),
                     "status", storage_health.get("status"))

    def _add_row(self, timestamp: str, device_name: str, device_type: str,
                vendor: str, metric_name: str, value: Any, unit: str, status: str):
        """Add a row to the CSV data."""
        self.data_rows.append({
            "timestamp": timestamp,
            "device_name": device_name,
            "device_type": device_type,
            "vendor": vendor,
            "metric_name": metric_name,
            "value": value if value is not None else 0,
            "unit": unit,
            "status": status
        })

    def _status_to_value(self, status: str) -> int:
        """Convert status string to numeric value."""
        status_map = {
            "OK": 1,
            "Warning": 2,
            "Critical": 3,
            "Unknown": 0
        }
        return status_map.get(status, 0)

    def _power_state_to_value(self, power_state: str) -> int:
        """Convert power state to numeric value."""
        power_map = {
            "On": 1,
            "Off": 0,
            "PoweringOn": 1,
            "PoweringOff": 0
        }
        return power_map.get(power_state, 0)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize metric name for CSV."""
        return name.lower().replace(" ", "_").replace("-", "_").replace(".", "_")

    def export_template(self, vendor: str, model: str, output_file: str = None) -> str:
        """
        Export a CSV template for a specific vendor/model.

        Args:
            vendor: Vendor name
            model: Model name
            output_file: Optional output file path

        Returns:
            CSV template as string
        """
        logger.info(f"Generating CSV template for {vendor} {model}")

        template_rows = [
            {
                "timestamp": "2025-11-15T10:00:00Z",
                "device_name": f"example-{model.lower().replace(' ', '-')}",
                "device_type": "server",
                "vendor": vendor,
                "metric_name": "cpu_temperature",
                "value": 45,
                "unit": "celsius",
                "status": "OK"
            },
            {
                "timestamp": "2025-11-15T10:00:00Z",
                "device_name": f"example-{model.lower().replace(' ', '-')}",
                "device_type": "server",
                "vendor": vendor,
                "metric_name": "fan_speed",
                "value": 3500,
                "unit": "rpm",
                "status": "OK"
            },
            {
                "timestamp": "2025-11-15T10:00:00Z",
                "device_name": f"example-{model.lower().replace(' ', '-')}",
                "device_type": "server",
                "vendor": vendor,
                "metric_name": "power_consumption",
                "value": 450,
                "unit": "watts",
                "status": "OK"
            }
        ]

        df = pd.DataFrame(template_rows)

        if output_file:
            df.to_csv(output_file, index=False)
            logger.info(f"CSV template exported to {output_file}")

        return df.to_csv(index=False)
