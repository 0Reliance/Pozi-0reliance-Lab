---
title: Windows Server Administration
description: Comprehensive guide for Windows Server administration in homelab environments
---

# Windows Server Administration

Windows Server provides enterprise-grade features for homelab environments, offering robust Active Directory, file services, and application hosting capabilities. This comprehensive guide covers Windows Server administration from installation to advanced management.

## 🪟 Windows Server Fundamentals

### Windows Architecture Overview
```powershell
# Windows Server Components

Operating System Kernel:
  Role: Core operating system kernel
  Architecture: Hybrid kernel (NT kernel)
  Versions: Windows Server 2019, 2022, 2025
  Editions: Standard, Datacenter, Essentials
  Licensing: Volume licensing, CALs

Active Directory:
  Role: Directory services and authentication
  Forest: Hierarchical domain structure
  Domain: Security and policy boundary
  Organizational Units: Container objects for delegation

Group Policy:
  Role: Centralized configuration management
  Objects: GPOs with settings and preferences
  Inheritance: Hierarchical policy application
  Processing: Client-side policy enforcement

Windows Management:
  Tools: GUI (MMC), PowerShell, RSAT
  Protocols: WinRM, WMI, RPC
  Logging: Event Viewer, Performance Monitor
```

### Windows Server Editions
```powershell
# Server Edition Comparison

Windows Server Essentials:
  Target: Small businesses (1-25 users, 50 devices)
  Features: File sharing, basic AD, remote access
  Limitations: 25 users, 50 devices, limited CALs
  Use Case: Small office homelab

Windows Server Standard:
  Target: Medium organizations
  Features: Full AD, unlimited users, 2 VMs
  Licensing: Per-core or CAL licensing
  Use Case: General purpose homelab server

Windows Server Datacenter:
  Target: Enterprise environments
  Features: Unlimited VMs, advanced features
  Licensing: Per-core licensing
  Use Case: Virtualization host, large infrastructure

Windows Server Azure Arc:
  Target: Hybrid cloud environments
  Features: Azure management, cloud integration
  Requirements: Azure subscription, Arc agents
  Use Case: Hybrid homelab-cloud setup
```

## 🚀 Windows Server Installation

### System Requirements
```powershell
# Minimum System Requirements
CPU: 1.4 GHz 64-bit processor (2+ cores recommended)
RAM: 512 MB (2 GB+ recommended)
Storage: 32 GB+ (60 GB+ recommended)
Network: Gigabit Ethernet

# Recommended Homelab Setup
CPU: 4+ cores, 2.5 GHz+ (virtualization support)
RAM: 16 GB+ (32 GB+ for virtualization)
Storage: 500 GB+ SSD (1 TB+ for data)
Network: 10 GbE (multiple NICs for virtualization)
Virtualization: SLAT support, nested virtualization

# Supported Hardware
Processor: x64 with Second Level Address Translation (SLAT)
RAM: ECC memory recommended for servers
Storage: SATA, SAS, NVMe, or storage spaces
Network: Intel/AMD NICs with offloading support
```

### Installation Process
```powershell
# Windows Server Installation Steps

# 1. Preparation Phase
# Download Windows Server ISO
# Verify ISO integrity (SHA-256 hash)
# Create bootable USB or mount ISO
# Backup existing data if upgrading

# 2. Boot and Setup
# Boot from USB/DVD/ISO
# Select language, time, currency
# Click "Install now"
# Enter product key or select evaluation
# Choose installation type (Custom: Install Windows only)

# 3. Disk Configuration
# Select target disk
# Choose partitioning scheme:
  - Windows default (recommended)
  - Custom (for specific layout)
# Create partitions:
  - System partition (100 MB, boot files)
  - Windows partition (remaining space)
  - Optional data partitions

# 4. Installation
# Windows files copy and expand
# System restarts multiple times
# Initial setup (OOBE - Out of Box Experience)
# Administrator password setup
# Network configuration

# 5. Post-Installation
# Windows Updates installation
# Driver installation
# Server role configuration
```

### Post-Installation Configuration
```powershell
# Initial Server Configuration
# Using Server Manager (GUI) or PowerShell

# 1. Computer Identity
Rename-Computer -NewName "HOMELAB-SRV01"
Add-Computer -DomainName "homelab.local"

# 2. Network Configuration
# Static IP assignment
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress "192.168.1.100" -PrefixLength 24
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "192.168.1.1,8.8.8.8"

# 3. Windows Update
Install-Module -Name PSWindowsUpdate
Get-WindowsUpdate -MicrosoftUpdate
Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot

# 4. Remote Desktop Enablement
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0
New-NetFirewallRule -DisplayName "Allow RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow

# 5. Time and Region
Set-TimeZone -Id "Eastern Standard Time"
Set-WinUserLanguage -Language en-US
```

## 📁 File Services and Storage

### File Server Setup
```powershell
# Install File Server Role
Install-WindowsFeature -Name File-Services, FS-FileServer
Install-WindowsFeature -Name File-Services, FS-Resource-Manager

# Create Shared Folders
# Create directory structure
New-Item -Path "C:\Shares" -ItemType Directory
New-Item -Path "C:\Shares\Public" -ItemType Directory
New-Item -Path "C:\Shares\Development" -ItemType Directory

# Configure sharing
New-SmbShare -Name "Public" -Path "C:\Shares\Public" -ReadAccess "Everyone"
New-SmbShare -Name "Development" -Path "C:\Shares\Development" -ChangeAccess "Developers" -FullAccess "Administrators"

# Configure NTFS permissions
# Development folder permissions
$acl = Get-Acl "C:\Shares\Development"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators","FullControl","Allow")
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Developers","Modify","Allow")
Set-Acl "C:\Shares\Development" $acl

# Public folder permissions
$acl = Get-Acl "C:\Shares\Public"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","Read","Allow")
Set-Acl "C:\Shares\Public" $acl
```

### Storage Management
```powershell
# Disk Management Commands
# List all disks
Get-Disk

# Initialize and partition disks
Initialize-Disk -Number 1 -PartitionStyle MBR
New-Partition -DiskNumber 1 -UseMaximumSize -AssignDriveLetter E
Format-Volume -DriveLetter E -FileSystem NTFS -Confirm:$false

# Storage Spaces (Windows Server 2012+)
# Create storage pool
$disks = Get-PhysicalDisk -CanPool $true
New-StoragePool -FriendlyName "DataPool" -PhysicalDisks $disks

# Create virtual disk
New-VirtualDisk -StoragePoolFriendlyName "DataPool" -Size 1TB
New-Partition -DiskNumber (Get-VirtualDisk -FriendlyName "DataPool").Number -UseMaximumSize -AssignDriveLetter F
Format-Volume -DriveLetter F -FileSystem NTFS -Confirm:$false

# Quota Management
# Enable disk quotas
Enable-Quota -Drive F
New-Quota -Drive F -Path F:\Users -SoftLimit 50GB -HardLimit 60GB

# File Server Resource Manager (FSRM)
# Install FSRM
Install-WindowsFeature -Name FS-Resource-Manager

# Configure quotas and screening
New-FsrmQuota -Path "F:\Users" -SoftLimit 50GB -HardLimit 60GB -Description "User storage quota"
New-FsrmFileScreen -Path "F:\Shares" -IncludeGroup "Media Files" -Executable $false -Description "Block media files"
```

## 🔐 Active Directory Administration

### Domain Controller Setup
```powershell
# Install Active Directory Domain Services
Install-WindowsFeature -Name AD-Domain-Services
Install-WindowsFeature -Name DNS
Install-WindowsFeature -Name RSAT-AD-Tools

# Create New Forest
Import-Module ADDSDeployment
$cred = Get-Credential
Install-ADDSForest -DomainName "homelab.local" -DomainNetbiosName "HOMELAB" -ForestMode "WinThreshold" -DatabasePath "C:\Windows\NTDS" -SysvolPath "C:\Windows\SYSVOL" -SafeModeAdministratorPassword $cred

# DNS Configuration
# Verify DNS zones
Get-DnsServerZone
Add-DnsServerPrimaryZone -NetworkID "192.168.1.0/24" -ZoneName "1.168.192.in-addr.arpa" -ReplicationScope Domain

# Domain Controller Promotion (additional DCs)
Install-ADDSDomainController -DomainName "homelab.local" -Credential $cred

# Verify AD Installation
Test-ComputerSecureChannel -Verbose
Get-ADDomainController -Filter *
Get-ADDomain
```

### User and Group Management
```powershell
# Create Organizational Units
New-ADOrganizationalUnit -Name "Servers" -Path "DC=homelab,DC=local"
New-ADOrganizationalUnit -Name "Users" -Path "DC=homelab,DC=local"
New-ADOrganizationalUnit -Name "Groups" -Path "DC=homelab,DC=local"

# Create User Accounts
$userParams = @{
    SamAccountName = "jsmith"
    UserPrincipalName = "jsmith@homelab.local"
    Name = "John Smith"
    GivenName = "John"
    Surname = "Smith"
    EmailAddress = "jsmith@homelab.local"
    Department = "IT"
    Title = "Developer"
    Office = "Homelab"
    AccountPassword = (ConvertTo-SecureString "TempPass123!" -AsPlainText -Force)
    Enabled = $true
    Path = "OU=Users,DC=homelab,DC=local"
}
New-ADUser @userParams

# Bulk User Creation
$users = Import-Csv "C:\temp\users.csv"
foreach ($user in $users) {
    New-ADUser -SamAccountName $user.Username -UserPrincipalName "$($user.Username)@homelab.local" -Name $user.FullName -AccountPassword (ConvertTo-SecureString "TempPass123!" -AsPlainText -Force) -Enabled $true -Path "OU=Users,DC=homelab,DC=local"
}

# Group Management
# Create security groups
New-ADGroup -Name "Developers" -GroupScope Global -GroupCategory Security
New-ADGroup -Name "Domain Admins" -GroupScope Global -GroupCategory Security
New-ADGroup -Name "File Server Users" -GroupScope Global -GroupCategory Security

# Add users to groups
Add-ADGroupMember -Identity "Developers" -Members "jsmith"
Add-ADGroupMember -Identity "File Server Users" -Members "jsmith","asmith"

# Computer Objects
# Join computer to domain (already done if DC)
# For workstations:
Add-Computer -DomainName "homelab.local" -Name "WKSTN-01"
```

### Group Policy Management
```powershell
# Group Policy Management Console (GPMC) or PowerShell
Import-Module GroupPolicy

# Create new GPO
New-GPO -Name "Homelab Workstation Configuration" -Comment "Base configuration for homelab workstations"

# Configure security policies
$gpo = Get-GPO -Name "Homelab Workstation Configuration"

# Password policy
Set-GPRegistryValue -Name "Password complexity" -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" -ValueName "PasswordComplexity" -Value 1 -Type DWord -Policy $gpo
Set-GPRegistryValue -Name "Minimum password length" -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" -ValueName "MinimumPasswordLength" -Value 8 -Type DWord -Policy $gpo

# Account lockout policy
Set-GPRegistryValue -Name "Account lockout threshold" -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" -ValueName "LockoutBadCount" -Value 5 -Type DWord -Policy $gpo
Set-GPRegistryValue -Name "Account lockout duration" -Key "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" -ValueName "LockoutDuration" -Value 30 -Type DWord -Policy $gpo

# User rights assignment
# Remote Desktop access
Set-GPPermission -Name "Allow log on through Remote Desktop Services" -Policy $gpo -PermissionDenied $false -AccountName "BUILTIN\Remote Desktop Users"

# Firewall configuration
# Enable Windows Firewall
Set-GPRegistryValue -Name "Enable firewall" -Key "HKLM\Software\Policies\Microsoft\WindowsFirewall\DomainProfile" -ValueName "EnableFirewall" -Value 1 -Type DWord -Policy $gpo

# Link GPO to OU
New-GPLink -Name "Homelab Workstation Configuration" -Target "OU=Workstations,DC=homelab,DC=local"

# Configure Group Policy processing time
$gpo = Get-GPO -Name "Homelab Workstation Configuration"
$gpo.General.ComputerPolicyEnabled = $true
```

## 🔄 Windows Server Roles

### DHCP Server Configuration
```powershell
# Install DHCP Server Role
Install-WindowsFeature -Name DHCP
Install-WindowsFeature -Name RSAT-DHCP

# Create DHCP Scope
Add-DhcpServerv4Scope -Name "Homelab Network" -StartRange "192.168.1.100" -EndRange "192.168.1.200" -SubnetMask "255.255.255.0" -State Active

# Configure scope options
Set-DhcpServerv4OptionValue -ComputerName "HOMELAB-SRV01" -DnsServer "192.168.1.1" -RouterId 192.168.1.1 -DnsDomain "homelab.local"

# DHCP Reservations
Add-DhcpServerv4Reservation -ComputerName "HOMELAB-SRV01" -ScopeId "192.168.1.0" -IPAddress "192.168.1.50" -ClientId "00-15-5D-01-23-45" -Name "File Server" -Description "Reserved for file server"

# DHCP Failover (for high availability)
# On primary server
Add-DhcpServerv4Failover -ComputerName "HOMELAB-SRV01" -PartnerServer "HOMELAB-SRV02" -SharedSecret "BackupSecret123" -MaxClientLeadTime 1:00:00 -State Active -Force
```

### DNS Server Configuration
```powershell
# DNS Server is installed with AD Domain Services
# Create additional zones if needed

# Create forward lookup zone
Add-DnsServerPrimaryZone -Name "external.local" -ZoneFile "external.local.dns" -ReplicationScope Domain

# Add records
Add-DnsServerResourceRecord -Name "web" -ZoneName "external.local" -ComputerName "HOMELAB-SRV01" -TimeToLive 01:00:00
Add-DnsServerResourceRecord -Name "vpn" -ZoneName "external.local" -IPv4Address "192.168.1.200" -TimeToLive 01:00:00

# Conditional forwarding
Add-DnsServerConditionalForwarder -IPAddress 8.8.8.8 -IPAddresses 8.8.4.4 -ZoneName "internet.com"

# DNS Security
# Configure DNSSEC
Set-DnsServerSetting -ComputerName "HOMELAB-SRV01" -EnableDnsSec $true
Set-DnsServerSetting -ComputerName "HOMELAB-SRV01" -EnableEDnsProbes $true

# DNS troubleshooting
Test-DnsServer -IPAddress 192.168.1.1 -Name "google.com"
Resolve-DnsName -Name "homelab.local" -Type A
```

### IIS Web Server Setup
```powershell
# Install IIS and required features
Install-WindowsFeature -Name Web-Server
Install-WindowsFeature -Name Web-WebServer
Install-WindowsFeature -Name Web-Common-Http
Install-WindowsFeature -Name Web-Static-Content
Install-WindowsFeature -Name Web-Default-Doc
Install-WindowsFeature -Name Web-App-Dev

# Create website
Import-Module WebAdministration
New-Website -Name "Homelab Portal" -Port 80 -PhysicalPath "C:\inetpub\homelab"
New-Website -Name "Homelab API" -Port 8080 -PhysicalPath "C:\inetpub\api"

# Configure HTTPS
# Create self-signed certificate
$cert = New-SelfSignedCertificate -DnsName "homelab.local" -CertStoreLocation "cert:\LocalMachine\My"

# Bind HTTPS site
New-Website -Name "Homelab Portal Secure" -Port 443 -PhysicalPath "C:\inetpub\homelab" -SslFlags 1
New-WebBinding -Name "Homelab Portal Secure" -Port 443 -Protocol https -SslFlags 1 -Certificate $cert

# Application Pools
New-WebAppPool -Name "HomelabAPI" -Force $true -RuntimeVersion v4.0 -ProcessModel Integrated

# URL Rewrite and Security
# Install URL Rewrite Module
Install-WindowsFeature -Name Web-Url-Auth
Install-WindowsFeature -Name Web-Filtering
Install-WindowsFeature -Name Web-Basic-Auth
Install-WindowsFeature -Name Windows-Authentication

# Configure security headers
# Add to web.config
$webConfig = @"
<configuration>
  <system.webServer>
    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="DENY" />
        <add name="X-XSS-Protection" value="1; mode=block" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
"
Set-Content -Path "C:\inetpub\homelab\web.config" -Value $webConfig
```

## 🔍 Monitoring and Performance

### Performance Monitoring
```powershell
# Performance Monitor Commands
# Get performance counters
Get-Counter "\\Processor(_Total)\% Processor Time"
Get-Counter "\\Memory\Available MBytes"
Get-Counter "\\Network Interface(*)\Bytes Total/sec"
Get-Counter "\\PhysicalDisk(_Total)\Disk Reads/sec"

# Create performance data collector
$collector = New-Object -ComObject Pla.DataCollectorSet
$collector.Query = "\\Processor(_Total)\% Processor Time", "\\Memory\Available MBytes"
$collector.DataCollectorSetType = 1
$collector.Start("C:\PerfLogs\HomelabPerformance")

# Windows Server Manager (GUI equivalent)
# Server Manager Dashboard
Get-Service | Where-Object {$_.Status -eq "Running"}
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-EventLog -LogName System -EntryType Error -Newest 20
```

### Event Log Management
```powershell
# Event Log Analysis
# Get recent system errors
Get-EventLog -LogName System -EntryType Error -After (Get-Date).AddDays(-1) | Format-Table TimeGenerated, Source, InstanceID, Message

# Security event monitoring
Get-EventLog -LogName Security -InstanceId 4625 -Newest 50 | Format-Table TimeGenerated, Message

# Custom event log creation
New-EventLog -LogName "Homelab Applications" -Source "HomelabMonitor"

# Write to custom log
Write-EventLog -LogName "Homelab Applications" -Source "HomelabMonitor" -EventId 1001 -EntryType Information -Message "Application started successfully"

# Log rotation and cleanup
# Configure event log retention
Limit-EventLog -LogName Application -MaximumSize 20MB -OverflowAction OverwriteOlder
Limit-EventLog -LogName System -MaximumSize 50MB -OverflowAction OverwriteOlder
```

### Windows Backup
```powershell
# Windows Server Backup (Wbadmin)
# Install Windows Server Backup feature
Install-WindowsFeature -Name Windows-Server-Backup

# Create backup schedule
$policy = New-WBPolicy
$backup = Add-WBBackupTarget -Policy $policy -TargetType Volume -VolumePath "C:\"
$backup = Add-WBBackupTarget -Policy $backup -TargetType Volume -VolumePath "E:\"
$policy = Add-WBSchedule -Policy $policy -ScheduleType Daily -Time 02:00
Set-WBPolicy -Policy $policy

# Manual backup
$backup = Start-WBBackup -Policy $policy -BackupTargets $backup.Targets -Async
$backup.JobId

# Monitor backup status
Get-WBJob -JobId $backup.JobId

# Bare metal backup
# For full system recovery
wbadmin start systemstatebackup -backuptarget:"E:\SystemStateBackup"
wbadmin start backup -include:C:,D: -backuptarget:"E:\FullBackup"
```

## 🛡️ Security and Hardening

### Windows Security
```powershell
# Windows Defender Configuration
# Check status
Get-MpComputerStatus

# Configure real-time protection
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -DisableRealtimeMonitoring $true

# Exclusions for homelab applications
Add-MpPreference -ExclusionPath "C:\Homelab\*"
Add-MpPreference -ExclusionProcess "homelab-service.exe"

# Scheduled scans
Set-MpPreference -ScanScheduleTime 02:00:00
Start-MpScan -ScanType QuickScan
```

### Windows Firewall
```powershell
# Windows Firewall Configuration
# Enable firewall profiles
Set-NetFirewallProfile -Profile Domain -Enabled True
Set-NetFirewallProfile -Profile Private -Enabled True
Set-NetFirewallProfile -Profile Public -Enabled True

# Create firewall rules
# Allow specific services
New-NetFirewallRule -DisplayName "Homelab Web Server" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -Enabled True
New-NetFirewallRule -DisplayName "Homelab SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow -Enabled True
New-NetFirewallRule -DisplayName "Homelab File Server" -Direction Inbound -Protocol TCP -LocalPort 445 -Action Allow -Enabled True

# Block specific protocols
New-NetFirewallRule -DisplayName "Block Telnet" -Direction Inbound -Protocol TCP -LocalPort 23 -Action Block -Enabled True

# Advanced firewall rules
# Block specific IPs
New-NetFirewallRule -DisplayName "Block Suspicious IP" -Direction Inbound -RemoteAddress "192.168.1.200" -Action Block -Enabled True

# Configure logging
Set-NetFirewallSetting -Enabled True -PolicyStore Domain
Set-NetFirewallSetting -LoggingAllowed True -PolicyStore Domain
Set-NetFirewallSetting -LoggingBlocked True -PolicyStore Domain
Set-NetFirewallSetting -LogMaxSize 4096 -PolicyStore Domain
```

### User Account Control (UAC)
```powershell
# UAC Configuration
# Check UAC status
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA"

# Configure UAC settings
# Standard user UAC level
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2 -Force

# Administrator UAC level
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 1 -Force

# UAC virtualization
# Enable UAC virtualization for file/registry operations
Enable-UACVirtualization

# Disable UAC (not recommended for production)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 0 -Force
```

## 🚀 PowerShell Automation

### PowerShell Scripts
```powershell
# Automated Server Setup Script
# Save as Setup-HomelabServer.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,
    
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [Parameter(Mandatory=$true)]
    [string]$AdminPassword
)

# Function to log actions
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor Green
    Add-Content -Path "C:\SetupLogs\server-setup.log" -Value "[$timestamp] $Message"
}

try {
    Write-Log "Starting server setup process"
    
    # Step 1: Configure computer identity
    Write-Log "Configuring computer name: $ComputerName"
    Rename-Computer -NewName $ComputerName -Force -Restart
    
    # Step 2: Install required roles and features
    Write-Log "Installing server roles"
    $features = @(
        "File-Services",
        "FS-FileServer", 
        "AD-Domain-Services",
        "DNS",
        "DHCP"
    )
    
    foreach ($feature in $features) {
        Write-Log "Installing feature: $feature"
        Install-WindowsFeature -Name $feature -IncludeManagementTools
    }
    
    # Step 3: Create domain (if this is the first DC)
    Write-Log "Creating Active Directory domain: $DomainName"
    $cred = New-Object System.Management.Automation.PSCredential("Administrator", (ConvertTo-SecureString $AdminPassword -AsPlainText -Force))
    Install-ADDSForest -DomainName $DomainName -SafeModeAdministratorPassword $cred -Force
    
    Write-Log "Server setup completed successfully"
    Write-Log "Computer will restart to complete domain controller promotion"
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log "ERROR: $($_.Exception.StackTrace)"
}
```

### Scheduled Tasks
```powershell
# Create scheduled tasks for maintenance
# Daily backup task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-Command 'Start-WBBackup -Policy $backupPolicy'"
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries $false -DontStopIfGoingOnBatteries $true

Register-ScheduledTask -TaskName "Daily Backup" -Action $action -Trigger $trigger -Settings $settings -User "NT AUTHORITY\SYSTEM"

# Weekly maintenance task
$weeklyAction = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-Command 'C:\Scripts\Maintenance.ps1'"
$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 03:00

Register-ScheduledTask -TaskName "Weekly Maintenance" -Action $weeklyAction -Trigger $weeklyTrigger -User "NT AUTHORITY\SYSTEM"

# Monitor scheduled tasks
Get-ScheduledTask | Where-Object {$_.State -eq "Ready"} | Select-Object TaskName, NextRunTime
```

## 🚨 Troubleshooting

### Common Issues
```powershell
# Active Directory Issues
# Test domain controller health
Test-ComputerSecureChannel
Test-ADDSForestInstallation

# Replication issues
Get-ADReplicationFailure
Get-ADReplicationPartnerMetadata
Get-ADReplicationQueueOperation

# DNS Issues
# Test DNS resolution
Test-Connection -ComputerName "google.com" -Port 53
Resolve-DnsName -Name "homelab.local"
Clear-DnsClientCache

# Network Issues
# Test network connectivity
Test-NetConnection -ComputerName "192.168.1.1" -Port 445
Test-NetConnection -ComputerName "8.8.8.8" -Port 53
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

### Recovery Tools
```powershell
# Windows Recovery Environment (WinRE)
# Create recovery USB
# Download Windows Assessment and Deployment Kit (ADK)
# Use Windows System Image Manager (DISM)
dism /online /export-driver /destination:C:\Drivers

# System Restore
Enable-ComputerRestore -Drive "C:\"
Checkpoint-Computer -Description "Before application installation"
Restore-Computer -RestorePoint (Get-ComputerRestorePoint | Sort-Object CreationTime -Descending | Select-Object -First 1)

# Safe Mode
# Restart into safe mode
Shutdown /r /f /o safe

# Last Known Good Configuration
# Boot with F8 key during startup
# Select "Last Known Good Configuration"
```

### Backup and Restore
```powershell
# System state backup
wbadmin start systemstatebackup -backuptarget:"\\BackupServer\Backups\$env:COMPUTERNAME\SystemState"

# Complete system backup
$backupPolicy = Get-WBPolicy
$backupPolicy = Add-WBBackupTarget -Policy $backupPolicy -TargetType Volume -VolumePath "C:","D:","E:"
Set-WBPolicy -Policy $backupPolicy

# Restore from backup
wbadmin start sysrecovery -version:MM-DD-YYYY-nn -backuptarget:"\\BackupServer\Backups\SystemStateBackup"

# Verify backup integrity
Get-WBBackupSet | Format-Table BackupTime, BackupTarget, Version
Get-WBBackupVolume -BackupPolicy $backupPolicy
```

## 📖 Further Reading

### Documentation
- [Microsoft Windows Server Documentation](https://docs.microsoft.com/en-us/windows-server/)
- [Microsoft Docs PowerShell](https://docs.microsoft.com/en-us/powershell/)
- [Active Directory Documentation](https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/)

### Books and Courses
- [Windows Server Inside Out](https://www.microsoftpressstore.com/learning-powershell)
- [MCSA Study Guide](https://www.microsoft.com/en-us/learning/mcsa-windows-server-2016)
- [Microsoft Learn](https://docs.microsoft.com/en-us/learn/)

### Communities
- Reddit: r/sysadmin, r/PowerShell, r/homelab
- Microsoft Tech Community
- Windows Server Forums
- PowerShell.org Community

### Advanced Topics
- Hyper-V virtualization
- Azure Hybrid Identity
- Windows Admin Center
- PowerShell DSC (Desired State Configuration)
- Windows Container deployment

---

**Ready to dive deeper?** Check our [System Administration](index.md) overview for comprehensive admin planning!
