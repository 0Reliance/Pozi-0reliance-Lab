---
title: Network Switch Configuration
description: Complete guide for homelab switch setup and VLAN configuration
---

# Network Switch Configuration

Managed switches form the backbone of any serious homelab network, providing connectivity, segmentation, and performance optimization. This guide covers switch selection, configuration, and advanced features.

## 🌐 Switch Fundamentals

### Switch Types Comparison
```bash
# Switch Categories and Use Cases

Unmanaged Switch:
  Cost: $20-100
  Use Case: Basic connectivity, small networks
  Features: Plug-and-play, auto-negotiation
  Limitations: No VLANs, no management
  Recommendation: Beginners, temporary setups

Smart Switch:
  Cost: $100-300
  Use Case: Small business, advanced homelabs
  Features: Basic management, some VLAN support
  Management: Web interface, basic monitoring
  Recommendation: Growing networks

Managed Switch:
  Cost: $300-2000+
  Use Case: Production homelabs, multi-tenant
  Features: Full VLAN support, L3 routing, monitoring
  Management: CLI, web, SNMP, API
  Recommendation: Serious homelabs

Core Switch (L3):
  Cost: $1000-5000+
  Use Case: Data center, large networks
  Features: Routing, advanced protocols, high throughput
  Management: Full network OS
  Recommendation: Enterprise homelabs
```

### Hardware Selection Criteria

#### Port Configuration
```bash
# Port Types and Recommendations

Gigabit Copper (1GbE):
  Use Cases: Workstations, basic servers
  Cable: Cat6 or better
  Distance: Up to 100 meters
  Power: PoE+ available on some ports

10Gigabit Copper (10GbE):
  Use Cases: Storage, virtualization hosts
  Cable: Cat6a or Cat7
  Distance: Up to 55 meters
  Power: High power consumption

SFP+ (Fiber):
  Use Cases: Backbone, long distance
  Cable: Single-mode or multi-mode fiber
  Distance: Up to 40km (single-mode)
  Types: SFP+, QSFP+, QSFP28

PoE (Power over Ethernet):
  Standards: 802.3af (15.4W), 802.3at (30W), 802.3bt (60W+)
  Use Cases: APs, IP cameras, VoIP phones
  Budget: Total power budget per switch
```

#### Performance Specifications
```bash
# Performance Metrics

Switching Capacity:
  Entry Level: 16-32 Gbps
  Mid Range: 64-128 Gbps
  High End: 256+ Gbps

Forwarding Rate:
  Entry Level: 10-20 Mpps
  Mid Range: 40-80 Mpps
  High End: 100+ Mpps

MAC Address Table:
  Entry Level: 8K-16K addresses
  Mid Range: 32K-64K addresses
  High End: 128K+ addresses

Buffer Memory:
  Entry Level: 1-4 MB
  Mid Range: 8-16 MB
  High End: 32+ MB
```

## 🔧 Basic Switch Setup

### Initial Configuration
```bash
# Connect to Switch (Web Interface)
1. Connect computer to switch port
2. Set IP: 192.168.1.2/24
3. Access: http://192.168.1.2
4. Default credentials: admin/admin or admin/password

# First-Time Setup Checklist
- [ ] Change default admin password
- [ ] Configure management IP
- [ ] Set hostname and domain
- [ ] Configure NTP server
- [ ] Enable HTTPS for management
- [ ] Backup initial configuration
```

### Port Configuration
```bash
# Basic Port Setup Examples

# Access Port (for workstations)
interface GigabitEthernet1/0/1
 description "Workstation Port - User 1"
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 storm-control broadcast level 10.00
 storm-control multicast level 5.00

# Uplink Port (to router)
interface TenGigabitEthernet1/0/1
 description "Uplink to Router"
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40
 spanning-tree portfast trunk
 mtu 9216

# Server Port (for NAS/hypervisor)
interface GigabitEthernet1/0/24
 description "Server Connection"
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 storm-control broadcast level 5.00

# IP Camera Port (with PoE)
interface GigabitEthernet1/0/48
 description "IP Camera - Front Entrance"
 switchport mode access
 switchport access vlan 40
 power inline auto
 spanning-tree portfast
```

### VLAN Configuration
```bash
# VLAN Setup Example

# Create VLANs
vlan 10
 name "MANAGEMENT"
 exit

vlan 20
 name "SERVERS"
 exit

vlan 30
 name "GUEST-WIFI"
 exit

vlan 40
 name "IOT-DEVICES"
 exit

# Configure SVI (Switch Virtual Interface)
interface Vlan10
 description "Management VLAN Interface"
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface Vlan20
 description "Server VLAN Interface"
 ip address 192.168.20.1 255.255.255.0
 no shutdown

# Configure Default Gateway
ip default-gateway 192.168.10.254
```

## 🔒 VLAN Segmentation Strategy

### Network Design Principles
```bash
# VLAN Segmentation Best Practices

Management VLAN (10):
  Purpose: Network infrastructure management
  Devices: Switches, routers, APs
  Security: Restricted access, ACLs
  Size: /24 subnet (254 hosts)
  Gateway: 192.168.10.1

Production VLAN (20):
  Purpose: Servers, storage, applications
  Devices: NAS, hypervisors, databases
  Security: Server-specific firewall rules
  Size: /24 subnet (254 hosts)
  Gateway: 192.168.20.1

User VLAN (30):
  Purpose: Workstations, user devices
  Devices: Desktops, laptops, printers
  Security: User access controls
  Size: /24 subnet (254 hosts)
  Gateway: 192.168.30.1

Guest WiFi VLAN (40):
  Purpose: Visitor WiFi, guest devices
  Devices: Guest APs, IoT devices
  Security: Isolated, time-limited access
  Size: /24 subnet (254 hosts)
  Gateway: 192.168.40.1

IoT VLAN (50):
  Purpose: Smart home devices, sensors
  Devices: Cameras, thermostats, lights
  Security: Device-specific firewall rules
  Size: /24 subnet (254 hosts)
  Gateway: 192.168.50.1
```

### Inter-VLAN Routing
```bash
# Layer 3 Switch Routing Configuration

# Enable IP Routing
ip routing

# Configure Static Routes
ip route 192.168.30.0 255.255.255.0 192.168.10.254
ip route 192.168.40.0 255.255.255.0 192.168.10.254
ip route 192.168.50.0 255.255.255.0 192.168.10.254

# Default Route
ip route 0.0.0.0 0.0.0.0 192.168.10.254

# DHCP Helper Addresses
ip helper-address 192.168.20.1  # Forward DHCP requests to server
```

## 🔗 Link Aggregation (LACP)

### Port Channel Configuration
```bash
# LACP Port Channel Setup

# Create Port Channel
interface Port-channel1
 description "Server Uplink Aggregation"
 switchport mode trunk
 switchport trunk allowed vlan all
 lacp system-priority 32768
 lacp port-priority 32768

# Configure Member Ports
interface GigabitEthernet1/0/47
 description "Uplink Member 1"
 channel-group 1 mode active
 spanning-tree portfast

interface GigabitEthernet1/0/48
 description "Uplink Member 2"
 channel-group 1 mode active
 spanning-tree portfast

# Verify Port Channel Status
show etherchannel summary
show lacp neighbor
show interfaces port-channel
```

### Load Balancing Algorithms
```bash
# LACP Load Balancing Methods

src-dst-ip:
  Description: Source and destination IP hash
  Use Case: Server-to-server communication
  Efficiency: Good for diverse IP flows
  Configuration: port-channel load-balance src-dst-ip

src-dst-mac:
  Description: Source and destination MAC hash
  Use Case: General purpose load balancing
  Efficiency: Good distribution
  Configuration: port-channel load-balance src-dst-mac

src-dst-port:
  Description: Source and destination port hash
  Use Case: Many connections to same service
  Efficiency: Excellent for web traffic
  Configuration: port-channel load-balance src-dst-port
```

## 🛡️ Security Configuration

### Port Security
```bash
# Switch Port Security Features

# Basic Port Security
interface GigabitEthernet1/0/10
 description "Secure Workstation Port"
 switchport mode access
 switchport access vlan 30
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 spanning-tree portfast

# Configure Allowed MAC Addresses
switchport port-security mac-address sticky
switchport port-security mac-address 0011.2233.4456
switchport port-security mac-address 0011.2233.4457

# Violation Actions
switchport port-security violation restrict  # Drop violating traffic
switchport port-security violation shutdown   # Shutdown port
switchport port-security violation protect    # Keep learning, drop new
```

### DHCP Snooping
```bash
# DHCP Snooping Configuration

# Enable DHCP Snooping Globally
ip dhcp snooping

# Configure Trusted Ports (to DHCP server)
interface GigabitEthernet1/0/1
 description "Uplink to DHCP Server"
 ip dhcp snooping trust

# Configure Untrusted Ports (client ports)
interface range GigabitEthernet1/0/2-48
 description "Client Access Ports"
 ip dhcp snooping limit rate 100

# DHCP Snooping Database
ip dhcp snooping database
show ip dhcp snooping
```

### Storm Control
```bash
# Broadcast Storm Control

# Configure Storm Control
interface GigabitEthernet1/0/10
 description "User Access Port"
 storm-control broadcast level 10.00  # 1% of 1Gbps
 storm-control multicast level 5.00   # 0.5% of 1Gbps
 storm-control unicast level 100.00 # 10% of 1Gbps
 storm-control action shutdown

# Monitor Storm Control
show storm-control
show interfaces counters
```

## 📊 Monitoring and Management

### SNMP Configuration
```bash
# SNMP Setup for Monitoring

# Enable SNMP
snmp-server community "homelab-ro" RO
snmp-server community "homelab-rw" RW

# Configure SNMP Views
snmp-server view "HOMELAB-VIEW" iso included
snmp-server view "HOMELAB-VIEW" system included
snmp-server view "HOMELAB-VIEW" interfaces included

# Configure SNMP Access
snmp-server community "homelab-ro" RO HOMELAB-VIEW
snmp-server community "homelab-rw" RW HOMELAB-VIEW

# SNMP Traps (Alerts)
snmp-server enable traps
snmp-server host 192.168.10.100 traps version 2c "homelab-trap"
```

### Performance Monitoring
```bash
# Interface Monitoring Commands

# Check Interface Status
show interfaces status
show interfaces summary
show interfaces counters

# Check Utilization
show interfaces utilization
show processes cpu
show memory

# Check Errors
show logging
show interfaces errdisable
show spanning-tree detail
```

## 🔧 Advanced Features

### Quality of Service (QoS)
```bash
# QoS Configuration

# Define QoS Classes
class-map match-any VOICE-TRAFFIC
 match dscp ef
 exit

class-map match-any VIDEO-TRAFFIC
 match dscp af41
 exit

class-map match-any BULK-TRAFFIC
 match dscp af11
 exit

# Define Policy Map
policy-map QOS-POLICY
 class VOICE-TRAFFIC
  priority percent 30
 class VIDEO-TRAFFIC
  bandwidth percent 40
 class BULK-TRAFFIC
  bandwidth percent 20
 class class-default
  fair-queue

# Apply to Interfaces
interface range GigabitEthernet1/0/1-48
 service-policy output QOS-POLICY
```

### Spanning Tree Optimization
```bash
# Rapid Spanning Tree Configuration

# Enable Rapid Spanning Tree
spanning-tree mode rapid-pvst

# Configure Root Bridge Priority
spanning-tree vlan 10 priority 4096
spanning-tree vlan 20 priority 8192
spanning-tree vlan 30 priority 12288
spanning-tree vlan 40 priority 16384

# Port Fast for Access Ports
interface range GigabitEthernet1/0/2-46
 spanning-tree portfast
 spanning-tree bpduguard enable

# Verify STP Status
show spanning-tree
show spanning-tree detail
show spanning-tree blockedports
```

## 🚨 Troubleshooting

### Common Issues and Solutions
```bash
# Issue: Port Not Coming Up
# Diagnosis Commands
show interfaces GigabitEthernet1/0/10 status
show interfaces GigabitEthernet1/0/10 counters
show logging | include GigabitEthernet1/0/10

# Common Solutions
1. Check cable connectivity
2. Verify device on other end is powered
3. Check for speed/duplex mismatches
4. Disable and re-enable interface
5. Check for spanning tree blocking

# Issue: VLAN Not Working
# Diagnosis Commands
show vlan brief
show interfaces trunk
show mac address-table dynamic

# Common Solutions
1. Verify trunk configuration on both ends
2. Check allowed VLAN list
3. Verify native VLAN configuration
4. Check for VLAN pruning
5. Verify tag rewriting if needed
```

### Performance Issues
```bash
# Issue: High CPU Usage
show processes cpu sorted
show memory

# Issue: Packet Loss
show interfaces counters
show logging
show storm-control

# Issue: Slow Performance
show interfaces utilization
show processes memory
show platform
```

## 📋 Configuration Backup and Recovery

### Automated Backup
```bash
# Backup Configuration Script
#!/bin/bash

BACKUP_DIR="/backups/switch-configs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
HOST="192.168.10.1"
USER="admin"
PASS="your-password"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup via TFTP
# Enable TFTP server on management station
expect << EOF
spawn ssh "$USER@$HOST"
expect "Password:"
send "$PASS\r"
expect ">"
send "copy running-config tftp://192.168.10.100/switch-backup-$TIMESTAMP.cfg\r"
expect ">"
send "exit\r"
expect eof
EOF

# Backup via SCP
scp "$USER@$HOST:running-config" "$BACKUP_DIR/switch-backup-$TIMESTAMP.cfg"

# Cleanup Old Backups (keep 30 days)
find "$BACKUP_DIR" -name "*.cfg" -mtime +30 -delete

echo "Backup completed: switch-backup-$TIMESTAMP.cfg"
```

### Configuration Restore
```bash
# Restore Configuration Script
#!/bin/bash

BACKUP_FILE="$1"
HOST="192.168.10.1"
USER="admin"
PASS="your-password"

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Restore via SCP
scp "$BACKUP_FILE" "$USER@$HOST:startup-config"

# Restore via SSH
expect << EOF
spawn ssh "$USER@$HOST"
expect "Password:"
send "$PASS\r"
expect ">"
send "copy startup-config running-config\r"
expect ">"
send "write memory\r"
expect ">"
send "exit\r"
expect eof
EOF

echo "Configuration restore completed"
```

## 🔍 Switch Selection Guide

### Entry Level Recommendations
```bash
# Budget Switches (<$300)

Netgear GS308:
  Ports: 8x Gigabit
  Management: Basic web interface
  VLANs: Basic support
  Use Case: Small homelab, learning

TP-Link TL-SG108:
  Ports: 8x Gigabit
  Management: Web interface
  Features: Basic QoS, port mirroring
  Use Case: Budget conscious setup

Ubiquiti UniFi Switch:
  Ports: 8x Gigabit
  Management: UniFi Controller
  Features: Auto-configuration, monitoring
  Use Case: UniFi ecosystem
```

### Mid-Range Recommendations
```bash
# Professional Switches ($300-1000)

Cisco Catalyst 2960-X:
  Ports: 24-48x Gigabit
  Management: CLI, web, SNMP
  Features: Full VLAN support, L3 routing
  Use Case: Production homelab

Aruba 2530:
  Ports: 24-48x Gigabit
  Management: Aruba Central, web
  Features: Advanced security, PoE+
  Use Case: Enterprise features, budget friendly

Ubiquiti UniFi Pro Switch:
  Ports: 24x Gigabit, 2x SFP+
  Management: UniFi Controller
  Features: Deep packet inspection, advanced QoS
  Use Case: Professional homelab with analytics
```

### Enterprise Recommendations
```bash
# High-End Switches ($1000+)

Cisco Catalyst 9300:
  Ports: 24x Multigigabit, 4x SFP28
  Management: DNA Center, full CLI
  Features: Advanced routing, telemetry, AI ops
  Use Case: Data center, enterprise homelab

Arista 7280R:
  Ports: 48x 1GbE, 4x 10GbE SFP+
  Management: CloudVision, EOS CLI
  Features: Extensible OS, programmable
  Use Case: Cloud-native homelab, automation
```

## 🔮 Future Considerations

### Network Evolution Planning
```bash
# 1-3 Year Planning
Year 1:
  - Upgrade to managed switches
  - Implement basic VLAN segmentation
  - Add monitoring and backup

Year 2:
  - Add link aggregation
  - Implement QoS policies
  - Add PoE for wireless APs

Year 3:
  - Upgrade to 10GbE where needed
  - Implement L3 routing
  - Add advanced security features
```

### Technology Trends
```bash
# Emerging Switch Technologies
Wi-Fi 6E Support:
  - Higher bandwidth for wireless backhaul
  - Lower latency applications
  - Future-proofing investments

Multi-Gigabit Ethernet:
  - 2.5GbE, 5GbE, 10GbE over copper
  - Gradual upgrade path
  - Cost-effective performance boost

AI/ML Features:
  - Anomaly detection
  - Automated optimization
  - Predictive maintenance
  - Enhanced security monitoring

SD-WAN Integration:
  - Multiple ISP management
  - Automatic failover
  - Application-aware routing
  - Better performance for cloud apps
```

## 📖 Further Reading

### Documentation
- [Cisco Switch Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/)
- [Aruba Switch Documentation](https://www.arubanetworks.com/techdocs/switches/)
- [Ubiquiti UniFi Switch Guide](https://help.ui.com/hc/en-us/articles/360008854373)

### Communities
- Reddit: r/networking, r/homelab
- Network Engineering Stack Exchange
- Cisco Community forums
- Aruba Networks community

### Training Resources
- [Cisco Networking Academy](https://www.netacad.com/)
- [CompTIA Network+ Certification](https://www.comptia.org/certifications/network/)
- [Wireshark University](https://www.wireshark-training.com/)

---

**Ready to dive deeper?** Check our [Network Infrastructure](index.md) overview for comprehensive network planning!
