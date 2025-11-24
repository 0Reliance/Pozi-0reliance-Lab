---
title: Network Infrastructure
description: Complete network setup guides for homelab environments
---

# Network Infrastructure

A solid network foundation is essential for any homelab. This section covers everything from basic network design to advanced routing, switching, and security configurations.

## 🌐 Network Design Principles

### Basic Topology
```
Internet
    ↓
[Router/Firewall]
    ↓
[Managed Switch]
    ├── [Server/Hypervisor]     # 192.168.1.100
    ├── [NAS Storage]           # 192.168.1.101
    ├── [AP for WiFi]           # 192.168.1.102
    └── [Workstation]           # 192.168.1.50
```

### Network Segmentation Strategy
```bash
Management Network:  192.168.1.0/24   # Infrastructure, admin access
Production Network:  192.168.10.0/24  # Services, applications
Storage Network:     192.168.20.0/24  # NAS, backups
IoT Network:        192.168.30.0/24  # Smart home devices
Guest Network:      192.168.40.0/24  # Visitors, testing
```

## 📚 Network Documentation

### [Router Configuration](router.md)
- OpenWRT/OPNsense setup
- VLAN configuration
- Firewall rules
- DHCP and DNS services

### [Switch Setup](switches.md)
- Managed switch configuration
- VLAN trunking
- Link aggregation
- Quality of Service (QoS)

### [Firewall Rules](firewall.md)
- Security policies
- Port forwarding
- Intrusion detection
- VPN configuration

## 🛠️ Essential Network Services

### DNS Services
- **Local DNS**: Resolve local services
- **Ad-blocking**: Block ads network-wide
- **DNS-over-HTTPS**: Secure DNS resolution
- **Failover**: Multiple DNS servers

### DHCP Services
- **Static Leases**: Reserve IPs for servers
- **Option Settings**: Configure network parameters
- **Failover**: Redundant DHCP servers

### VPN Services
- **WireGuard**: Modern, fast VPN
- **OpenVPN**: Traditional, compatible
- **Site-to-site**: Connect multiple locations
- **Client VPN**: Remote access

## 🔧 Network Monitoring

### Traffic Analysis
```bash
# Monitor network interfaces
iftop -i eth0
nethogs -t

# Packet capture
tcpdump -i eth0 -n port 80
tcpdump -i eth0 -n host 192.168.1.100
```

### Performance Monitoring
```bash
# Network performance tests
iperf3 -s                          # Server mode
iperf3 -c server-ip -t 30          # Client mode

# Latency testing
ping -c 100 8.8.8.8
mtr google.com
```

## 📋 Network Planning Checklist

### Pre-Setup Planning
- [ ] Network diagram
- [ ] IP address scheme
- [ ] VLAN strategy
- [ ] Security requirements
- [ ] Performance needs

### Hardware Requirements
- [ ] Router/firewall device
- [ ] Managed switch (optional but recommended)
- [ ] Access points (for WiFi)
- [ ] Network cables (Cat6 or better)
- [ ] UPS for network equipment

### Software Stack
- [ ] Router firmware (OpenWRT/OPNsense)
- [ ] Monitoring tools
- [ ] Configuration management
- [ ] Backup solution

## 🚀 Getting Started

### Step 1: Assess Your Needs
- Number of devices
- Bandwidth requirements
- Security concerns
- Growth plans

### Step 2: Choose Your Router
- **OpenWRT**: Flexible, open-source
- **OPNsense**: Security-focused
- **pfSense**: Enterprise features
- **Stock firmware**: Basic functionality

### Step 3: Plan Your Network
- IP addressing scheme
- VLAN segmentation
- Firewall policies
- Monitoring strategy

### Step 4: Implement Gradually
- Start with basic setup
- Add advanced features
- Test thoroughly
- Document everything

## 📊 Common Network Configurations

### Small Homelab (1-5 devices)
```bash
Network: 192.168.1.0/24
Gateway: 192.168.1.1
DNS: 192.168.1.1, 8.8.8.8
DHCP Range: 192.168.1.100-200
```

### Medium Homelab (6-20 devices)
```bash
Management: 192.168.1.0/24   # Infrastructure
Services:  192.168.10.0/24  # Applications
Storage:   192.168.20.0/24  # NAS, backups
```

### Advanced Homelab (20+ devices)
```bash
Management: 192.168.1.0/24   # Infrastructure
Production: 192.168.10.0/24  # Services
Development: 192.168.20.0/24  # Dev/staging
Storage:    192.168.30.0/24  # NAS, backups
IoT:        192.168.40.0/24  # Smart devices
Guest:      192.168.50.0/24  # Visitors
```

## 🔍 Troubleshooting Common Issues

### Connectivity Problems
```bash
# Check basic connectivity
ping -c 4 8.8.8.8
ping -c 4 gateway-ip

# Check DNS resolution
nslookup google.com
dig @8.8.8.8 google.com

# Check routing
ip route show
traceroute google.com
```

### Performance Issues
```bash
# Check for packet loss
ping -c 100 8.8.8.8 | tail -1

# Check bandwidth usage
iftop -t -s 30

# Check network errors
cat /proc/net/dev
```

## 📚 Learning Resources

### Essential Reading
- [Network+ Study Guide](https://www.comptia.org/training/resources/exam-objectives/network)
- [TCP/IP Illustrated](https://en.wikipedia.org/wiki/TCP/IP_Illustrated)
- [OpenWRT Documentation](https://openwrt.org/docs/start)

### Online Communities
- Reddit: r/homelab, r/networking
- Forums: OpenWRT, OPNsense communities
- YouTube: NetworkChuck, Lawrence Systems

---

**Ready to dive deeper?** Start with our [Router Configuration](router.md) guide to build your network foundation!
