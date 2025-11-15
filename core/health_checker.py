"""
Health Checker Module

Orchestrates health checks across different infrastructure components.
"""

from typing import Dict, List, Any, Optional
from loguru import logger
from .redfish_client import RedfishClient


class HealthStatus:
    """Health status constants."""
    OK = "OK"
    WARNING = "Warning"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"


class HealthChecker:
    """
    Orchestrates health checks for infrastructure devices.

    Collects and analyzes health metrics from Redfish endpoints.
    """

    def __init__(self, client: RedfishClient):
        """
        Initialize health checker.

        Args:
            client: Initialized RedfishClient instance
        """
        self.client = client
        self.health_data: Dict[str, Any] = {}

    def check_overall_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Dictionary containing all health metrics
        """
        logger.info("Starting comprehensive health check")

        self.health_data = {
            "timestamp": self._get_timestamp(),
            "vendor_info": self.client.get_vendor_info(),
            "system_health": self.check_system_health(),
            "thermal_health": self.check_thermal_health(),
            "power_health": self.check_power_health(),
            "storage_health": self.check_storage_health(),
            "overall_status": HealthStatus.UNKNOWN
        }

        # Determine overall status
        self.health_data["overall_status"] = self._calculate_overall_status()

        logger.info(f"Health check complete. Status: {self.health_data['overall_status']}")
        return self.health_data

    def check_system_health(self) -> Dict[str, Any]:
        """
        Check system-level health.

        Returns:
            System health metrics
        """
        logger.debug("Checking system health")

        system_info = self.client.get_system_info()
        if not system_info:
            return {"status": HealthStatus.UNKNOWN, "error": "Unable to retrieve system info"}

        status = system_info.get("Status", {})

        return {
            "status": self._map_status(status),
            "state": status.get("State", "Unknown"),
            "health": status.get("Health", "Unknown"),
            "power_state": system_info.get("PowerState", "Unknown"),
            "processor_count": system_info.get("ProcessorSummary", {}).get("Count", 0),
            "memory_total_gb": system_info.get("MemorySummary", {}).get("TotalSystemMemoryGiB", 0),
            "boot_source": system_info.get("Boot", {}).get("BootSourceOverrideTarget", "Unknown")
        }

    def check_thermal_health(self) -> Dict[str, Any]:
        """
        Check thermal health (temperatures and fans).

        Returns:
            Thermal health metrics
        """
        logger.debug("Checking thermal health")

        thermal_data = self.client.get_thermal()
        if not thermal_data:
            return {"status": HealthStatus.UNKNOWN, "error": "Unable to retrieve thermal data"}

        temperatures = []
        fans = []
        thermal_status = HealthStatus.OK

        # Process temperature sensors
        for temp in thermal_data.get("Temperatures", []):
            status = temp.get("Status", {})
            health = status.get("Health", "OK")

            temp_info = {
                "name": temp.get("Name", "Unknown"),
                "reading_celsius": temp.get("ReadingCelsius"),
                "upper_threshold_critical": temp.get("UpperThresholdCritical"),
                "upper_threshold_fatal": temp.get("UpperThresholdFatal"),
                "status": self._map_status(status),
                "health": health
            }
            temperatures.append(temp_info)

            if health == "Critical":
                thermal_status = HealthStatus.CRITICAL
            elif health == "Warning" and thermal_status != HealthStatus.CRITICAL:
                thermal_status = HealthStatus.WARNING

        # Process fans
        for fan in thermal_data.get("Fans", []):
            status = fan.get("Status", {})
            health = status.get("Health", "OK")

            fan_info = {
                "name": fan.get("Name", "Unknown"),
                "reading_rpm": fan.get("Reading"),
                "min_reading_rpm": fan.get("MinReadingRange"),
                "max_reading_rpm": fan.get("MaxReadingRange"),
                "status": self._map_status(status),
                "health": health
            }
            fans.append(fan_info)

            if health == "Critical":
                thermal_status = HealthStatus.CRITICAL
            elif health == "Warning" and thermal_status != HealthStatus.CRITICAL:
                thermal_status = HealthStatus.WARNING

        return {
            "status": thermal_status,
            "temperatures": temperatures,
            "fans": fans,
            "temperature_count": len(temperatures),
            "fan_count": len(fans)
        }

    def check_power_health(self) -> Dict[str, Any]:
        """
        Check power health.

        Returns:
            Power health metrics
        """
        logger.debug("Checking power health")

        power_data = self.client.get_power()
        if not power_data:
            return {"status": HealthStatus.UNKNOWN, "error": "Unable to retrieve power data"}

        power_supplies = []
        power_status = HealthStatus.OK
        total_consumed = 0
        total_capacity = 0

        # Process power supplies
        for psu in power_data.get("PowerSupplies", []):
            status = psu.get("Status", {})
            health = status.get("Health", "OK")

            psu_info = {
                "name": psu.get("Name", "Unknown"),
                "model": psu.get("Model", "Unknown"),
                "manufacturer": psu.get("Manufacturer", "Unknown"),
                "serial_number": psu.get("SerialNumber", "Unknown"),
                "capacity_watts": psu.get("PowerCapacityWatts", 0),
                "input_voltage": psu.get("LineInputVoltage"),
                "output_voltage": psu.get("OutputVoltage"),
                "status": self._map_status(status),
                "health": health
            }
            power_supplies.append(psu_info)

            if psu.get("PowerCapacityWatts"):
                total_capacity += psu["PowerCapacityWatts"]

            if health == "Critical":
                power_status = HealthStatus.CRITICAL
            elif health == "Warning" and power_status != HealthStatus.CRITICAL:
                power_status = HealthStatus.WARNING

        # Process power control/consumption
        power_control = power_data.get("PowerControl", [])
        if power_control:
            total_consumed = power_control[0].get("PowerConsumedWatts", 0)

        return {
            "status": power_status,
            "power_supplies": power_supplies,
            "supply_count": len(power_supplies),
            "total_consumed_watts": total_consumed,
            "total_capacity_watts": total_capacity,
            "utilization_percent": round((total_consumed / total_capacity * 100), 2) if total_capacity > 0 else 0
        }

    def check_storage_health(self) -> Dict[str, Any]:
        """
        Check storage health.

        Returns:
            Storage health metrics
        """
        logger.debug("Checking storage health")

        storage_data = self.client.get_storage()
        if not storage_data:
            return {"status": HealthStatus.UNKNOWN, "error": "Unable to retrieve storage data"}

        # Storage checking logic will be vendor-specific
        # This is a basic implementation
        return {
            "status": HealthStatus.OK,
            "controllers": [],
            "drives": [],
            "message": "Storage health check requires vendor-specific implementation"
        }

    def _map_status(self, status_obj: Dict[str, str]) -> str:
        """
        Map Redfish status to our health status.

        Args:
            status_obj: Status object from Redfish

        Returns:
            Normalized health status
        """
        if not status_obj:
            return HealthStatus.UNKNOWN

        health = status_obj.get("Health", "").lower()
        state = status_obj.get("State", "").lower()

        if health == "critical" or state == "disabled":
            return HealthStatus.CRITICAL
        elif health == "warning":
            return HealthStatus.WARNING
        elif health == "ok" and state in ["enabled", "standbyoffline", "unavailableoffline"]:
            return HealthStatus.OK
        else:
            return HealthStatus.UNKNOWN

    def _calculate_overall_status(self) -> str:
        """
        Calculate overall health status from all components.

        Returns:
            Overall health status
        """
        statuses = [
            self.health_data.get("system_health", {}).get("status", HealthStatus.UNKNOWN),
            self.health_data.get("thermal_health", {}).get("status", HealthStatus.UNKNOWN),
            self.health_data.get("power_health", {}).get("status", HealthStatus.UNKNOWN),
            self.health_data.get("storage_health", {}).get("status", HealthStatus.UNKNOWN)
        ]

        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(s == HealthStatus.OK for s in statuses):
            return HealthStatus.OK
        else:
            return HealthStatus.UNKNOWN

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def export_metrics(self) -> Dict[str, Any]:
        """
        Export collected health metrics in a standardized format.

        Returns:
            Formatted metrics dictionary
        """
        return self.health_data

    def get_alerts(self) -> List[Dict[str, str]]:
        """
        Extract alerts from health data.

        Returns:
            List of alert dictionaries
        """
        alerts = []

        # Check thermal alerts
        thermal = self.health_data.get("thermal_health", {})
        for temp in thermal.get("temperatures", []):
            if temp["status"] != HealthStatus.OK:
                alerts.append({
                    "severity": temp["status"],
                    "component": "thermal",
                    "message": f"{temp['name']}: {temp['reading_celsius']}°C (Status: {temp['health']})"
                })

        for fan in thermal.get("fans", []):
            if fan["status"] != HealthStatus.OK:
                alerts.append({
                    "severity": fan["status"],
                    "component": "thermal",
                    "message": f"{fan['name']}: {fan['reading_rpm']} RPM (Status: {fan['health']})"
                })

        # Check power alerts
        power = self.health_data.get("power_health", {})
        for psu in power.get("power_supplies", []):
            if psu["status"] != HealthStatus.OK:
                alerts.append({
                    "severity": psu["status"],
                    "component": "power",
                    "message": f"{psu['name']}: Status {psu['health']}"
                })

        return alerts
