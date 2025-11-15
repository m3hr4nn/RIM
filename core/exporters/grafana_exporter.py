"""
Grafana Exporter Module

Generates Grafana dashboards from health metrics.
"""

from typing import Dict, Any, List
from loguru import logger
import json
from datetime import datetime


class GrafanaExporter:
    """
    Exports health metrics to Grafana dashboard format.

    Generates JSON dashboards compatible with Grafana 8.0+
    """

    def __init__(self):
        """Initialize Grafana exporter."""
        self.dashboard_version = 1

    def export_dashboard(self, vendor: str, model: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Grafana dashboard JSON.

        Args:
            vendor: Vendor name
            model: Model name
            metrics: Metrics dictionary from health checker

        Returns:
            Grafana dashboard as dictionary
        """
        logger.info(f"Generating Grafana dashboard for {vendor} {model}")

        dashboard = {
            "dashboard": {
                "id": None,
                "uid": None,
                "title": f"RIM - {vendor} {model}",
                "tags": ["rim", "hardware", vendor.lower(), "redfish"],
                "timezone": "browser",
                "schemaVersion": 30,
                "version": self.dashboard_version,
                "refresh": "30s",
                "panels": []
            },
            "folderId": 0,
            "overwrite": False
        }

        # Add panels
        panel_id = 1
        y_position = 0

        # System status panel
        dashboard["dashboard"]["panels"].append(
            self._create_stat_panel(
                panel_id, "System Status", 0, y_position, 6, 4,
                "system_status"
            )
        )
        panel_id += 1

        # Temperature panel
        dashboard["dashboard"]["panels"].append(
            self._create_graph_panel(
                panel_id, "Temperatures", 6, y_position, 18, 8,
                "temp_*"
            )
        )
        panel_id += 1
        y_position += 8

        # Power consumption panel
        dashboard["dashboard"]["panels"].append(
            self._create_gauge_panel(
                panel_id, "Power Consumption", 0, y_position, 8, 6,
                "power_consumption"
            )
        )
        panel_id += 1

        # Fan speeds panel
        dashboard["dashboard"]["panels"].append(
            self._create_graph_panel(
                panel_id, "Fan Speeds", 8, y_position, 16, 6,
                "fan_*"
            )
        )

        return dashboard

    def _create_stat_panel(self, panel_id: int, title: str, x: int, y: int,
                          w: int, h: int, metric: str) -> Dict[str, Any]:
        """Create a stat panel."""
        return {
            "id": panel_id,
            "type": "stat",
            "title": title,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": metric,
                    "refId": "A"
                }
            ],
            "options": {
                "graphMode": "none",
                "colorMode": "value",
                "justifyMode": "auto",
                "textMode": "auto"
            },
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {"type": "value", "value": "1", "text": "OK"},
                        {"type": "value", "value": "2", "text": "Warning"},
                        {"type": "value", "value": "3", "text": "Critical"}
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "gray"},
                            {"value": 1, "color": "green"},
                            {"value": 2, "color": "yellow"},
                            {"value": 3, "color": "red"}
                        ]
                    }
                }
            }
        }

    def _create_graph_panel(self, panel_id: int, title: str, x: int, y: int,
                           w: int, h: int, metric: str) -> Dict[str, Any]:
        """Create a time-series graph panel."""
        return {
            "id": panel_id,
            "type": "graph",
            "title": title,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": metric,
                    "refId": "A"
                }
            ],
            "yaxes": [
                {
                    "format": "short",
                    "label": None,
                    "show": True
                },
                {
                    "format": "short",
                    "label": None,
                    "show": True
                }
            ],
            "lines": True,
            "fill": 1,
            "linewidth": 2,
            "points": False,
            "pointradius": 5
        }

    def _create_gauge_panel(self, panel_id: int, title: str, x: int, y: int,
                           w: int, h: int, metric: str) -> Dict[str, Any]:
        """Create a gauge panel."""
        return {
            "id": panel_id,
            "type": "gauge",
            "title": title,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [
                {
                    "expr": metric,
                    "refId": "A"
                }
            ],
            "options": {
                "showThresholdLabels": False,
                "showThresholdMarkers": True
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "watt",
                    "min": 0,
                    "max": 1000,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"value": 0, "color": "green"},
                            {"value": 500, "color": "yellow"},
                            {"value": 800, "color": "red"}
                        ]
                    }
                }
            }
        }

    def generate_from_health_data(self, health_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Generate dashboard from health check data.

        Args:
            health_data: Health metrics from HealthChecker
            output_file: Optional output file path

        Returns:
            Grafana dashboard JSON as string
        """
        vendor_info = health_data.get("vendor_info", {})
        vendor = vendor_info.get("vendor", "Unknown")
        model = vendor_info.get("model", "Unknown")

        dashboard = self.export_dashboard(vendor, model, health_data)
        dashboard_json = json.dumps(dashboard, indent=2)

        if output_file:
            with open(output_file, "w") as f:
                f.write(dashboard_json)
            logger.info(f"Grafana dashboard saved to {output_file}")

        return dashboard_json
