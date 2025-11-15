"""
Redfish Client Module

Provides a generic client for interacting with Redfish APIs across different vendors.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from urllib3.exceptions import InsecureRequestWarning
from loguru import logger
import urllib3

# Disable SSL warnings (can be configured per environment)
urllib3.disable_warnings(InsecureRequestWarning)


class RedfishClient:
    """
    Generic Redfish API client for infrastructure monitoring.

    This client provides standardized access to Redfish endpoints across
    different vendor implementations.
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 443,
        verify_ssl: bool = False,
        timeout: int = 30
    ):
        """
        Initialize Redfish client.

        Args:
            host: Hostname or IP address of the Redfish endpoint
            username: Authentication username
            password: Authentication password
            port: Redfish API port (default: 443)
            verify_ssl: Whether to verify SSL certificates (default: False)
            timeout: Request timeout in seconds (default: 30)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl

        # Cache for frequently accessed data
        self._cache: Dict[str, Any] = {}

        logger.info(f"Initialized Redfish client for {host}")

    def get(self, endpoint: str, use_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        Perform GET request to Redfish endpoint.

        Args:
            endpoint: API endpoint path (e.g., '/redfish/v1/Systems')
            use_cache: Whether to use cached response if available

        Returns:
            JSON response as dictionary, or None on error
        """
        if use_cache and endpoint in self._cache:
            logger.debug(f"Using cached response for {endpoint}")
            return self._cache[endpoint]

        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"GET request to {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if use_cache:
                self._cache[endpoint] = data

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {url}: {e}")
            return None

    def get_root_service(self) -> Optional[Dict[str, Any]]:
        """Get Redfish root service information."""
        return self.get("/redfish/v1/", use_cache=True)

    def get_systems(self) -> List[str]:
        """
        Get list of available systems.

        Returns:
            List of system URLs
        """
        data = self.get("/redfish/v1/Systems")
        if data and "Members" in data:
            return [member["@odata.id"] for member in data["Members"]]
        return []

    def get_system_info(self, system_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a system.

        Args:
            system_id: System identifier (if None, uses first system)

        Returns:
            System information dictionary
        """
        if not system_id:
            systems = self.get_systems()
            if not systems:
                logger.error("No systems found")
                return None
            system_id = systems[0]

        if not system_id.startswith("/redfish"):
            system_id = f"/redfish/v1/Systems/{system_id}"

        return self.get(system_id)

    def get_chassis(self) -> List[str]:
        """
        Get list of available chassis.

        Returns:
            List of chassis URLs
        """
        data = self.get("/redfish/v1/Chassis")
        if data and "Members" in data:
            return [member["@odata.id"] for member in data["Members"]]
        return []

    def get_chassis_info(self, chassis_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a chassis.

        Args:
            chassis_id: Chassis identifier (if None, uses first chassis)

        Returns:
            Chassis information dictionary
        """
        if not chassis_id:
            chassis_list = self.get_chassis()
            if not chassis_list:
                logger.error("No chassis found")
                return None
            chassis_id = chassis_list[0]

        if not chassis_id.startswith("/redfish"):
            chassis_id = f"/redfish/v1/Chassis/{chassis_id}"

        return self.get(chassis_id)

    def get_thermal(self, chassis_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get thermal information (temperatures, fans).

        Args:
            chassis_id: Chassis identifier

        Returns:
            Thermal data dictionary
        """
        chassis_info = self.get_chassis_info(chassis_id)
        if chassis_info and "Thermal" in chassis_info:
            thermal_url = chassis_info["Thermal"]["@odata.id"]
            return self.get(thermal_url)
        return None

    def get_power(self, chassis_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get power information (consumption, supplies).

        Args:
            chassis_id: Chassis identifier

        Returns:
            Power data dictionary
        """
        chassis_info = self.get_chassis_info(chassis_id)
        if chassis_info and "Power" in chassis_info:
            power_url = chassis_info["Power"]["@odata.id"]
            return self.get(power_url)
        return None

    def get_managers(self) -> List[str]:
        """
        Get list of available managers.

        Returns:
            List of manager URLs
        """
        data = self.get("/redfish/v1/Managers")
        if data and "Members" in data:
            return [member["@odata.id"] for member in data["Members"]]
        return []

    def get_storage(self, system_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get storage information.

        Args:
            system_id: System identifier

        Returns:
            Storage data dictionary
        """
        system_info = self.get_system_info(system_id)
        if system_info and "Storage" in system_info:
            storage_url = system_info["Storage"]["@odata.id"]
            return self.get(storage_url)
        return None

    def test_connection(self) -> bool:
        """
        Test connection to Redfish endpoint.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            data = self.get_root_service()
            if data and "RedfishVersion" in data:
                logger.info(f"Successfully connected to Redfish {data['RedfishVersion']}")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_vendor_info(self) -> Optional[Dict[str, str]]:
        """
        Extract vendor information from system.

        Returns:
            Dictionary with vendor, model, and other identifying information
        """
        system_info = self.get_system_info()
        if not system_info:
            return None

        return {
            "vendor": system_info.get("Manufacturer", "Unknown"),
            "model": system_info.get("Model", "Unknown"),
            "serial_number": system_info.get("SerialNumber", "Unknown"),
            "bios_version": system_info.get("BiosVersion", "Unknown"),
            "sku": system_info.get("SKU", "Unknown")
        }

    def clear_cache(self):
        """Clear the response cache."""
        self._cache.clear()
        logger.debug("Cache cleared")

    def close(self):
        """Close the session."""
        self.session.close()
        logger.info(f"Closed Redfish client for {self.host}")
