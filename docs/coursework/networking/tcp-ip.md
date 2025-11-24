# TCP/IP Protocol Suite

## Overview

The TCP/IP protocol suite is the foundational architecture of the internet and modern networking. This comprehensive guide covers the layers, protocols, and practical implementations.

## OSI vs TCP/IP Models

### TCP/IP Model (4 Layers)
1. **Application Layer** (HTTP, FTP, SMTP, DNS)
2. **Transport Layer** (TCP, UDP)
3. **Internet Layer** (IP, ICMP, ARP)
4. **Network Access Layer** (Ethernet, Wi-Fi)

### OSI Model (7 Layers)
1. Application Layer
2. Presentation Layer
3. Session Layer
4. Transport Layer
5. Network Layer
6. Data Link Layer
7. Physical Layer

## Layer 4: Application Protocols

### HTTP/HTTPS
```bash
# HTTP Request Example
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: text/html

# HTTPS Handshake
Client Hello → Server Hello → Certificate → Key Exchange
```

### DNS Resolution
```bash
# DNS Query Process
1. Check local cache
2. Query DNS resolver
3. Query root server
4. Query TLD server
5. Query authoritative server
```

### Email Protocols
```bash
# SMTP (Port 25, 587, 465)
EHLO mail.example.com
MAIL FROM: sender@example.com
RCPT TO: recipient@example.com
DATA

# POP3 (Port 110, 995)
USER username
PASS password
LIST
RETR 1

# IMAP (Port 143, 993)
LOGIN username password
SELECT INBOX
FETCH 1 ALL
```

## Layer 3: Transport Layer

### TCP (Transmission Control Protocol)
```python
# TCP Three-Way Handshake
"""
Client                           Server
SYN    ------------------------>
       <------------------------ SYN-ACK
ACK    ------------------------>
Connection Established
"""

# TCP Connection States
states = {
    "CLOSED": "No connection active",
    "LISTEN": "Waiting for connection request",
    "SYN_SENT": "Connection request sent",
    "SYN_RECEIVED": "Connection request received",
    "ESTABLISHED": "Connection established",
    "FIN_WAIT_1": "Termination from user sent",
    "FIN_WAIT_2": "Waiting for termination from remote",
    "CLOSE_WAIT": "Waiting for close from user",
    "CLOSING": "Both sides closing",
    "LAST_ACK": "Waiting for final ACK",
    "TIME_WAIT": "Waiting for 2MSL timeout"
}
```

### UDP (User Datagram Protocol)
```python
# UDP Characteristics
udp_features = {
    "connectionless": "No handshake required",
    "unreliable": "No guarantee of delivery",
    "unordered": "Packets may arrive out of sequence",
    "lightweight": "Minimal overhead (8 bytes header)",
    "fast": "No connection setup overhead"
}

# Common UDP Ports
udp_ports = {
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    69: "TFTP",
    123: "NTP",
    161: "SNMP",
    500: "IPSec"
}
```

## Layer 2: Internet Layer

### IPv4 Addressing
```bash
# IPv4 Address Classes
Class A: 1.0.0.0 - 126.255.255.255  (255.0.0.0)
Class B: 128.0.0.0 - 191.255.255.255 (255.255.0.0)
Class C: 192.0.0.0 - 223.255.255.255 (255.255.255.0)

# Subnetting Example
Network: 192.168.1.0/24
Subnets: /26 (255.255.255.192)
- 192.168.1.0/26 (62 hosts)
- 192.168.1.64/26 (62 hosts)
- 192.168.1.128/26 (62 hosts)
- 192.168.1.192/26 (62 hosts)

# CIDR Notation
192.168.1.0/24 = 255.255.255.0
10.0.0.0/8 = 255.0.0.0
172.16.0.0/12 = 255.240.0.0
```

### IPv6 Addressing
```bash
# IPv6 Address Format
2001:0db8:85a3:0000:0000:8a2e:0370:7334

# Compressed Format
2001:db8:85a3::8a2e:370:7334

# IPv6 Address Types
Unicast: One-to-one communication
Multicast: One-to-many communication
Anycast: One-to-nearest communication

# IPv6 Prefixes
/64: Standard subnet size
/48: Typical allocation for sites
/32: Allocation for ISPs
```

### ICMP (Internet Control Message Protocol)
```bash
# Common ICMP Types
Type 0: Echo Reply
Type 3: Destination Unreachable
Type 5: Redirect
Type 8: Echo Request
Type 11: Time Exceeded
Type 12: Parameter Problem

# Traceroute using ICMP
traceroute google.com
1  192.168.1.1    1.234 ms
2  10.0.0.1       12.456 ms
3  203.0.113.1    23.789 ms
```

## Layer 1: Network Access Layer

### Ethernet
```bash
# Ethernet Frame Structure
| Preamble | SFD | Destination | Source | Type | Data | FCS |
|   8B     | 1B  |     6B      |   6B   |  2B  | 46-1500B | 4B |

# MAC Address Format
XX:XX:XX:XX:XX:XX
OUI (3 bytes) + NIC-specific (3 bytes)

# Ethernet Standards
10BASE-T: 10 Mbps, twisted pair
100BASE-TX: 100 Mbps, twisted pair
1000BASE-T: 1 Gbps, twisted pair
10GBASE-T: 10 Gbps, twisted pair
```

### ARP (Address Resolution Protocol)
```bash
# ARP Process
1. Check ARP cache for MAC address
2. Broadcast ARP request: "Who has IP 192.168.1.10?"
3. Target responds: "192.168.1.10 is at 00:11:22:33:44:55"
4. Update ARP cache

# ARP Commands
arp -a                    # Display ARP cache
arp -d 192.168.1.10      # Delete ARP entry
arp -s 192.168.1.10 00:11:22:33:44:55  # Static ARP entry
```

## Network Configuration

### Linux Network Configuration
```bash
# IP Address Configuration
ip addr add 192.168.1.10/24 dev eth0
ip link set eth0 up

# Route Configuration
ip route add default via 192.168.1.1
ip route add 10.0.0.0/8 via 192.168.1.254

# DNS Configuration
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Network Interface Configuration File (/etc/network/interfaces)
auto eth0
iface eth0 inet static
    address 192.168.1.10
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4
```

### Windows Network Configuration
```powershell
# IP Address Configuration
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.1.10 -PrefixLength 24 -DefaultGateway 192.168.1.1

# DNS Configuration
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "8.8.8.8","8.8.4.4"

# Route Configuration
New-NetRoute -DestinationPrefix "10.0.0.0/8" -InterfaceAlias "Ethernet" -NextHop 192.168.1.254
```

## Troubleshooting TCP/IP

### Network Diagnostic Tools
```bash
# Ping Test
ping -c 4 8.8.8.8
ping -c 4 google.com

# Traceroute
traceroute google.com
tracert google.com  # Windows

# DNS Resolution
nslookup google.com
dig google.com ANY
host google.com

# Network Statistics
netstat -tulnp      # Linux connections
netstat -an         # All connections
ss -tulnp          # Modern Linux alternative

# Packet Capture
tcpdump -i eth0 -n port 80
tcpdump -i eth0 host 192.168.1.10
```

### Common TCP/IP Issues
```bash
# No Connectivity
1. Check physical connection
2. Verify IP configuration
3. Test local connectivity (127.0.0.1)
4. Test gateway connectivity
5. Test DNS resolution
6. Test external connectivity

# Intermittent Connectivity
1. Check for packet loss
2. Verify MTU settings
3. Check for duplex mismatches
4. Monitor error counters

# Performance Issues
1. Check bandwidth utilization
2. Monitor latency
3. Verify routing efficiency
4. Check for congestion
```

## Security Considerations

### Network Security Best Practices
```bash
# Firewall Rules (iptables)
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP

# Network Segmentation
VLAN 10: Management Network
VLAN 20: User Network
VLAN 30: Server Network
VLAN 40: DMZ

# Access Control Lists
access-list 101 permit tcp 192.168.1.0 0.0.0.255 any eq 80
access-list 101 deny tcp any any eq 23
```

### Network Monitoring
```bash
# Traffic Monitoring
iftop -i eth0
nethogs
tcpstat -i eth0

# Network Performance
iperf -c server_ip -t 30
mtr google.com
bwm-ng
```

## Advanced Topics

### Quality of Service (QoS)
```bash
# Traffic Classification
tc qdisc add dev eth0 root handle 1: htb default 30
tc class add dev eth0 parent 1: classid 1:1 htb rate 1000mbit
tc class add dev eth0 parent 1:1 classid 1:10 htb rate 500mbit ceil 800mbit

# Prioritization
tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dport 22 0xffff flowid 1:10
```

### Load Balancing
```bash
# Round Robin DNS
www IN A 192.168.1.10
www IN A 192.168.1.11
www IN A 192.168.1.12

# HAProxy Configuration
backend web_servers
    balance roundrobin
    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
    server web3 192.168.1.12:80 check
```

## Practical Labs

### Lab 1: Basic Network Configuration
```bash
# Objectives
1. Configure static IP address
2. Set up default gateway
3. Configure DNS servers
4. Test connectivity
5. Verify routing table

# Steps
1. Configure network interface
2. Add default route
3. Configure DNS resolution
4. Test with ping and traceroute
5. Document configuration
```

### Lab 2: Protocol Analysis
```bash
# Objectives
1. Capture HTTP traffic
2. Analyze TCP handshake
3. Examine DNS queries
4. Identify protocol headers
5. Document findings

# Tools
1. Wireshark/Tcpdump
2. Protocol analyzers
3. Network monitoring tools
```

## Summary

The TCP/IP protocol suite provides the foundation for modern networking. Understanding each layer and its protocols is essential for:

- **Network Administration**: Configuring and maintaining networks
- **Troubleshooting**: Diagnosing and resolving network issues
- **Security**: Implementing network security measures
- **Performance**: Optimizing network performance
- **Design**: Planning and implementing network architectures

Key takeaways include understanding protocol interactions, proper configuration methods, effective troubleshooting techniques, and security best practices.

## Further Reading

- [TCP/IP Illustrated](https://en.wikipedia.org/wiki/TCP/IP_Illustrated)
- [RFC 791 - Internet Protocol](https://tools.ietf.org/html/rfc791)
- [RFC 793 - Transmission Control Protocol](https://tools.ietf.org/html/rfc793)
- [Computer Networks by Andrew Tanenbaum](https://en.wikipedia.org/wiki/Computer_Networks_(book))

---

*This guide covers the essential concepts of TCP/IP networking with practical examples and hands-on labs for comprehensive learning.*
