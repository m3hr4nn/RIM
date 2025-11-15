"""
Base Vendor Class

Abstract base class for vendor-specific Redfish implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from loguru import logger
from ..redfish_client import RedfishClient


class BaseVendor(ABC):
    """
    Abstract base class for vendor-specific implementations.

    Each vendor class should inherit from this and implement vendor-specific
    methods for extracting metrics and handling vendor-specific endpoints.
    """

    def __init__(self, client: RedfishClient):
        """
        Initialize vendor implementation.

        Args:
            client: Initialized RedfishClient instance
        """
        self.client = client
        self.vendor_name = self.get_vendor_name()
        logger.info(f"Initialized {self.vendor_name} vendor implementation")

    @abstractmethod
    def get_vendor_name(self) -> str:
        """
        Get the vendor name.

        Returns:
            Vendor name string
        """
        pass

    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported models for this vendor.

        Returns:
            List of supported model names/patterns
        """
        pass

    @abstractmethod
    def get_thermal_metrics(self) -> Dict[str, Any]:
        """
        Get vendor-specific thermal metrics.

        Returns:
            Dictionary containing thermal data
        """
        pass

    @abstractmethod
    def get_power_metrics(self) -> Dict[str, Any]:
        """
        Get vendor-specific power metrics.

        Returns:
            Dictionary containing power data
        """
        pass

    @abstractmethod
    def get_storage_metrics(self) -> Dict[str, Any]:
        """
        Get vendor-specific storage metrics.

        Returns:
            Dictionary containing storage data
        """
        pass

    @abstractmethod
    def get_network_metrics(self) -> Dict[str, Any]:
        """
        Get vendor-specific network metrics.

        Returns:
            Dictionary containing network data
        """
        pass

    def get_custom_endpoints(self) -> Dict[str, str]:
        """
        Get vendor-specific custom Redfish endpoints.

        Override this method if vendor has custom/OEM endpoints.

        Returns:
            Dictionary mapping endpoint names to URLs
        """
        return {}

    def validate_compatibility(self, model: str) -> bool:
        """
        Check if this vendor implementation is compatible with the given model.

        Args:
            model: Model identifier

        Returns:
            True if compatible, False otherwise
        """
        supported = self.get_supported_models()
        for pattern in supported:
            if pattern.lower() in model.lower():
                return True
        return False

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics from all sources.

        Returns:
            Comprehensive metrics dictionary
        """
        logger.info(f"Collecting all metrics for {self.vendor_name}")

        metrics = {
            "vendor": self.vendor_name,
            "vendor_info": self.client.get_vendor_info(),
            "thermal": self.get_thermal_metrics(),
            "power": self.get_power_metrics(),
            "storage": self.get_storage_metrics(),
            "network": self.get_network_metrics()
        }

        return metrics

    def get_firmware_versions(self) -> Dict[str, str]:
        """
        Get firmware version information.

        Returns:
            Dictionary with component firmware versions
        """
        versions = {}

        # Get system info for BIOS version
        system_info = self.client.get_system_info()
        if system_info:
            versions["bios"] = system_info.get("BiosVersion", "Unknown")

        # Get manager firmware
        managers = self.client.get_managers()
        for i, manager_url in enumerate(managers):
            manager_data = self.client.get(manager_url)
            if manager_data:
                fw_version = manager_data.get("FirmwareVersion", "Unknown")
                versions[f"manager_{i}"] = fw_version

        return versions

    def export_zabbix_template(self) -> str:
        """
        Generate Zabbix template XML for this vendor.

        Override this method to provide vendor-specific Zabbix templates.

        Returns:
            Zabbix template XML as string
        """
        raise NotImplementedError(f"Zabbix template export not implemented for {self.vendor_name}")

    def export_grafana_dashboard(self) -> Dict[str, Any]:
        """
        Generate Grafana dashboard JSON for this vendor.

        Override this method to provide vendor-specific Grafana dashboards.

        Returns:
            Grafana dashboard JSON as dictionary
        """
        raise NotImplementedError(f"Grafana dashboard export not implemented for {self.vendor_name}")
