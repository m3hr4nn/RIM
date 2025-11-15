# Vendor Data Gathering Guide

This guide explains how to gather vendor-specific Redfish implementation details and develop monitoring configurations for RIM (RedFish Infrastructure Monitor).

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Finding Vendor Documentation](#finding-vendor-documentation)
4. [Accessing Redfish APIs](#accessing-redfish-apis)
5. [Exploring Vendor Endpoints](#exploring-vendor-endpoints)
6. [Testing Tools](#testing-tools)
7. [Vendor-Specific Resources](#vendor-specific-resources)
8. [Common Challenges](#common-challenges)
9. [Best Practices](#best-practices)

## Overview

Each hardware vendor implements Redfish slightly differently, with vendor-specific extensions (OEM data) and unique endpoint structures. To create effective monitoring configurations, you need to:

1. Access actual hardware or vendor simulators
2. Explore the Redfish API structure
3. Identify key metrics and their locations
4. Document vendor-specific quirks
5. Test configurations thoroughly

## Prerequisites

### Required Access

- **Physical Hardware**: Access to the actual server/storage/network device
- **OR Redfish Simulator**: Vendor-provided Redfish simulator
- **OR Virtual Environment**: VMware/VirtualBox with vendor management software

### Required Credentials

- Management interface credentials (BMC/iDRAC/iLO/CIMC)
- Network access to the management interface
- Appropriate permissions for Redfish API access

### Required Tools

- cURL or wget for HTTP requests
- Python with requests library
- Postman or similar API testing tool (optional)
- Browser for web-based interface exploration

## Finding Vendor Documentation

### Dell EMC

**Official Resources:**
- **Redfish API Guide**: https://www.dell.com/support/kbdoc/en-us/000177876/how-to-use-the-redfish-api-on-poweredge-servers
- **iDRAC REST API**: Search Dell Support for "iDRAC Redfish"
- **Developer Portal**: https://developer.dell.com/apis

**What to Download:**
```
1. Dell EMC PowerEdge Redfish API Reference Guide
2. iDRAC9 Redfish API Guide (PDF)
3. Dell EMC OpenManage Python SDK documentation
```

**How to Access:**
1. Visit Dell Support website
2. Search for your specific model (e.g., "PowerEdge R740 Redfish")
3. Download the latest iDRAC firmware documentation
4. Check the "Manuals & Documents" section

### HPE (Hewlett Packard Enterprise)

**Official Resources:**
- **iLO RESTful API**: https://www.hpe.com/us/en/servers/restful-api.html
- **iLO 5 Documentation**: https://support.hpe.com/
- **Developer Portal**: https://developer.hpe.com/

**What to Download:**
```
1. HPE iLO 5 Redfish API Reference
2. HPE Redfish API Data Model Reference
3. iLOrest Tool Documentation
```

**How to Access:**
1. Visit HPE Support Center
2. Search for "iLO Redfish API"
3. Filter by your server generation (Gen10, Gen10 Plus, etc.)
4. Download API documentation

### Cisco

**Official Resources:**
- **CIMC API Guide**: https://www.cisco.com/c/en/us/support/servers-unified-computing/index.html
- **Redfish Implementation**: Search for "Cisco CIMC Redfish"
- **DevNet**: https://developer.cisco.com/

**What to Download:**
```
1. Cisco UCS C-Series Redfish API Guide
2. CIMC Configuration Guide
3. Cisco IMC Supervisor Documentation
```

**How to Access:**
1. Visit Cisco DevNet or Support
2. Navigate to UCS documentation
3. Look for "Programmability" or "API" sections

### Lenovo

**Official Resources:**
- **XClarity Administrator**: https://sysmgt.lenovofiles.com/help/index.jsp
- **Redfish API Guide**: Search Lenovo Support for "Redfish"

**What to Download:**
```
1. Lenovo XClarity Administrator Redfish API
2. ThinkSystem Server Management Guide
3. Lenovo BMC Redfish Implementation
```

### Supermicro

**Official Resources:**
- **IPMI and Redfish**: https://www.supermicro.com/en/solutions/management-software
- **Redfish Implementation**: Contact Supermicro support or check server documentation

**What to Download:**
```
1. SuperServer Redfish API Guide (if available)
2. IPMI User Guide
3. BMC firmware release notes
```

### NetApp

**Official Resources:**
- **ONTAP REST API**: https://docs.netapp.com/us-en/ontap-automation/
- **Developer Portal**: https://devnet.netapp.com/

**What to Download:**
```
1. ONTAP REST API Documentation
2. NetApp Storage System Redfish Implementation
3. API Reference Guide
```

## Accessing Redfish APIs

### Step 1: Verify Redfish Support

First, verify that your device supports Redfish:

```bash
# Check Redfish root endpoint
curl -k -u admin:password https://DEVICE_IP/redfish/v1/

# Expected response should include:
{
  "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
  "@odata.id": "/redfish/v1/",
  "@odata.type": "#ServiceRoot.v1_5_0.ServiceRoot",
  "RedfishVersion": "1.6.0",
  "Name": "Root Service",
  ...
}
```

### Step 2: Explore the Service Root

```bash
# Get the service root to see available endpoints
curl -k -u admin:password https://DEVICE_IP/redfish/v1/ | python -m json.tool
```

Key sections to look for:
- `Systems` - Server/compute systems
- `Chassis` - Physical enclosures
- `Managers` - Management controllers (BMC/iDRAC/iLO)
- `SessionService` - Authentication
- `AccountService` - User management
- `UpdateService` - Firmware updates

### Step 3: Navigate the Resource Tree

Follow the `@odata.id` links to explore:

```bash
# Get systems
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Systems

# Get first system details
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Systems/System.Embedded.1

# Get chassis
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Chassis

# Get thermal data
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Chassis/System.Embedded.1/Thermal

# Get power data
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Chassis/System.Embedded.1/Power
```

## Exploring Vendor Endpoints

### Key Metrics to Identify

For each vendor, document the following:

#### 1. Thermal Metrics

- Temperature sensor locations
- Fan locations and readings
- Threshold values (warning/critical)
- Sensor naming conventions

Example exploration:
```bash
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Chassis/CHASSIS_ID/Thermal | python -m json.tool > thermal.json
```

Look for:
```json
{
  "Temperatures": [
    {
      "Name": "CPU1 Temp",
      "ReadingCelsius": 45,
      "UpperThresholdCritical": 85,
      "Status": {"Health": "OK"}
    }
  ],
  "Fans": [
    {
      "Name": "Fan1",
      "Reading": 3500,
      "ReadingUnits": "RPM",
      "Status": {"Health": "OK"}
    }
  ]
}
```

#### 2. Power Metrics

- Power consumption readings
- Power supply status
- Voltage readings
- Capacity information

```bash
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Chassis/CHASSIS_ID/Power | python -m json.tool > power.json
```

#### 3. Storage Metrics

- Storage controllers
- Drive information
- RAID status
- Drive health

```bash
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Systems/SYSTEM_ID/Storage | python -m json.tool > storage.json
```

#### 4. Network Metrics

- Network interfaces
- Link status
- Bandwidth information

```bash
curl -k -u admin:password https://DEVICE_IP/redfish/v1/Systems/SYSTEM_ID/EthernetInterfaces | python -m json.tool > network.json
```

### Vendor-Specific OEM Extensions

Most vendors add custom data under `Oem` sections:

**Dell Example:**
```json
{
  "Oem": {
    "Dell": {
      "@odata.type": "#DellOem.v1_0_0.DellOemResources",
      "DellAttributes": {...}
    }
  }
}
```

**HPE Example:**
```json
{
  "Oem": {
    "Hpe": {
      "@odata.type": "#HpeiLOSSO.v2_0_0.HpeiLOSSO",
      ...
    }
  }
}
```

Document these OEM extensions as they often contain valuable metrics.

## Testing Tools

### 1. RIM Validation Script

Use the built-in validation tool:

```bash
python tools/validate_redfish.py --host DEVICE_IP --user admin --password pass
```

### 2. Postman Collection

Import Redfish API collections:
1. Open Postman
2. Import collection
3. Set base URL to `https://DEVICE_IP/redfish/v1/`
4. Configure authentication (Basic Auth)
5. Explore endpoints

### 3. Python Script

Create a simple exploration script:

```python
from core import RedfishClient
import json

client = RedfishClient(
    host="DEVICE_IP",
    username="admin",
    password="password"
)

# Test connection
if client.test_connection():
    print("✓ Connection successful")

# Get vendor info
vendor_info = client.get_vendor_info()
print(f"Vendor: {vendor_info['vendor']}")
print(f"Model: {vendor_info['model']}")

# Get thermal data
thermal = client.get_thermal()
with open('thermal_data.json', 'w') as f:
    json.dump(thermal, f, indent=2)

# Get power data
power = client.get_power()
with open('power_data.json', 'w') as f:
    json.dump(power, f, indent=2)

client.close()
```

### 4. Vendor Simulators

#### Dell iDRAC Simulator
- Not publicly available, request from Dell
- Check Dell EMC World events for simulator access

#### HPE iLO Simulator
- Download from HPE Support
- Available as virtual appliance

#### Cisco DevNet Sandbox
- Free access to UCS simulators
- https://devnetsandbox.cisco.com/

## Vendor-Specific Resources

### Dell EMC Specific

**Simulator Access:**
- Contact Dell sales or support for iDRAC simulator
- Use Dell EMC Virtual Labs (requires registration)

**Key Endpoints:**
```
/redfish/v1/Managers/iDRAC.Embedded.1/Attributes
/redfish/v1/Systems/System.Embedded.1/Attributes
/redfish/v1/Managers/iDRAC.Embedded.1/Oem/Dell/DellLCService
```

**Unique Features:**
- Detailed iDRAC attributes
- Lifecycle controller integration
- RAID controller details
- NIC statistics

### HPE Specific

**Simulator:**
- Download iLO 5 simulator from HPE Support
- Deploy as virtual machine

**Key Endpoints:**
```
/redfish/v1/Systems/1/
/redfish/v1/Managers/1/
/redfish/v1/Chassis/1/Thermal/
/redfish/v1/Chassis/1/Power/
```

**Unique Features:**
- iLO Advanced features
- Smart Storage information
- Embedded diagnostics
- Historical data

### Cisco Specific

**DevNet Resources:**
- Free sandbox environments
- API documentation
- Code samples

**Key Endpoints:**
```
/redfish/v1/Systems/FCH{SERIAL}/
/redfish/v1/Chassis/1/
/redfish/v1/Managers/CIMC/
```

**Unique Features:**
- UCS-specific inventory
- Fabric interconnect data
- Integrated network adapters

## Common Challenges

### Challenge 1: Different Redfish Versions

**Problem:** Vendors implement different Redfish versions

**Solution:**
- Check `RedfishVersion` in service root
- Implement version-specific handling
- Test against multiple firmware versions

### Challenge 2: Inconsistent Naming

**Problem:** Sensor names vary widely

**Solution:**
- Create vendor-specific name parsers
- Document naming patterns
- Use flexible matching

### Challenge 3: Missing Metrics

**Problem:** Some expected metrics not available

**Solution:**
- Check OEM sections for vendor-specific metrics
- Review firmware version (upgrade if needed)
- Contact vendor support for API limitations

### Challenge 4: Authentication Issues

**Problem:** Different auth methods across vendors

**Solution:**
- Support both Basic Auth and session-based auth
- Implement token refresh for long-running sessions
- Handle SSL/TLS certificate variations

### Challenge 5: Rate Limiting

**Problem:** Too many requests trigger throttling

**Solution:**
- Implement request caching
- Add delays between requests
- Batch requests where possible

## Best Practices

### 1. Documentation

Create a vendor profile document:

```markdown
# Vendor: Dell EMC
## Model: PowerEdge R740
## Firmware: iDRAC 4.40.00.00

### Redfish Version: 1.6.0

### Endpoints Tested:
- /redfish/v1/ ✓
- /redfish/v1/Systems/System.Embedded.1 ✓
- /redfish/v1/Chassis/System.Embedded.1/Thermal ✓
- /redfish/v1/Chassis/System.Embedded.1/Power ✓

### Metrics Available:
#### Thermal:
- CPU temperatures (2x)
- Inlet temperature
- Exhaust temperature
- System board temperature
- Fans (6x)

#### Power:
- Total power consumption
- PSU status (2x)
- PSU output power

### OEM Extensions:
- DellAttributes available
- RAID controller details in Storage
```

### 2. Versioning

Track firmware versions that work:

```
Dell iDRAC 4.40+ - Tested ✓
HPE iLO 5 v2.30+ - Tested ✓
Cisco CIMC 4.1+ - Planned
```

### 3. Test Coverage

- Test against multiple hardware configurations
- Verify with different firmware versions
- Test error conditions (unplugged PSU, etc.)
- Validate across server generations

### 4. Community Collaboration

- Share findings in GitHub Discussions
- Contribute vendor implementations
- Report bugs with specific firmware versions
- Share Redfish response samples (sanitized)

## Next Steps

After gathering vendor data:

1. **Implement Vendor Class**
   - Create `/core/vendors/your_vendor.py`
   - Extend `BaseVendor` class
   - Implement required methods

2. **Generate Templates**
   - Create Zabbix template
   - Create Grafana dashboard
   - Export CSV template

3. **Test**
   - Run against real hardware
   - Validate metrics accuracy
   - Test template imports

4. **Document**
   - Add to README
   - Create integration guide
   - Update support matrix

5. **Contribute**
   - Submit pull request
   - Share in community
   - Help others with same vendor

## Need Help?

- **GitHub Issues**: Report problems or ask questions
- **GitHub Discussions**: Share experiences and tips
- **Documentation**: Check the main docs
- **Community**: Join discussions with other contributors

## Resources

### General Redfish Resources

- **DMTF Redfish Specification**: https://www.dmtf.org/standards/redfish
- **Redfish Developer Hub**: https://redfish.dmtf.org/
- **Redfish Mockup Server**: https://github.com/DMTF/Redfish-Mockup-Server
- **Redfish Tools**: https://github.com/DMTF/Redfish-Tools

### Vendor Contact

If you can't find documentation:

1. Contact vendor technical support
2. Request API documentation
3. Ask about developer programs
4. Check for NDA-protected resources
5. Attend vendor technical conferences

---

**Remember**: Always sanitize credentials and sensitive data before sharing API responses or documentation!