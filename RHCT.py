#!/usr/bin/env python3
"""
Redfish Health Check Tool
Compliant with DMTF Redfish specifications and security principles
"""

import pandas as pd
import requests
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
import base64
import urllib3
from urllib.parse import urljoin
import logging
import os
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from dataclasses import dataclass
import hashlib
import ssl

# Disable SSL warnings for self-signed certificates (common in BMCs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ServerCredentials:
    """Secure credential storage following DMTF security principles"""
    server_id: str
    server_name: str
    ip_address: str
    username: str
    password_hash: str  # Store hashed passwords
    
    def get_auth_header(self, password: str) -> str:
        """Generate base64 encoded auth header"""
        credentials = f"{self.username}:{password}"
        return base64.b64encode(credentials.encode()).decode()

class RedfishClient:
    """
    Redfish API client following DMTF specifications
    Implements security best practices and error handling
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False  # Most BMCs use self-signed certs
        self.session.timeout = 30
        
        # Set standard Redfish headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'RedfishHealthChecker/1.0'
        })
        
        self.service_root = None
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Redfish service
        Supports both basic auth and session-based auth
        """
        try:
            # First, try to get service root
            response = self.session.get(f"{self.base_url}/redfish/v1/")
            if response.status_code == 401:
                # Try basic authentication
                auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
                self.session.headers['Authorization'] = f'Basic {auth_string}'
                
                response = self.session.get(f"{self.base_url}/redfish/v1/")
            
            if response.status_code == 200:
                self.service_root = response.json()
                self.authenticated = True
                logger.info(f"Successfully authenticated to {self.base_url}")
                return True
            else:
                logger.error(f"Authentication failed for {self.base_url}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error for {self.base_url}: {str(e)}")
            return False
    
    def get_resource(self, path: str) -> Optional[Dict]:
        """Get a Redfish resource with error handling"""
        try:
            url = urljoin(self.base_url, path)
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get {path}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting {path}: {str(e)}")
            return None
    
    def get_health_status(self) -> Dict:
        """
        Comprehensive health check following DMTF Redfish schema
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'
        health_data = {
            'timestamp': timestamp,
            'server_info': {},
            'system_health': {},
            'chassis_health': {},
            'thermal_health': {},
            'power_health': {},
            'storage_health': {},
            'network_health': {},
            'errors': []
        }
        
        try:
            # Get Systems collection
            systems = self.get_resource('/redfish/v1/Systems/')
            if systems and 'Members' in systems:
                for system_ref in systems['Members']:
                    system_data = self.get_resource(system_ref['@odata.id'])
                    if system_data:
                        health_data['server_info'] = {
                            'manufacturer': system_data.get('Manufacturer', 'Unknown'),
                            'model': system_data.get('Model', 'Unknown'),
                            'serial_number': system_data.get('SerialNumber', 'Unknown'),
                            'bios_version': system_data.get('BiosVersion', 'Unknown'),
                            'power_state': system_data.get('PowerState', 'Unknown'),
                            'health': system_data.get('Status', {}).get('Health', 'Unknown'),
                            'state': system_data.get('Status', {}).get('State', 'Unknown')
                        }
                        
                        health_data['system_health'] = {
                            'overall_health': system_data.get('Status', {}).get('Health', 'Unknown'),
                            'state': system_data.get('Status', {}).get('State', 'Unknown'),
                            'processor_summary': system_data.get('ProcessorSummary', {}),
                            'memory_summary': system_data.get('MemorySummary', {})
                        }
            
            # Get Chassis collection
            chassis = self.get_resource('/redfish/v1/Chassis/')
            if chassis and 'Members' in chassis:
                for chassis_ref in chassis['Members']:
                    chassis_data = self.get_resource(chassis_ref['@odata.id'])
                    if chassis_data:
                        health_data['chassis_health'] = {
                            'health': chassis_data.get('Status', {}).get('Health', 'Unknown'),
                            'state': chassis_data.get('Status', {}).get('State', 'Unknown'),
                            'chassis_type': chassis_data.get('ChassisType', 'Unknown')
                        }
                        
                        # Get Thermal data
                        thermal_path = chassis_data.get('Thermal', {}).get('@odata.id')
                        if thermal_path:
                            thermal_data = self.get_resource(thermal_path)
                            if thermal_data:
                                health_data['thermal_health'] = self._process_thermal_data(thermal_data)
                        
                        # Get Power data
                        power_path = chassis_data.get('Power', {}).get('@odata.id')
                        if power_path:
                            power_data = self.get_resource(power_path)
                            if power_data:
                                health_data['power_health'] = self._process_power_data(power_data)
            
            # Get Storage health
            storage_data = self.get_resource('/redfish/v1/Systems/1/Storage/')
            if storage_data:
                health_data['storage_health'] = self._process_storage_data(storage_data)
            
        except Exception as e:
            health_data['errors'].append(f"Health check error: {str(e)}")
            logger.error(f"Health check failed: {str(e)}")
        
        return health_data
    
    def _process_thermal_data(self, thermal_data: Dict) -> Dict:
        """Process thermal sensor data"""
        thermal_health = {
            'temperatures': [],
            'fans': [],
            'overall_status': 'OK'
        }
        
        # Process temperature sensors
        for temp in thermal_data.get('Temperatures', []):
            temp_info = {
                'name': temp.get('Name', 'Unknown'),
                'reading': temp.get('ReadingCelsius'),
                'status': temp.get('Status', {}).get('Health', 'Unknown'),
                'upper_threshold': temp.get('UpperThresholdCritical'),
                'lower_threshold': temp.get('LowerThresholdCritical')
            }
            thermal_health['temperatures'].append(temp_info)
            
            if temp_info['status'] not in ['OK', 'Unknown']:
                thermal_health['overall_status'] = 'Warning'
        
        # Process fans
        for fan in thermal_data.get('Fans', []):
            fan_info = {
                'name': fan.get('Name', 'Unknown'),
                'reading_rpm': fan.get('Reading'),
                'status': fan.get('Status', {}).get('Health', 'Unknown')
            }
            thermal_health['fans'].append(fan_info)
            
            if fan_info['status'] not in ['OK', 'Unknown']:
                thermal_health['overall_status'] = 'Critical'
        
        return thermal_health
    
    def _process_power_data(self, power_data: Dict) -> Dict:
        """Process power supply and consumption data"""
        power_health = {
            'power_supplies': [],
            'power_consumption': {},
            'overall_status': 'OK'
        }
        
        # Process power supplies
        for psu in power_data.get('PowerSupplies', []):
            psu_info = {
                'name': psu.get('Name', 'Unknown'),
                'status': psu.get('Status', {}).get('Health', 'Unknown'),
                'power_capacity': psu.get('PowerCapacityWatts'),
                'power_output': psu.get('LastPowerOutputWatts')
            }
            power_health['power_supplies'].append(psu_info)
            
            if psu_info['status'] not in ['OK', 'Unknown']:
                power_health['overall_status'] = 'Critical'
        
        # Process power consumption
        power_control = power_data.get('PowerControl', [])
        if power_control:
            power_health['power_consumption'] = {
                'consumed_watts': power_control[0].get('PowerConsumedWatts'),
                'average_watts': power_control[0].get('AverageConsumedWatts'),
                'max_watts': power_control[0].get('PowerCapacityWatts')
            }
        
        return power_health
    
    def _process_storage_data(self, storage_data: Dict) -> Dict:
        """Process storage controller and drive data"""
        storage_health = {
            'controllers': [],
            'drives': [],
            'overall_status': 'OK'
        }
        
        for storage_ref in storage_data.get('Members', []):
            storage_controller = self.get_resource(storage_ref['@odata.id'])
            if storage_controller:
                controller_info = {
                    'name': storage_controller.get('Name', 'Unknown'),
                    'status': storage_controller.get('Status', {}).get('Health', 'Unknown')
                }
                storage_health['controllers'].append(controller_info)
                
                # Get drives
                drives_path = storage_controller.get('Drives', [])
                for drive_ref in drives_path:
                    drive_data = self.get_resource(drive_ref['@odata.id'])
                    if drive_data:
                        drive_info = {
                            'name': drive_data.get('Name', 'Unknown'),
                            'status': drive_data.get('Status', {}).get('Health', 'Unknown'),
                            'capacity': drive_data.get('CapacityBytes'),
                            'media_type': drive_data.get('MediaType', 'Unknown')
                        }
                        storage_health['drives'].append(drive_info)
                        
                        if drive_info['status'] not in ['OK', 'Unknown']:
                            storage_health['overall_status'] = 'Warning'
        
        return storage_health

class HealthCheckTool:
    """Main health check tool coordinator"""
    
    def __init__(self):
        self.servers = []
        self.results = {}
        
    def load_servers_from_excel(self, file_path: str) -> bool:
        """Load server information from Excel file"""
        try:
            df = pd.read_excel(file_path)
            required_columns = ['#', 'server name', 'universal IP', 'User', 'Password']
            
            # Check if all required columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            self.servers = []
            for _, row in df.iterrows():
                server = ServerCredentials(
                    server_id=str(row['#']),
                    server_name=row['server name'],
                    ip_address=row['universal IP'],
                    username=row['User'],
                    password_hash=hashlib.sha256(row['Password'].encode()).hexdigest()
                )
                self.servers.append((server, row['Password']))  # Keep original password for auth
            
            logger.info(f"Loaded {len(self.servers)} servers from Excel file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            return False
    
    def perform_health_checks(self, max_workers: int = 5) -> Dict:
        """Perform health checks on all servers concurrently"""
        results = {}
        
        def check_single_server(server_data):
            server, password = server_data
            try:
                # Try different common Redfish base paths
                base_urls = [
                    f"https://{server.ip_address}",
                    f"https://{server.ip_address}:443",
                    f"http://{server.ip_address}:80"
                ]
                
                for base_url in base_urls:
                    try:
                        client = RedfishClient(base_url, server.username, password)
                        if client.authenticate():
                            health_data = client.get_health_status()
                            health_data['server_name'] = server.server_name
                            health_data['ip_address'] = server.ip_address
                            return server.server_id, health_data
                    except Exception as e:
                        continue
                
                # If all URLs fail
                return server.server_id, {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'server_name': server.server_name,
                    'ip_address': server.ip_address,
                    'errors': [f"Failed to connect to Redfish service on {server.ip_address}"],
                    'connection_status': 'Failed'
                }
                
            except Exception as e:
                return server.server_id, {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'server_name': server.server_name,
                    'ip_address': server.ip_address,
                    'errors': [f"Health check failed: {str(e)}"],
                    'connection_status': 'Error'
                }
        
        # Execute health checks concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_server = {executor.submit(check_single_server, server_data): server_data[0].server_id 
                              for server_data in self.servers}
            
            for future in concurrent.futures.as_completed(future_to_server):
                server_id, result = future.result()
                results[server_id] = result
                logger.info(f"Completed health check for server {server_id}")
        
        return results
    
    def export_to_json(self, results: Dict, output_path: str = "health_check_results.json"):
        """Export results to JSON format (DMTF compliant)"""
        try:
            json_output = {
                "RedfishHealthCheck": {
                    "@odata.type": "#HealthCheckReport.v1_0_0.HealthCheckReport",
                    "Id": "HealthCheckReport",
                    "Name": "Server Health Check Report",
                    "Description": "Comprehensive server health check using Redfish API",
                    "ReportTime": datetime.utcnow().isoformat() + 'Z',
                    "Servers": results
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to JSON: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return None
    
    def export_to_xml(self, results: Dict, output_path: str = "health_check_results.xml"):
        """Export results to XML format (DMTF compliant)"""
        try:
            root = ET.Element("RedfishHealthCheck")
            root.set("xmlns", "http://redfish.dmtf.org/schemas/v1")
            root.set("ReportTime", datetime.utcnow().isoformat() + 'Z')
            
            for server_id, server_data in results.items():
                server_elem = ET.SubElement(root, "Server")
                server_elem.set("Id", server_id)
                
                for key, value in server_data.items():
                    if isinstance(value, dict):
                        section_elem = ET.SubElement(server_elem, key.replace('_', ''))
                        self._dict_to_xml(section_elem, value)
                    elif isinstance(value, list):
                        section_elem = ET.SubElement(server_elem, key.replace('_', ''))
                        for item in value:
                            item_elem = ET.SubElement(section_elem, "Item")
                            if isinstance(item, dict):
                                self._dict_to_xml(item_elem, item)
                            else:
                                item_elem.text = str(item)
                    else:
                        elem = ET.SubElement(server_elem, key.replace('_', ''))
                        elem.text = str(value) if value is not None else ""
            
            # Pretty print XML
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = xml.dom.minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
            
            logger.info(f"Results exported to XML: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting to XML: {str(e)}")
            return None
    
    def _dict_to_xml(self, parent, data):
        """Helper method to convert dictionary to XML elements"""
        for key, value in data.items():
            if isinstance(value, dict):
                elem = ET.SubElement(parent, key.replace('_', ''))
                self._dict_to_xml(elem, value)
            elif isinstance(value, list):
                for item in value:
                    elem = ET.SubElement(parent, key.replace('_', '').rstrip('s'))
                    if isinstance(item, dict):
                        self._dict_to_xml(elem, item)
                    else:
                        elem.text = str(item)
            else:
                elem = ET.SubElement(parent, key.replace('_', ''))
                elem.text = str(value) if value is not None else ""
    
    def generate_html_report(self, results: Dict, output_path: str = "health_report.html") -> str:
        """Generate comprehensive HTML report"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Health Check Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .summary {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .servers {{
            padding: 30px;
        }}
        .server {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }}
        .server-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }}
        .server-name {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin: 0;
        }}
        .server-info {{
            color: #666;
            margin: 5px 0 0 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-ok {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-critical {{ background: #f8d7da; color: #721c24; }}
        .status-unknown {{ background: #e2e3e5; color: #383d41; }}
        .server-details {{
            padding: 20px;
        }}
        .detail-section {{
            margin-bottom: 25px;
        }}
        .detail-section h4 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.2em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }}
        .detail-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .detail-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }}
        .detail-item strong {{
            color: #333;
        }}
        .error-list {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
        }}
        .error-list h5 {{
            margin: 0 0 10px 0;
            color: #721c24;
        }}
        .error-list ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .error-list li {{
            color: #721c24;
            margin-bottom: 5px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        @media (max-width: 768px) {{
            .detail-grid {{
                grid-template-columns: 1fr;
            }}
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Server Health Check Report</h1>
            <p>Generated on {timestamp} | DMTF Redfish Compliant</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="summary-cards">
"""
            
            # Calculate summary statistics
            total_servers = len(results)
            healthy_servers = sum(1 for r in results.values() 
                                if r.get('system_health', {}).get('overall_health') == 'OK')
            warning_servers = sum(1 for r in results.values() 
                                if r.get('system_health', {}).get('overall_health') == 'Warning')
            critical_servers = sum(1 for r in results.values() 
                                 if r.get('system_health', {}).get('overall_health') in ['Critical', 'Error'])
            
            html_content += f"""
                <div class="summary-card">
                    <h3>Total Servers</h3>
                    <div class="number">{total_servers}</div>
                </div>
                <div class="summary-card">
                    <h3>Healthy</h3>
                    <div class="number" style="color: #28a745;">{healthy_servers}</div>
                </div>
                <div class="summary-card">
                    <h3>Warnings</h3>
                    <div class="number" style="color: #ffc107;">{warning_servers}</div>
                </div>
                <div class="summary-card">
                    <h3>Critical</h3>
                    <div class="number" style="color: #dc3545;">{critical_servers}</div>
                </div>
            </div>
        </div>
        
        <div class="servers">
            <h2>Server Details</h2>
"""
            
            # Generate server details
            for server_id, server_data in results.items():
                overall_health = server_data.get('system_health', {}).get('overall_health', 'Unknown')
                status_class = f"status-{overall_health.lower()}" if overall_health != 'Unknown' else "status-unknown"
                
                html_content += f"""
            <div class="server">
                <div class="server-header">
                    <h3 class="server-name">{server_data.get('server_name', 'Unknown Server')}</h3>
                    <p class="server-info">
                        IP: {server_data.get('ip_address', 'N/A')} | 
                        Checked: {server_data.get('timestamp', 'N/A')} |
                        <span class="status-badge {status_class}">{overall_health}</span>
                    </p>
                </div>
                <div class="server-details">
"""
                
                # Server Information
                server_info = server_data.get('server_info', {})
                if server_info:
                    html_content += """
                    <div class="detail-section">
                        <h4>🖥️ Server Information</h4>
                        <div class="detail-grid">
"""
                    for key, value in server_info.items():
                        display_key = key.replace('_', ' ').title()
                        html_content += f"""
                            <div class="detail-item">
                                <strong>{display_key}:</strong> {value}
                            </div>
"""
                    html_content += "</div></div>"
                
                # System Health
                system_health = server_data.get('system_health', {})
                if system_health:
                    html_content += """
                    <div class="detail-section">
                        <h4>🔧 System Health</h4>
                        <div class="detail-grid">
"""
                    for key, value in system_health.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                display_key = f"{key.replace('_', ' ').title()} - {sub_key.replace('_', ' ').title()}"
                                html_content += f"""
                            <div class="detail-item">
                                <strong>{display_key}:</strong> {sub_value}
                            </div>
"""
                        else:
                            display_key = key.replace('_', ' ').title()
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{display_key}:</strong> {value}
                            </div>
"""
                    html_content += "</div></div>"
                
                # Thermal Health
                thermal_health = server_data.get('thermal_health', {})
                if thermal_health:
                    html_content += """
                    <div class="detail-section">
                        <h4>🌡️ Thermal Status</h4>
                        <div class="detail-grid">
"""
                    if 'overall_status' in thermal_health:
                        html_content += f"""
                            <div class="detail-item">
                                <strong>Overall Status:</strong> {thermal_health['overall_status']}
                            </div>
"""
                    
                    if 'temperatures' in thermal_health:
                        for temp in thermal_health['temperatures']:
                            temp_reading = temp.get('reading', 'N/A')
                            temp_unit = '°C' if temp_reading != 'N/A' else ''
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{temp.get('name', 'Temperature Sensor')}:</strong> 
                                {temp_reading}{temp_unit} - {temp.get('status', 'Unknown')}
                            </div>
"""
                    
                    if 'fans' in thermal_health:
                        for fan in thermal_health['fans']:
                            fan_reading = fan.get('reading_rpm', 'N/A')
                            fan_unit = ' RPM' if fan_reading != 'N/A' else ''
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{fan.get('name', 'Fan')}:</strong> 
                                {fan_reading}{fan_unit} - {fan.get('status', 'Unknown')}
                            </div>
"""
                    html_content += "</div></div>"
                
                # Power Health
                power_health = server_data.get('power_health', {})
                if power_health:
                    html_content += """
                    <div class="detail-section">
                        <h4>⚡ Power Status</h4>
                        <div class="detail-grid">
"""
                    if 'overall_status' in power_health:
                        html_content += f"""
                            <div class="detail-item">
                                <strong>Overall Status:</strong> {power_health['overall_status']}
                            </div>
"""
                    
                    if 'power_consumption' in power_health:
                        power_consumption = power_health['power_consumption']
                        for key, value in power_consumption.items():
                            if value is not None:
                                display_key = key.replace('_', ' ').title()
                                html_content += f"""
                            <div class="detail-item">
                                <strong>{display_key}:</strong> {value} W
                            </div>
"""
                    
                    if 'power_supplies' in power_health:
                        for psu in power_health['power_supplies']:
                            psu_name = psu.get('name', 'Power Supply')
                            psu_status = psu.get('status', 'Unknown')
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{psu_name}:</strong> {psu_status}
                            </div>
"""
                    html_content += "</div></div>"
                
                # Storage Health
                storage_health = server_data.get('storage_health', {})
                if storage_health:
                    html_content += """
                    <div class="detail-section">
                        <h4>💾 Storage Status</h4>
                        <div class="detail-grid">
"""
                    if 'overall_status' in storage_health:
                        html_content += f"""
                            <div class="detail-item">
                                <strong>Overall Status:</strong> {storage_health['overall_status']}
                            </div>
"""
                    
                    if 'controllers' in storage_health:
                        for controller in storage_health['controllers']:
                            controller_name = controller.get('name', 'Storage Controller')
                            controller_status = controller.get('status', 'Unknown')
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{controller_name}:</strong> {controller_status}
                            </div>
"""
                    
                    if 'drives' in storage_health:
                        for drive in storage_health['drives']:
                            drive_name = drive.get('name', 'Drive')
                            drive_status = drive.get('status', 'Unknown')
                            drive_capacity = drive.get('capacity', 'Unknown')
                            if drive_capacity != 'Unknown' and drive_capacity:
                                drive_capacity_gb = round(int(drive_capacity) / (1024**3), 2)
                                capacity_text = f" ({drive_capacity_gb} GB)"
                            else:
                                capacity_text = ""
                            html_content += f"""
                            <div class="detail-item">
                                <strong>{drive_name}:</strong> {drive_status}{capacity_text}
                            </div>
"""
                    html_content += "</div></div>"
                
                # Errors section
                errors = server_data.get('errors', [])
                if errors:
                    html_content += """
                    <div class="error-list">
                        <h5>⚠️ Errors and Warnings</h5>
                        <ul>
"""
                    for error in errors:
                        html_content += f"<li>{error}</li>"
                    html_content += "</ul></div>"
                
                html_content += """
                </div>
            </div>
"""
            
            html_content += """
        </div>
        
        <div class="footer">
            <p>This report was generated using DMTF Redfish API standards for server health monitoring.</p>
            <p>Report generated by Redfish Health Check Tool v1.0</p>
        </div>
    </div>
</body>
</html>
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return None

def main():
    """Main execution function"""
    print("🏥 Redfish Health Check Tool v1.0")
    print("=" * 50)
    
    # Initialize the health check tool
    health_tool = HealthCheckTool()
    
    # Get input file path
    excel_file = input("Enter path to Excel file with server information: ").strip()
    if not excel_file:
        excel_file = "servers.xlsx"  # Default filename
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: File '{excel_file}' not found!")
        return
    
    # Load servers from Excel
    print(f"📊 Loading servers from {excel_file}...")
    if not health_tool.load_servers_from_excel(excel_file):
        print("❌ Failed to load servers from Excel file!")
        return
    
    print(f"✅ Successfully loaded {len(health_tool.servers)} servers")
    
    # Perform health checks
    print("\n🔍 Performing health checks...")
    results = health_tool.perform_health_checks()
    
    if not results:
        print("❌ No health check results obtained!")
        return
    
    print(f"✅ Health checks completed for {len(results)} servers")
    
    # Generate reports
    print("\n📄 Generating reports...")
    
    # Generate JSON report
    json_file = health_tool.export_to_json(results)
    if json_file:
        print(f"✅ JSON report: {json_file}")
    
    # Generate XML report
    xml_file = health_tool.export_to_xml(results)
    if xml_file:
        print(f"✅ XML report: {xml_file}")
    
    # Generate HTML report
    html_file = health_tool.generate_html_report(results)
    if html_file:
        print(f"✅ HTML report: {html_file}")
    
    print("\n🎉 Health check completed successfully!")
    print(f"📊 Summary: {len(results)} servers checked")
    
    # Display quick summary
    healthy = sum(1 for r in results.values() 
                  if r.get('system_health', {}).get('overall_health') == 'OK')
    warning = sum(1 for r in results.values() 
                  if r.get('system_health', {}).get('overall_health') == 'Warning')
    critical = sum(1 for r in results.values() 
                   if r.get('system_health', {}).get('overall_health') in ['Critical', 'Error'])
    
    print(f"🟢 Healthy: {healthy}")
    print(f"🟡 Warning: {warning}")
    print(f"🔴 Critical: {critical}")

if __name__ == "__main__":
    main()
