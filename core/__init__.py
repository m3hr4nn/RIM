"""
RedFish Infrastructure Monitor (RIM) - Core Module

This module provides the core functionality for interacting with Redfish APIs,
performing health checks, and exporting data to various monitoring platforms.
"""

__version__ = "1.0.0"
__author__ = "m3hr4nn"

from .redfish_client import RedfishClient
from .health_checker import HealthChecker

__all__ = ["RedfishClient", "HealthChecker"]
