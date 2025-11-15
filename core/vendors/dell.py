"""
Dell EMC Vendor Implementation

Vendor-specific implementation for Dell EMC PowerEdge servers.
"""

from typing import Dict, Any, List
from loguru import logger
from .base_vendor import BaseVendor


class DellVendor(BaseVendor):
    """
    Dell EMC specific implementation for PowerEdge servers.

    Supports: PowerEdge R740, R640, R940, R740xd, and other 14G/15G servers
    """

    def get_vendor_name(self) -> str:
        return "Dell EMC"

    def get_supported_models(self) -> List[str]:
        return [
            "PowerEdge R740",
            "PowerEdge R640",
            "PowerEdge R940",
            "PowerEdge R740xd",
            "PowerEdge R440",
            "PowerEdge R540",
            "PowerEdge R6415",
            "PowerEdge R7415",
            "PowerEdge R7425"
        ]

    def get_thermal_metrics(self) -> Dict[str, Any]:
        """
        Get Dell-specific thermal metrics.

        Dell servers provide detailed thermal information including:
        - Inlet temperature
        - Exhaust temperature
        - CPU temperatures
        - Memory temperatures
        - PCIe temperatures
        """
        logger.debug("Collecting Dell thermal metrics")

        thermal_data = self.client.get_thermal()
        if not thermal_data:
            return {"error": "Unable to retrieve thermal data"}

        metrics = {
            "temperatures": [],
            "fans": [],
            "summary": {
                "max_temperature": 0,
                "avg_temperature": 0,
                "critical_count": 0,
                "warning_count": 0
            }
        }

        # Process temperatures
        temps = []
        for temp in thermal_data.get("Temperatures", []):
            temp_reading = temp.get("ReadingCelsius")
            if temp_reading:
                temps.append(temp_reading)

            temp_info = {
                "name": temp.get("Name", "Unknown"),
                "reading_celsius": temp_reading,
                "upper_threshold_critical": temp.get("UpperThresholdCritical"),
                "upper_threshold_fatal": temp.get("UpperThresholdFatal"),
                "lower_threshold_critical": temp.get("LowerThresholdCritical"),
                "status": temp.get("Status", {}).get("Health", "OK"),
                "location": self._parse_dell_sensor_location(temp.get("Name", ""))
            }
            metrics["temperatures"].append(temp_info)

            if temp.get("Status", {}).get("Health") == "Critical":
                metrics["summary"]["critical_count"] += 1
            elif temp.get("Status", {}).get("Health") == "Warning":
                metrics["summary"]["warning_count"] += 1

        # Calculate summary stats
        if temps:
            metrics["summary"]["max_temperature"] = max(temps)
            metrics["summary"]["avg_temperature"] = round(sum(temps) / len(temps), 2)

        # Process fans
        for fan in thermal_data.get("Fans", []):
            fan_info = {
                "name": fan.get("Name", "Unknown"),
                "reading_rpm": fan.get("Reading"),
                "reading_percent": fan.get("ReadingUnits") == "Percent",
                "min_reading": fan.get("MinReadingRange"),
                "max_reading": fan.get("MaxReadingRange"),
                "status": fan.get("Status", {}).get("Health", "OK"),
                "location": self._parse_dell_fan_location(fan.get("Name", ""))
            }
            metrics["fans"].append(fan_info)

        return metrics

    def get_power_metrics(self) -> Dict[str, Any]:
        """
        Get Dell-specific power metrics.

        Dell servers provide:
        - Power consumption per PSU
        - Total system power
        - Power capacity
        - Input/output voltages
        - Efficiency ratings
        """
        logger.debug("Collecting Dell power metrics")

        power_data = self.client.get_power()
        if not power_data:
            return {"error": "Unable to retrieve power data"}

        metrics = {
            "power_supplies": [],
            "power_control": {},
            "summary": {
                "total_capacity_watts": 0,
                "total_consumed_watts": 0,
                "redundancy_status": "Unknown",
                "efficiency_percent": 0
            }
        }

        # Process power supplies
        for psu in power_data.get("PowerSupplies", []):
            psu_info = {
                "name": psu.get("Name", "Unknown"),
                "model": psu.get("Model", "Unknown"),
                "manufacturer": psu.get("Manufacturer", "Unknown"),
                "serial_number": psu.get("SerialNumber", "Unknown"),
                "firmware_version": psu.get("FirmwareVersion", "Unknown"),
                "capacity_watts": psu.get("PowerCapacityWatts", 0),
                "input_voltage": psu.get("LineInputVoltage"),
                "output_voltage": psu.get("OutputVoltage"),
                "status": psu.get("Status", {}).get("Health", "OK"),
                "state": psu.get("Status", {}).get("State", "Unknown"),
                "hot_pluggable": psu.get("HotPluggable", False)
            }
            metrics["power_supplies"].append(psu_info)
            metrics["summary"]["total_capacity_watts"] += psu.get("PowerCapacityWatts", 0)

        # Process power control
        power_control = power_data.get("PowerControl", [])
        if power_control:
            pc = power_control[0]
            metrics["power_control"] = {
                "consumed_watts": pc.get("PowerConsumedWatts", 0),
                "capacity_watts": pc.get("PowerCapacityWatts", 0),
                "average_watts": pc.get("PowerMetrics", {}).get("AverageConsumedWatts", 0),
                "max_watts": pc.get("PowerMetrics", {}).get("MaxConsumedWatts", 0),
                "min_watts": pc.get("PowerMetrics", {}).get("MinConsumedWatts", 0)
            }
            metrics["summary"]["total_consumed_watts"] = pc.get("PowerConsumedWatts", 0)

        # Calculate efficiency
        if metrics["summary"]["total_capacity_watts"] > 0:
            metrics["summary"]["efficiency_percent"] = round(
                (metrics["summary"]["total_consumed_watts"] /
                 metrics["summary"]["total_capacity_watts"] * 100), 2
            )

        # Get redundancy info
        redundancy = power_data.get("Redundancy", [])
        if redundancy:
            metrics["summary"]["redundancy_status"] = redundancy[0].get("Status", {}).get("Health", "Unknown")

        return metrics

    def get_storage_metrics(self) -> Dict[str, Any]:
        """
        Get Dell-specific storage metrics.

        Dell servers use PERC RAID controllers with detailed storage info.
        """
        logger.debug("Collecting Dell storage metrics")

        storage_data = self.client.get_storage()
        if not storage_data:
            return {"error": "Unable to retrieve storage data"}

        metrics = {
            "controllers": [],
            "drives": [],
            "summary": {
                "total_controllers": 0,
                "total_drives": 0,
                "total_capacity_gb": 0,
                "failed_drives": 0
            }
        }

        # Dell storage implementation would go here
        # This requires iterating through Storage collection
        # Placeholder for now

        return metrics

    def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get Dell-specific network metrics.
        """
        logger.debug("Collecting Dell network metrics")

        # Network metrics implementation
        # This would query EthernetInterfaces collection

        return {
            "interfaces": [],
            "summary": {
                "total_interfaces": 0,
                "active_interfaces": 0
            }
        }

    def get_custom_endpoints(self) -> Dict[str, str]:
        """
        Get Dell-specific OEM endpoints.

        Dell provides additional OEM endpoints for:
        - iDRAC specific info
        - Lifecycle controller
        - System attributes
        """
        return {
            "idrac_attributes": "/redfish/v1/Managers/iDRAC.Embedded.1/Attributes",
            "system_attributes": "/redfish/v1/Systems/System.Embedded.1/Attributes",
            "lifecycle_controller": "/redfish/v1/Managers/iDRAC.Embedded.1/Oem/Dell/DellLCService",
            "jobs": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs"
        }

    def _parse_dell_sensor_location(self, sensor_name: str) -> str:
        """
        Parse Dell sensor naming to determine location.

        Args:
            sensor_name: Sensor name from Redfish

        Returns:
            Parsed location string
        """
        if "CPU" in sensor_name:
            return "Processor"
        elif "Inlet" in sensor_name:
            return "Front"
        elif "Exhaust" in sensor_name:
            return "Rear"
        elif "DIMM" in sensor_name or "Mem" in sensor_name:
            return "Memory"
        elif "PCIe" in sensor_name:
            return "PCIe"
        else:
            return "System"

    def _parse_dell_fan_location(self, fan_name: str) -> str:
        """
        Parse Dell fan naming to determine location.

        Args:
            fan_name: Fan name from Redfish

        Returns:
            Parsed location string
        """
        if "Fan1" in fan_name or "FAN1" in fan_name:
            return "Front-Left"
        elif "Fan2" in fan_name or "FAN2" in fan_name:
            return "Front-Right"
        elif "Fan3" in fan_name or "FAN3" in fan_name:
            return "Rear-Left"
        elif "Fan4" in fan_name or "FAN4" in fan_name:
            return "Rear-Right"
        else:
            return "Unknown"
