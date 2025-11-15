# RedFish Infrastructure Monitor (RIM)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A comprehensive monitoring solution that bridges hardware infrastructure and monitoring platforms like Zabbix and Grafana. RIM provides standardized, vendor-agnostic monitoring configurations based on the DMTF Redfish specification.

## 🎯 Mission

To provide system administrators and DevOps engineers with production-ready, downloadable monitoring configurations for infrastructure devices, enabling immediate hardware health monitoring without the complexity of manually configuring Redfish endpoints for each vendor.

## ✨ Features

- **Vendor-Agnostic**: Standardized interface for multiple hardware vendors
- **Multi-Platform Support**: Export to Zabbix, Grafana, Prometheus, CSV
- **Easy Integration**: Pre-built templates and dashboards ready for import
- **Comprehensive Metrics**: Temperature, power, storage, network monitoring
- **Extensible Architecture**: Easy to add new vendor implementations
- **Production Ready**: Tested configurations for enterprise hardware

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/m3hr4nn/RIM.git
cd RIM

# Install dependencies
pip install -r requirements.txt

# Run a quick health check
python RHCT.py
```

### Basic Usage

```python
from core import RedfishClient, HealthChecker

# Initialize client
client = RedfishClient(
    host="10.0.0.100",
    username="admin",
    password="password"
)

# Perform health check
checker = HealthChecker(client)
health_data = checker.check_overall_health()

print(f"Overall Status: {health_data['overall_status']}")
```

## 📁 Project Structure

```
RIM/
├── core/                      # Core Python library
│   ├── redfish_client.py      # Redfish API client
│   ├── health_checker.py      # Health check orchestration
│   ├── exporters/             # Export to various formats
│   │   ├── zabbix_exporter.py
│   │   ├── grafana_exporter.py
│   │   ├── csv_exporter.py
│   │   └── prometheus_exporter.py
│   └── vendors/               # Vendor-specific implementations
│       ├── base_vendor.py     # Abstract base class
│       ├── dell.py            # Dell EMC
│       ├── hp.py              # HPE
│       └── ...
├── configs/                   # Pre-built configurations
│   ├── zabbix/               # Zabbix templates
│   └── grafana/              # Grafana dashboards
├── tools/                     # Utility scripts
├── tests/                     # Test suite
└── docs/                      # Documentation

```

## 🔧 Development Setup

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Access to Redfish-enabled hardware (or simulator)

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including dev tools)
pip install -r requirements.txt

# Run tests
pytest tests/

# Run linters
black core/ --check
flake8 core/
pylint core/
```

### Environment Variables

Create a `.env` file for your test environment:

```bash
REDFISH_HOST=10.0.0.100
REDFISH_USER=admin
REDFISH_PASSWORD=yourpassword
REDFISH_PORT=443
REDFISH_VERIFY_SSL=false
```

## 📊 Supported Vendors

| Vendor | Server | Storage | Network | Status |
|--------|--------|---------|---------|--------|
| Dell EMC | ✅ | ✅ | ❌ | Stable |
| HPE | ✅ | ✅ | ❌ | Beta |
| Cisco | ✅ | ❌ | ✅ | Beta |
| Lenovo | ✅ | ❌ | ❌ | Beta |
| Supermicro | ✅ | ❌ | ❌ | WIP |
| NetApp | ❌ | ✅ | ❌ | Planned |

See [VENDOR_GUIDE.md](VENDOR_GUIDE.md) for detailed information on gathering vendor-specific data.

## 📖 Documentation

- **[Getting Started](docs/getting-started.md)** - Installation and basic usage
- **[Vendor Guide](VENDOR_GUIDE.md)** - How to gather vendor-specific information
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[API Reference](docs/api.md)** - Detailed API documentation
- **[Integration Guides](docs/integration/)** - Platform-specific integration guides

## 🎯 Use Cases

### Export to CSV for Grafana

```python
from core import RedfishClient, HealthChecker
from core.exporters import CSVExporter

client = RedfishClient(host="10.0.0.100", username="admin", password="pass")
checker = HealthChecker(client)
health_data = checker.check_overall_health()

exporter = CSVExporter()
csv_content = exporter.export(health_data, output_file="metrics.csv")
```

### Vendor-Specific Implementation

```python
from core import RedfishClient
from core.vendors.dell import DellVendor

client = RedfishClient(host="dell-server.local", username="admin", password="pass")
dell = DellVendor(client)

# Get Dell-specific metrics
thermal = dell.get_thermal_metrics()
power = dell.get_power_metrics()

print(f"Max Temperature: {thermal['summary']['max_temperature']}°C")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-vendor`
3. Implement your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- DMTF Redfish Working Group for the excellent API specification
- All contributors who help improve this project
- The infrastructure monitoring community

## 📞 Contact & Support

- **Author**: m3hr4nn
- **Repository**: https://github.com/m3hr4nn/RIM
- **Issues**: https://github.com/m3hr4nn/RIM/issues
- **Website**: https://m3hr4nn.github.io/RIM (coming soon)

## 🗺️ Roadmap

### 2025 Q1
- [x] Core Redfish client library
- [x] Basic health checking
- [ ] Zabbix template generator
- [ ] Initial documentation site

### 2025 Q2
- [ ] Grafana dashboard generator
- [ ] CSV/JSON export formats
- [ ] 5+ server vendor support
- [ ] Prometheus exporter

### 2025 Q3
- [ ] Storage device support
- [ ] Network equipment support
- [ ] Advanced Grafana dashboards
- [ ] Community contributions

---

**Built with ❤️ for the infrastructure monitoring community**
