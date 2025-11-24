---
title: Router Configuration
description: Complete router setup guide for OpenWRT and OPNsense
---

# Router Configuration Guide

A properly configured router is the foundation of your homelab network. This guide covers OpenWRT and OPNsense setup, from basic configuration to advanced features.

## 🛒 Choosing Your Router

### Hardware Requirements

**Minimum Requirements:**
- CPU: Dual-core 1GHz+
- RAM: 512MB+
- Storage: 128MB Flash
- Ethernet: Gigabit ports
- WiFi: 802.11ac or better

**Recommended Hardware:**
- **Ubiquiti EdgeRouter**: Professional features, affordable
- **Netgear Nighthawk**: Good performance, OpenWRT support
- **Linksys WRT series**: Excellent OpenWRT support
- **Protectli Vault**: pfSense/OPNsense appliances

### Firmware Options

| Firmware | Pros | Cons | Best For |
|-----------|------|------|----------|
| **OpenWRT** | Lightweight, customizable | Steeper learning curve | Advanced users, custom setups |
| **OPNsense** | Security-focused, user-friendly | Higher resource requirements | Security-conscious users |
| **pfSense** | Enterprise features, stable | Complex, requires more resources | Business-like setups |
| **Stock** | Easy, supported | Limited features | Beginners, simple setups |

## 📦 OpenWRT Installation

### Initial Setup

#### 1. Download and Flash
```bash
# Find your router model
# Download firmware from openwrt.org

# Flash firmware via web interface
# or use TFTP method for bricked routers
```

#### 2. Initial Configuration
```bash
# Connect to router via SSH
ssh root@192.168.1.1

# Set root password
passwd

# Configure LAN interface
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.proto='static'
uci commit network
/etc/init.d/network restart
```

#### 3. Basic Network Configuration
```bash
# Configure WAN interface
uci set network.wan.proto='dhcp'
uci set network.wan.hostname='homelab-router'
uci commit network

# Configure wireless (if available)
uci set wireless.@wifi-iface[0].ssid='Homelab-Net'
uci set wireless.@wifi-iface[0].encryption='psk2'
uci set wireless.@wifi-iface[0].key='your-secure-password'
uci commit wireless
wifi up
```

### Advanced OpenWRT Configuration

#### VLAN Setup
```bash
# Create VLAN 10 for services
uci set network.vlan10=interface
uci set network.vlan10.type='bridge'
uci set network.vlan10.proto='static'
uci set network.vlan10.ipaddr='192.168.10.1'
uci set network.vlan10.netmask='255.255.255.0'
uci set network.vlan10.device='eth0.10'

# Configure VLAN tagging
uci set network.eth0_10=vlan
uci set network.eth0_10.device='eth0'
uci set network.eth0_10.vlan='10'
uci commit network
/etc/init.d/network restart
```

#### DHCP Configuration
```bash
# Configure DHCP for main LAN
uci set dhcp.lan.start='100'
uci set dhcp.lan.limit='150'
uci set dhcp.lan.leasetime='12h'
uci commit dhcp

# Configure DHCP for VLAN 10
uci set dhcp.vlan10=dhcp
uci set dhcp.vlan10.interface='vlan10'
uci set dhcp.vlan10.start='50'
uci set dhcp.vlan10.limit='100'
uci set dhcp.vlan10.leasetime='24h'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

#### Firewall Configuration
```bash
# Create new firewall zone for services
uci add firewall zone
uci set firewall.@zone[-1].name='services'
uci set firewall.@zone[-1].input='REJECT'
uci set firewall.@zone[-1].output='ACCEPT'
uci set firewall.@zone[-1].forward='REJECT'
uci set firewall.@zone[-1].network='vlan10'

# Allow traffic from LAN to services
uci add firewall forwarding
uci set firewall.@forwarding[-1].src='lan'
uci set firewall.@forwarding[-1].dest='services'

# Allow specific services
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-HTTP'
uci set firewall.@rule[-1].src='wan'
uci set firewall.@rule[-1].dest_port='80'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'

uci commit firewall
/etc/init.d/firewall restart
```

## 🛡️ OPNsense Installation

### Initial Setup

#### 1. Installation
```bash
# Download OPNsense image
# Create bootable USB
# Install on target hardware
# Follow web-based installer
```

#### 2. Initial Web Configuration
1. Access web interface: `https://192.168.1.1`
2. Default credentials: `admin / pfsense`
3. Run initial setup wizard
4. Configure WAN and LAN interfaces

#### 3. Basic Network Setup
```
Interfaces > Assignments
- Configure LAN: 192.168.1.1/24
- Configure WAN: DHCP or static
- Enable interfaces

System > General Setup
- Set hostname: homelab-router
- Set domain: local
- Configure DNS servers
```

### Advanced OPNsense Configuration

#### VLAN Configuration
```
Interfaces > Assignments > VLANs
- Create VLAN 10: eth0.10
- Parent interface: eth0
- VLAN tag: 10
- Priority: 0

Interfaces > Assignments
- Create new interface: OPT1
- Assign to VLAN 10
- Configure IP: 192.168.10.1/24
- Enable interface
```

#### DHCP Server Setup
```
Services > DHCP Server
- Enable DHCP on LAN
- Range: 192.168.1.100 to 192.168.1.200
- Lease time: 12 hours

- Enable DHCP on VLAN interface
- Range: 192.168.10.50 to 192.168.10.150
- Lease time: 24 hours
```

#### Firewall Rules
```
Firewall > Rules > LAN
- Default deny all
- Allow LAN to any
- Allow DNS/ DHCP

Firewall > Rules > Services (VLAN 10)
- Default deny all
- Allow Services to LAN (management)
- Allow Services to WAN (updates)
```

## 🌐 DNS Configuration

### OpenWRT DNS Setup
```bash
# Install additional DNS packages
opkg update
opkg install dnsmasq-full unbound

# Configure local DNS
uci set dhcp.@dnsmasq[0].server='8.8.8.8'
uci set dhcp.@dnsmasq[0].server='1.1.1.1'
uci set dhcp.@dnsmasq[0].noresolv='1'

# Add local hostnames
uci add dhcp domain
uci set dhcp.@domain[-1].name='server'
uci set dhcp.@domain[-1].ip='192.168.1.100'

uci commit dhcp
/etc/init.d/dnsmasq restart
```

### OPNsense DNS Setup
```
System > General Setup > DNS Servers
- Primary: 8.8.8.8
- Secondary: 1.1.1.1
- Enable DNS Server Override

Services > Unbound DNS > General
- Enable Unbound
- Enable DNSSEC
- Enable Forwarding Mode

Services > Unbound DNS > Advanced
- Add local domain zones
- Configure private reverse lookups
```

## 🔧 Advanced Features

### Port Forwarding

#### OpenWRT Port Forwarding
```bash
# Forward port 8080 to internal server
uci add firewall redirect
uci set firewall.@redirect[-1].name='Web-Server'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].proto='tcp'
uci set firewall.@redirect[-1].src_dport='8080'
uci set firewall.@redirect[-1].dest_ip='192.168.1.100'
uci set firewall.@redirect[-1].dest_port='80'

uci commit firewall
/etc/init.d/firewall restart
```

#### OPNsense Port Forwarding
```
Firewall > NAT > Port Forward
- WAN interface: selected
- Protocol: TCP
- Source: any
- Destination port: 8080
- Redirect target IP: 192.168.1.100
- Redirect target port: 80
- Description: Web Server
```

### Quality of Service (QoS)

#### OpenWRT QoS
```bash
# Install QoS packages
opkg install qos-scripts

# Configure basic QoS
uci set qos.wan='interface'
uci set qos.wan.upload='10000'   # 10 Mbps upload
uci set qos.wan.download='50000'  # 50 Mbps download

# Add traffic classes
uci add qos classify
uci set qos.@classify[-1].target='High Priority'
uci set qos.@classify[-1].portrange='22,80,443'

uci commit qos
/etc/init.d/qos restart
```

### VPN Configuration

#### OpenWRT WireGuard
```bash
# Install WireGuard
opkg update
opkg install wireguard-tools

# Generate keys
wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/wireguard/public.key

# Configure WireGuard interface
uci set network.wg0=interface
uci set network.wg0.proto='wireguard'
uci set network.wg0.private_key='$(cat /etc/wireguard/private.key)'
uci set network.wg0.listen_port='51820'

# Add peer configuration
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key='client-public-key'
uci set network.@wireguard_wg0[-1].allowed_ips='192.168.200.2/32'

uci commit network
/etc/init.d/network restart
```

#### OPNsense WireGuard
```
VPN > WireGuard > General
- Enable WireGuard
- Listen Port: 51820

VPN > WireGuard > Peers
- Add peer
- Public Key: client-public-key
- Allowed IPs: 192.168.200.2/32
- Description: Client Device
```

## 📊 Monitoring and Logging

### OpenWRT Monitoring
```bash
# Install monitoring packages
opkg install luci-app-statistics collectd collectd-mod-cpu collectd-mod-memory

# Configure collectd
uci set luci_statistics.collectd.enable='1'
uci set luci_statistics.collectd.Interval='30'

uci commit luci_statistics
/etc/init.d/collectd restart
```

### OPNsense Monitoring
```
System > Logging > Settings
- Enable remote logging
- Set log levels
- Configure log rotation

System > Monitoring > Settings
- Enable system monitoring
- Configure thresholds
- Set up notifications
```

## 🔍 Troubleshooting

### Common Router Issues

#### No Internet Access
```bash
# Check WAN status
ifconfig wan
ping -c 4 8.8.8.8

# Check DNS resolution
nslookup google.com

# Check routing tables
ip route show
```

#### DHCP Not Working
```bash
# Check DHCP service status
/etc/init.d/dnsmasq status

# Check DHCP leases
cat /tmp/dhcp.leases

# Restart DHCP service
/etc/init.d/dnsmasq restart
```

#### Firewall Blocking Traffic
```bash
# Check firewall rules
iptables -L -n

# Check for blocked connections
iptables -L -v -n | head -20

# Temporarily disable firewall for testing
/etc/init.d/firewall stop
# Test, then re-enable
/etc/init.d/firewall start
```

### Performance Optimization

#### Router Performance
```bash
# Check CPU usage
top

# Check memory usage
free -m

# Check network interfaces
cat /proc/net/dev
```

#### Network Optimization
```bash
# Enable TCP BBR congestion control
echo 'net.ipv4.tcp_congestion_control=bbr' >> /etc/sysctl.conf

# Optimize network buffers
echo 'net.core.rmem_max=16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max=16777216' >> /etc/sysctl.conf

sysctl -p
```

## 📋 Maintenance Checklist

### Monthly Maintenance
- [ ] Check firmware updates
- [ ] Review firewall logs
- [ ] Backup configuration
- [ ] Monitor performance metrics
- [ ] Check for security advisories

### Quarterly Maintenance
- [ ] Update all packages
- [ ] Review and optimize rules
- [ ] Test backup and restore
- [ ] Audit user access
- [ ] Update documentation

---

**Need more advanced networking?** Check out our [Switch Setup](switches.md) and [Firewall Rules](firewall.md) guides!
