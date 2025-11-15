#!/usr/bin/env python3
"""
Redfish Validation Tool

Validates Redfish connectivity and explores available endpoints.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import RedfishClient, HealthChecker
from loguru import logger


def validate_connection(host: str, username: str, password: str, port: int = 443):
    """
    Validate Redfish connection and gather basic information.

    Args:
        host: Redfish endpoint host
        username: Username
        password: Password
        port: Port number
    """
    print(f"\n{'='*60}")
    print(f"RIM - Redfish Validation Tool")
    print(f"{'='*60}\n")

    print(f"Testing connection to: {host}:{port}")
    print(f"Username: {username}")
    print("-" * 60)

    try:
        # Initialize client
        client = RedfishClient(
            host=host,
            username=username,
            password=password,
            port=port,
            verify_ssl=False
        )

        # Test connection
        print("\n[1/6] Testing connection...")
        if not client.test_connection():
            print("❌ Connection failed!")
            return False
        print("✓ Connection successful")

        # Get service root
        print("\n[2/6] Getting service root...")
        root = client.get_root_service()
        if root:
            print(f"✓ Redfish Version: {root.get('RedfishVersion', 'Unknown')}")
            print(f"✓ Service Name: {root.get('Name', 'Unknown')}")
        else:
            print("❌ Failed to get service root")
            return False

        # Get vendor info
        print("\n[3/6] Getting vendor information...")
        vendor_info = client.get_vendor_info()
        if vendor_info:
            print(f"✓ Vendor: {vendor_info['vendor']}")
            print(f"✓ Model: {vendor_info['model']}")
            print(f"✓ Serial Number: {vendor_info['serial_number']}")
            print(f"✓ BIOS Version: {vendor_info['bios_version']}")
        else:
            print("❌ Failed to get vendor info")

        # Get systems
        print("\n[4/6] Discovering systems...")
        systems = client.get_systems()
        print(f"✓ Found {len(systems)} system(s)")
        for i, system in enumerate(systems, 1):
            print(f"  {i}. {system}")

        # Get chassis
        print("\n[5/6] Discovering chassis...")
        chassis_list = client.get_chassis()
        print(f"✓ Found {len(chassis_list)} chassis")
        for i, chassis in enumerate(chassis_list, 1):
            print(f"  {i}. {chassis}")

        # Get managers
        print("\n[6/6] Discovering managers...")
        managers = client.get_managers()
        print(f"✓ Found {len(managers)} manager(s)")
        for i, manager in enumerate(managers, 1):
            print(f"  {i}. {manager}")

        # Perform health check
        print("\n" + "=" * 60)
        print("Running comprehensive health check...")
        print("=" * 60)

        checker = HealthChecker(client)
        health_data = checker.check_overall_health()

        print(f"\n✓ Overall Status: {health_data['overall_status']}")
        print(f"✓ System Health: {health_data['system_health'].get('status', 'Unknown')}")
        print(f"✓ Thermal Health: {health_data['thermal_health'].get('status', 'Unknown')}")
        print(f"✓ Power Health: {health_data['power_health'].get('status', 'Unknown')}")

        # Show thermal summary
        thermal = health_data.get('thermal_health', {})
        if thermal and 'temperatures' in thermal:
            print(f"\n  Temperature Sensors: {len(thermal['temperatures'])}")
            if thermal.get('summary'):
                print(f"    Max Temperature: {thermal['summary'].get('max_temperature', 0)}°C")
                print(f"    Avg Temperature: {thermal['summary'].get('avg_temperature', 0)}°C")

        if thermal and 'fans' in thermal:
            print(f"  Fans: {len(thermal['fans'])}")

        # Show power summary
        power = health_data.get('power_health', {})
        if power:
            print(f"\n  Power Consumption: {power.get('total_consumed_watts', 0)}W")
            print(f"  Power Capacity: {power.get('total_capacity_watts', 0)}W")
            print(f"  Power Supplies: {power.get('supply_count', 0)}")

        # Get alerts
        alerts = checker.get_alerts()
        if alerts:
            print(f"\n⚠️  Active Alerts: {len(alerts)}")
            for alert in alerts[:5]:  # Show first 5
                print(f"    [{alert['severity']}] {alert['message']}")
        else:
            print("\n✓ No active alerts")

        print("\n" + "=" * 60)
        print("✓ Validation complete!")
        print("=" * 60)

        client.close()
        return True

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n❌ Error: {e}")
        return False


def export_data(host: str, username: str, password: str, port: int, output_dir: str):
    """
    Export all Redfish data to files for analysis.

    Args:
        host: Redfish endpoint host
        username: Username
        password: Password
        port: Port number
        output_dir: Output directory for files
    """
    print(f"\nExporting Redfish data to: {output_dir}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        client = RedfishClient(host, username, password, port, verify_ssl=False)

        # Export service root
        root = client.get_root_service()
        if root:
            with open(output_path / "service_root.json", "w") as f:
                json.dump(root, f, indent=2)
            print("✓ Exported service_root.json")

        # Export system info
        system_info = client.get_system_info()
        if system_info:
            with open(output_path / "system_info.json", "w") as f:
                json.dump(system_info, f, indent=2)
            print("✓ Exported system_info.json")

        # Export thermal data
        thermal = client.get_thermal()
        if thermal:
            with open(output_path / "thermal.json", "w") as f:
                json.dump(thermal, f, indent=2)
            print("✓ Exported thermal.json")

        # Export power data
        power = client.get_power()
        if power:
            with open(output_path / "power.json", "w") as f:
                json.dump(power, f, indent=2)
            print("✓ Exported power.json")

        # Export health check
        checker = HealthChecker(client)
        health_data = checker.check_overall_health()
        with open(output_path / "health_check.json", "w") as f:
            json.dump(health_data, f, indent=2)
        print("✓ Exported health_check.json")

        print(f"\n✓ All data exported to {output_dir}")

        client.close()

    except Exception as e:
        logger.error(f"Export failed: {e}")
        print(f"\n❌ Error: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="RIM Redfish Validation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate connection
  python validate_redfish.py --host 10.0.0.100 --user admin --password pass

  # Export data for analysis
  python validate_redfish.py --host 10.0.0.100 --user admin --password pass --export ./vendor_data

  # Use custom port
  python validate_redfish.py --host 10.0.0.100 --user admin --password pass --port 8443
        """
    )

    parser.add_argument("--host", required=True, help="Redfish host/IP address")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--port", type=int, default=443, help="Port (default: 443)")
    parser.add_argument("--export", help="Export data to directory")

    args = parser.parse_args()

    # Run validation
    success = validate_connection(args.host, args.user, args.password, args.port)

    # Export if requested
    if args.export and success:
        export_data(args.host, args.user, args.password, args.port, args.export)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
