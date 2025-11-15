# RedFish Infrastructure Monitor (RIM)

## Project Overview

**RIM** (RedFish Infrastructure Monitor) is a comprehensive monitoring solution designed to bridge the gap between hardware infrastructure and monitoring platforms like Zabbix and Grafana. The project provides standardized, vendor-agnostic monitoring configurations based on the DMTF Redfish specification for enterprise infrastructure devices.

## Mission Statement

To provide system administrators and DevOps engineers with production-ready, downloadable monitoring configurations for infrastructure devices, enabling immediate hardware health monitoring without the complexity of manually configuring Redfish endpoints for each vendor.

## Project Goals

1. **Unified Hardware Language**: Translate vendor-specific Redfish implementations into standardized monitoring configurations
2. **Multi-Platform Support**: Provide monitoring configurations for Zabbix, Grafana, and other popular monitoring platforms
3. **Vendor Coverage**: Support major infrastructure vendors across servers, storage, and network equipment
4. **Easy Deployment**: Downloadable, import-ready configuration files
5. **Visual Dashboards**: Pre-built Grafana dashboards for immediate visualization
6. **Community-Driven**: Open-source project with community contributions for vendor-specific configurations

## Architecture

### Core Components

```
RIM/
├── core/                          # Core Python library
│   ├── redfish_client.py          # Redfish API client
│   ├── health_checker.py          # Health check orchestration
│   ├── exporters/                 # Export to various formats
│   │   ├── zabbix_exporter.py     # Zabbix template generator
│   │   ├── grafana_exporter.py    # Grafana dashboard generator
│   │   ├── csv_exporter.py        # CSV/TXT data exporter
│   │   └── prometheus_exporter.py # Prometheus metrics exporter
│   └── vendors/                   # Vendor-specific implementations
│       ├── dell.py                # Dell EMC specifics
│       ├── hp.py                  # HPE specifics
│       ├── cisco.py               # Cisco specifics
│       ├── lenovo.py              # Lenovo specifics
│       ├── supermicro.py          # Supermicro specifics
│       └── netapp.py              # NetApp specifics
│
├── configs/                       # Pre-built configurations
│   ├── zabbix/
│   │   ├── servers/
│   │   │   ├── dell-poweredge.xml
│   │   │   ├── hp-proliant.xml
│   │   │   ├── cisco-ucs.xml
│   │   │   └── ...
│   │   ├── storage/
│   │   │   ├── dell-emc-unity.xml
│   │   │   ├── netapp-fas.xml
│   │   │   └── ...
│   │   └── network/
│   │       ├── cisco-nexus.xml
│   │       └── ...
│   │
│   └── grafana/
│       ├── dashboards/
│       │   ├── servers/
│       │   │   ├── dell-poweredge.json
│       │   │   ├── hp-proliant.json
│       │   │   └── ...
│       │   ├── storage/
│       │   │   ├── dell-emc-unity.json
│       │   │   └── ...
│       │   └── network/
│       │       └── ...
│       └── datasources/
│           ├── csv-templates/
│           └── json-templates/
│
├── docs/                          # GitHub Pages documentation site
│   ├── index.html                 # Landing page
│   ├── getting-started.html
│   ├── vendor-guides/
│   │   ├── servers.html
│   │   ├── storage.html
│   │   └── network.html
│   ├── integration/
│   │   ├── zabbix.html
│   │   ├── grafana.html
│   │   └── prometheus.html
│   └── assets/
│       ├── css/
│       ├── js/
│       └── images/
│
├── web/                           # GitHub Pages source
│   ├── _config.yml                # Jekyll configuration
│   ├── index.md                   # Home page
│   ├── downloads/                 # Download page organization
│   │   ├── servers.md
│   │   ├── storage.md
│   │   └── network.md
│   └── dashboards/
│       └── grafana.md
│
└── tools/                         # Utility scripts
    ├── generate_zabbix_template.py
    ├── generate_grafana_dashboard.py
    └── validate_redfish.py
```

## GitHub Pages Website Structure

### Website Goals

The RIM website (https://m3hr4nn.github.io/RIM) will serve as:

1. **Documentation Hub**: Comprehensive guides for using RIM
2. **Download Center**: Categorized downloads for all configurations
3. **Integration Guides**: Step-by-step integration with monitoring platforms
4. **Community Portal**: Contribution guidelines and vendor support matrix

### Website Pages

#### 1. Home Page (`index.html`)
- Project overview
- Quick start guide
- Featured vendors
- Latest updates
- Community statistics

#### 2. Downloads Section

##### Servers (`/downloads/servers.html`)
Categorized by vendor:
- **Dell EMC**
  - PowerEdge R740
  - PowerEdge R640
  - PowerEdge R940
  - [Zabbix Template] [Grafana Dashboard] [CSV Template]

- **HPE**
  - ProLiant DL380 Gen10
  - ProLiant DL360 Gen10
  - Synergy
  - [Zabbix Template] [Grafana Dashboard] [CSV Template]

- **Cisco**
  - UCS C-Series
  - UCS B-Series
  - [Zabbix Template] [Grafana Dashboard] [CSV Template]

- **Lenovo**
  - ThinkSystem SR650
  - ThinkSystem SR630
  - [Zabbix Template] [Grafana Dashboard] [CSV Template]

- **Supermicro**
  - SuperServer Series
  - [Zabbix Template] [Grafana Dashboard] [CSV Template]

##### Storage (`/downloads/storage.html`)
- **Dell EMC**
  - Unity
  - PowerStore
  - VNX

- **NetApp**
  - FAS Series
  - AFF Series

- **Pure Storage**
  - FlashArray

- **HPE**
  - 3PAR
  - Nimble Storage

##### Network Equipment (`/downloads/network.html`)
- **Cisco**
  - Nexus Series
  - Catalyst Series

- **Arista**
  - 7000 Series

- **Juniper**
  - QFX Series
  - EX Series

#### 3. Integration Guides

##### Zabbix Integration (`/integration/zabbix.html`)
- Installing Zabbix templates
- Configuring host monitoring
- Setting up triggers and alerts
- Custom macros for each vendor
- Troubleshooting guide

##### Grafana Integration (`/integration/grafana.html`)
- Importing dashboards
- Configuring data sources
- CSV/JSON import formats
- Dashboard customization
- Variables and filters

##### Prometheus Integration (`/integration/prometheus.html`)
- Prometheus exporter setup
- Metrics format
- Service discovery
- Alert manager configuration

#### 4. Documentation

##### API Reference (`/docs/api.html`)
- Python library usage
- Redfish client API
- Custom vendor implementations
- Export formats

##### Contributor Guide (`/docs/contributing.html`)
- How to add new vendor support
- Template creation guidelines
- Testing requirements
- Pull request process

## Grafana Integration

### Data Export Formats

RIM will support multiple data export formats for Grafana:

#### 1. CSV Format (`metrics.csv`)

```csv
timestamp,device_name,device_type,vendor,metric_name,value,unit,status
2025-11-15T10:30:00Z,server-01,server,Dell,cpu_temperature,45,celsius,OK
2025-11-15T10:30:00Z,server-01,server,Dell,fan_speed,3500,rpm,OK
2025-11-15T10:30:00Z,server-01,server,Dell,power_consumption,450,watts,OK
2025-11-15T10:30:00Z,server-01,server,Dell,memory_health,1,status,OK
2025-11-15T10:30:00Z,storage-01,storage,NetApp,disk_utilization,75,percent,Warning
```

#### 2. JSON Format (`metrics.json`)

```json
{
  "datasource": "RIM-Redfish-Metrics",
  "targets": [
    {
      "device": "server-01",
      "vendor": "Dell",
      "model": "PowerEdge R740",
      "metrics": {
        "thermal": {
          "temperatures": [
            {"name": "CPU1", "value": 45, "unit": "celsius", "status": "OK"},
            {"name": "CPU2", "value": 47, "unit": "celsius", "status": "OK"}
          ],
          "fans": [
            {"name": "Fan1", "value": 3500, "unit": "rpm", "status": "OK"}
          ]
        },
        "power": {
          "consumption": 450,
          "capacity": 1100,
          "supplies": [
            {"name": "PSU1", "status": "OK", "output": 225}
          ]
        },
        "storage": {
          "controllers": [
            {"name": "PERC H740P", "status": "OK"}
          ],
          "drives": [
            {"name": "Disk.Bay.0", "status": "OK", "capacity_gb": 1200}
          ]
        }
      }
    }
  ]
}
```

#### 3. Simple Text Format (`metrics.txt`)

```
# Server Metrics - server-01 (Dell PowerEdge R740)
cpu1_temp 45
cpu2_temp 47
fan1_speed 3500
fan2_speed 3600
power_watts 450
psu1_status 1
psu2_status 1
memory_status 1
storage_status 1
```

### Grafana Dashboard Templates

Each vendor/model combination will have:

1. **Overview Dashboard**: High-level health status
2. **Detailed Metrics Dashboard**: Deep-dive into specific components
3. **Alert Dashboard**: Current and historical alerts
4. **Comparison Dashboard**: Compare multiple devices

#### Dashboard Features

- **Time-series graphs**: Temperature, power consumption, fan speeds
- **Status panels**: Component health (green/yellow/red)
- **Table views**: Drive status, network port status
- **Gauges**: Utilization percentages
- **Variables**: Device selection, time range, vendor filter
- **Annotations**: Maintenance events, configuration changes

### Import Instructions

Users will be able to:
1. Download pre-configured Grafana dashboard JSON
2. Import CSV data using CSV plugin
3. Import JSON data using JSON API datasource
4. Connect to live Prometheus exporter
5. Use Infinity datasource for direct HTTP queries

## Zabbix Integration

### Template Structure

Each Zabbix template will include:

1. **Discovery Rules**
   - Auto-discover Redfish endpoints
   - Discover system components (CPUs, memory, drives, PSUs)
   - Discover network interfaces

2. **Items**
   - Temperature sensors
   - Fan speeds
   - Power consumption
   - Component health status
   - BIOS version
   - Firmware versions

3. **Triggers**
   - Critical temperature thresholds
   - Fan failure detection
   - Power supply failure
   - Drive failure prediction
   - Memory errors

4. **Graphs**
   - Temperature trends
   - Power consumption over time
   - Fan speed monitoring
   - Network throughput

5. **Screens/Dashboards**
   - System overview
   - Component health matrix
   - Historical trends

### Vendor-Specific Macros

Templates will use macros for vendor-specific values:

```
{$REDFISH.URL} = https://{HOST.CONN}
{$REDFISH.USER} = admin
{$REDFISH.PASSWORD} = {stored in Zabbix vault}
{$TEMP.WARN} = 75
{$TEMP.CRIT} = 85
{$FAN.MIN.WARN} = 2000
{$FAN.MIN.CRIT} = 1500
```

## Development Workflow

### Adding New Vendor Support

1. **Research Phase**
   - Document vendor's Redfish implementation
   - Identify unique endpoints and data structures
   - Test against actual hardware or simulator

2. **Implementation Phase**
   - Create vendor-specific class in `core/vendors/`
   - Implement metric extraction methods
   - Add export logic for Zabbix/Grafana

3. **Configuration Phase**
   - Generate Zabbix template XML
   - Create Grafana dashboard JSON
   - Prepare CSV/JSON export samples

4. **Documentation Phase**
   - Add vendor to website downloads page
   - Create integration guide
   - Update support matrix

5. **Testing Phase**
   - Validate against vendor hardware
   - Test template imports
   - Verify metrics accuracy

### File Naming Conventions

- Zabbix templates: `zabbix_{vendor}_{model}_{version}.xml`
- Grafana dashboards: `grafana_{vendor}_{model}_{version}.json`
- CSV templates: `csv_{vendor}_{model}_template.csv`
- Documentation: `{vendor}-{model}-guide.md`

## Technology Stack

### Backend
- **Python 3.7+**: Core library
- **requests**: Redfish API communication
- **pandas**: Data manipulation
- **xml.etree**: Zabbix XML generation
- **json**: Grafana JSON generation

### Frontend (GitHub Pages)
- **Jekyll**: Static site generator
- **Bootstrap 5**: Responsive design
- **jQuery**: Interactive elements
- **Highlight.js**: Code syntax highlighting
- **Font Awesome**: Icons

### Monitoring Integration
- **Zabbix 5.0+**: Template format
- **Grafana 8.0+**: Dashboard format
- **Prometheus**: Metrics exporter

## Deployment Strategy

### Phase 1: Core Functionality (v1.0)
- [ ] Redfish client library
- [ ] Basic health checking
- [ ] JSON/XML/CSV export
- [ ] Support for 3-5 major server vendors

### Phase 2: Monitoring Integration (v1.5)
- [ ] Zabbix template generator
- [ ] Grafana dashboard generator
- [ ] Prometheus exporter
- [ ] GitHub Pages website v1

### Phase 3: Extended Coverage (v2.0)
- [ ] Storage device support
- [ ] Network equipment support
- [ ] 10+ vendor support
- [ ] Advanced dashboards

### Phase 4: Enterprise Features (v2.5)
- [ ] Multi-tenancy support
- [ ] Role-based access control
- [ ] Webhook integrations
- [ ] Custom alerting engine

## GitHub Pages Deployment

### Setup Instructions

1. Enable GitHub Pages in repository settings
2. Set source to `docs/` folder or `gh-pages` branch
3. Configure custom domain (optional): `rim.example.com`
4. Use Jekyll for static site generation

### Website Build Process

```bash
# Local development
cd web/
bundle install
bundle exec jekyll serve

# Production build
bundle exec jekyll build
# Output to _site/ directory
```

### Content Organization

```
web/
├── _layouts/
│   ├── default.html
│   ├── download.html
│   └── guide.html
├── _includes/
│   ├── header.html
│   ├── footer.html
│   └── vendor-table.html
├── _data/
│   ├── vendors.yml
│   ├── downloads.yml
│   └── versions.yml
├── assets/
│   ├── css/
│   ├── js/
│   └── downloads/
│       ├── zabbix/
│       ├── grafana/
│       └── csv/
└── pages/
    ├── index.md
    ├── downloads.md
    ├── integration.md
    └── documentation.md
```

## Data Files for Downloads

### Vendor Data (`_data/vendors.yml`)

```yaml
servers:
  - name: Dell EMC
    id: dell
    models:
      - name: PowerEdge R740
        id: r740
        redfish_version: 1.6.0
        downloads:
          zabbix: /assets/downloads/zabbix/servers/dell-poweredge-r740.xml
          grafana: /assets/downloads/grafana/servers/dell-poweredge-r740.json
          csv_template: /assets/downloads/csv/servers/dell-poweredge-r740-template.csv
      - name: PowerEdge R640
        id: r640
        redfish_version: 1.6.0
        downloads:
          zabbix: /assets/downloads/zabbix/servers/dell-poweredge-r640.xml
          grafana: /assets/downloads/grafana/servers/dell-poweredge-r640.json
          csv_template: /assets/downloads/csv/servers/dell-poweredge-r640-template.csv

storage:
  - name: NetApp
    id: netapp
    models:
      - name: FAS8200
        id: fas8200
        redfish_version: 1.4.0
        downloads:
          zabbix: /assets/downloads/zabbix/storage/netapp-fas8200.xml
          grafana: /assets/downloads/grafana/storage/netapp-fas8200.json
          csv_template: /assets/downloads/csv/storage/netapp-fas8200-template.csv

network:
  - name: Cisco
    id: cisco
    models:
      - name: Nexus 9000
        id: nexus9000
        redfish_version: 1.5.0
        downloads:
          zabbix: /assets/downloads/zabbix/network/cisco-nexus9000.xml
          grafana: /assets/downloads/grafana/network/cisco-nexus9000.json
          csv_template: /assets/downloads/csv/network/cisco-nexus9000-template.csv
```

## User Workflow

### For Zabbix Users

1. Visit RIM website
2. Navigate to Downloads > Servers
3. Select vendor and model
4. Download Zabbix template XML
5. Import into Zabbix: Configuration > Templates > Import
6. Create host with Redfish interface
7. Link template to host
8. Configure authentication macros
9. Monitor hardware health

### For Grafana Users

1. Visit RIM website
2. Navigate to Downloads > Servers
3. Select vendor and model
4. Download Grafana dashboard JSON
5. Download CSV template (optional)
6. Import dashboard: Dashboards > Import
7. Configure datasource:
   - Option A: Import CSV data
   - Option B: Use JSON API datasource
   - Option C: Connect to Prometheus exporter
8. Customize dashboard variables
9. Visualize hardware metrics

## CSV Import to Grafana

### Steps for End Users

1. **Generate CSV Data**
   ```bash
   python -m rim export --format csv --device server-01 --output metrics.csv
   ```

2. **Install Grafana CSV Plugin**
   ```bash
   grafana-cli plugins install marcusolsson-csv-datasource
   ```

3. **Configure CSV Datasource in Grafana**
   - Navigate to Configuration > Data Sources
   - Add CSV datasource
   - Point to CSV file location (local or HTTP)
   - Set refresh interval

4. **Import RIM Dashboard**
   - Download dashboard JSON from RIM website
   - Import to Grafana
   - Select CSV datasource
   - Metrics appear automatically

### Alternative: JSON API Datasource

1. **Run RIM API Server**
   ```bash
   python -m rim serve --port 8080
   ```

2. **Configure JSON API Datasource**
   - Install JSON API plugin
   - Point to `http://localhost:8080/metrics`
   - Set authentication if needed

3. **Import Dashboard**
   - Dashboards automatically query JSON API
   - Real-time metric updates

## Support Matrix

| Vendor | Server | Storage | Network | Zabbix | Grafana | Status |
|--------|--------|---------|---------|--------|---------|--------|
| Dell EMC | ✅ | ✅ | ❌ | ✅ | ✅ | Stable |
| HPE | ✅ | ✅ | ❌ | ✅ | ✅ | Stable |
| Cisco | ✅ | ❌ | ✅ | ✅ | ✅ | Beta |
| Lenovo | ✅ | ❌ | ❌ | ✅ | ✅ | Beta |
| Supermicro | ✅ | ❌ | ❌ | ✅ | 🚧 | WIP |
| NetApp | ❌ | ✅ | ❌ | ✅ | ✅ | Stable |
| Pure Storage | ❌ | ✅ | ❌ | 🚧 | 🚧 | Planned |
| Arista | ❌ | ❌ | ✅ | 🚧 | 🚧 | Planned |

## Contributing

We welcome contributions! To add vendor support:

1. Fork the repository
2. Create vendor branch: `vendor/dell-poweredge`
3. Implement vendor class
4. Generate templates
5. Add documentation
6. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) file

## Community

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Wiki**: Extended documentation and examples
- **Discord**: Real-time community support (planned)

## Roadmap

### 2025 Q1
- [x] Core Redfish client library
- [x] Basic health checking
- [ ] Zabbix template generator
- [ ] Initial GitHub Pages site

### 2025 Q2
- [ ] Grafana dashboard generator
- [ ] CSV/JSON export formats
- [ ] 5+ server vendor support
- [ ] Documentation site v1

### 2025 Q3
- [ ] Storage device support
- [ ] Network equipment support
- [ ] Prometheus exporter
- [ ] Advanced Grafana dashboards

### 2025 Q4
- [ ] Community contributions integration
- [ ] Enterprise features
- [ ] API server mode
- [ ] Webhook integrations

## Quick Start for Development

```bash
# Clone repository
git clone https://github.com/m3hr4nn/RIM.git
cd RIM

# Install dependencies
pip install -r requirements.txt

# Run health check
python RHCT.py

# Generate Zabbix template
python -m rim generate-zabbix --vendor dell --model r740

# Generate Grafana dashboard
python -m rim generate-grafana --vendor dell --model r740

# Export metrics to CSV
python -m rim export --format csv --device server-01

# Start local website
cd web/
bundle exec jekyll serve
# Visit http://localhost:4000
```

## Contact

- **Author**: m3hr4nn
- **Repository**: https://github.com/m3hr4nn/RIM
- **Website**: https://m3hr4nn.github.io/RIM (coming soon)
- **Issues**: https://github.com/m3hr4nn/RIM/issues

---

**Built with ❤️ for the infrastructure monitoring community**
