#!/usr/bin/env python3
"""
Template Generator Tool

Generates Zabbix templates and Grafana dashboards from health data.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import RedfishClient, HealthChecker
from core.exporters import ZabbixExporter, GrafanaExporter, CSVExporter
from loguru import logger


def generate_templates(host: str, username: str, password: str,
                      output_dir: str, formats: list):
    """
    Generate monitoring templates from live Redfish data.

    Args:
        host: Redfish endpoint host
        username: Username
        password: Password
        output_dir: Output directory for templates
        formats: List of formats to generate (zabbix, grafana, csv)
    """
    print(f"\n{'='*60}")
    print(f"RIM - Template Generator")
    print(f"{'='*60}\n")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # Connect and gather data
        print(f"Connecting to {host}...")
        client = RedfishClient(host, username, password, verify_ssl=False)

        if not client.test_connection():
            print("❌ Connection failed!")
            return False

        print("✓ Connected successfully")

        # Get vendor info
        vendor_info = client.get_vendor_info()
        vendor = vendor_info['vendor'].replace(" ", "-")
        model = vendor_info['model'].replace(" ", "-")

        print(f"\nVendor: {vendor_info['vendor']}")
        print(f"Model: {vendor_info['model']}")

        # Perform health check
        print("\nRunning health check...")
        checker = HealthChecker(client)
        health_data = checker.check_overall_health()
        print("✓ Health check complete")

        # Generate templates
        print(f"\nGenerating templates to: {output_dir}")
        print("-" * 60)

        if 'zabbix' in formats:
            print("\nGenerating Zabbix template...")
            exporter = ZabbixExporter()
            template_file = output_path / f"zabbix_{vendor}_{model}.xml"
            template = exporter.generate_from_health_data(health_data, str(template_file))
            print(f"✓ Saved: {template_file}")

        if 'grafana' in formats:
            print("\nGenerating Grafana dashboard...")
            exporter = GrafanaExporter()
            dashboard_file = output_path / f"grafana_{vendor}_{model}.json"
            dashboard = exporter.generate_from_health_data(health_data, str(dashboard_file))
            print(f"✓ Saved: {dashboard_file}")

        if 'csv' in formats:
            print("\nGenerating CSV export...")
            exporter = CSVExporter()
            csv_file = output_path / f"csv_{vendor}_{model}_template.csv"
            csv_content = exporter.export(health_data, str(csv_file))
            print(f"✓ Saved: {csv_file}")

            # Also generate example with actual data
            example_file = output_path / f"csv_{vendor}_{model}_example.csv"
            exporter.export(health_data, str(example_file))
            print(f"✓ Saved: {example_file}")

        print("\n" + "=" * 60)
        print("✓ Template generation complete!")
        print("=" * 60)

        client.close()
        return True

    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        print(f"\n❌ Error: {e}")
        return False


def generate_offline(health_data_file: str, output_dir: str, formats: list):
    """
    Generate templates from previously exported health data.

    Args:
        health_data_file: Path to health_check.json file
        output_dir: Output directory for templates
        formats: List of formats to generate
    """
    print(f"\nGenerating templates from: {health_data_file}")

    try:
        with open(health_data_file, 'r') as f:
            health_data = json.load(f)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        vendor_info = health_data.get('vendor_info', {})
        vendor = vendor_info.get('vendor', 'Unknown').replace(" ", "-")
        model = vendor_info.get('model', 'Unknown').replace(" ", "-")

        if 'zabbix' in formats:
            exporter = ZabbixExporter()
            template_file = output_path / f"zabbix_{vendor}_{model}.xml"
            exporter.generate_from_health_data(health_data, str(template_file))
            print(f"✓ Generated: {template_file}")

        if 'grafana' in formats:
            exporter = GrafanaExporter()
            dashboard_file = output_path / f"grafana_{vendor}_{model}.json"
            exporter.generate_from_health_data(health_data, str(dashboard_file))
            print(f"✓ Generated: {dashboard_file}")

        if 'csv' in formats:
            exporter = CSVExporter()
            csv_file = output_path / f"csv_{vendor}_{model}.csv"
            exporter.export(health_data, str(csv_file))
            print(f"✓ Generated: {csv_file}")

        print("\n✓ Template generation complete!")
        return True

    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="RIM Template Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all templates from live device
  python generate_templates.py --host 10.0.0.100 --user admin --password pass --output ./configs

  # Generate only Zabbix template
  python generate_templates.py --host 10.0.0.100 --user admin --password pass --format zabbix --output ./configs

  # Generate from exported health data
  python generate_templates.py --from-file ./vendor_data/health_check.json --output ./configs

  # Generate multiple formats
  python generate_templates.py --host 10.0.0.100 --user admin --password pass --format zabbix grafana csv --output ./configs
        """
    )

    parser.add_argument("--host", help="Redfish host/IP address")
    parser.add_argument("--user", help="Username")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--port", type=int, default=443, help="Port (default: 443)")
    parser.add_argument("--from-file", help="Generate from health_check.json file")
    parser.add_argument("--format", nargs='+',
                       choices=['zabbix', 'grafana', 'csv', 'all'],
                       default=['all'],
                       help="Template formats to generate")
    parser.add_argument("--output", default="./configs",
                       help="Output directory (default: ./configs)")

    args = parser.parse_args()

    # Validate arguments
    if not args.from_file and not (args.host and args.user and args.password):
        parser.error("Either --from-file or (--host, --user, --password) must be provided")

    # Determine formats
    if 'all' in args.format:
        formats = ['zabbix', 'grafana', 'csv']
    else:
        formats = args.format

    # Generate templates
    if args.from_file:
        success = generate_offline(args.from_file, args.output, formats)
    else:
        success = generate_templates(
            args.host, args.user, args.password,
            args.output, formats
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
