# Microsoft Sentinel Cheatsheet intermediate

Microsoft Sentinel is a cloud-native Security Information and Event Management (SIEM) and Security Orchestration, Automation, and Response (SOAR) solution that provides intelligent security analytics and threat intelligence across the enterprise. Built on Azure, Sentinel delivers scalable security monitoring, advanced threat detection, and automated incident response capabilities that enable security teams to detect, investigate, and respond to threats at cloud scale.

## Platform Overview

### Core Architecture

Microsoft Sentinel operates as a fully managed service within the Azure ecosystem, leveraging Azure Monitor Logs as its underlying data platform. The architecture consists of several integrated components that work together to provide comprehensive security operations capabilities.

The data ingestion layer supports a wide variety of data sources through native connectors, REST APIs, and custom integrations. Sentinel can collect data from Microsoft services (Office 365, Azure AD, Windows Security Events), third-party security tools, cloud platforms, network devices, and custom applications.

The analytics engine utilizes machine learning algorithms, behavioral analytics, and rule-based detection to identify potential security threats. Sentinel's detection capabilities include built-in analytics rules, custom KQL (Kusto Query Language) queries, machine learning models for anomaly detection, and threat intelligence integration.

### Key Features

```powershell
# Core Platform Capabilities
- Cloud-native SIEM and SOAR platform
- Advanced threat detection and analytics
- Security orchestration and automated response
- Threat intelligence integration
- Machine learning and behavioral analytics
- Custom dashboards and workbooks
- Incident management and investigation
- Threat hunting capabilities
```

## Data Connectors and Ingestion

### Microsoft Service Connectors

```powershell
# Azure Active Directory connector
Connect-AzAccount
Set-AzContext -SubscriptionId "<subscription-id>"

# Enable Azure AD connector via PowerShell
$resourceGroupName = "sentinel-rg"
$workspaceName = "sentinel-workspace"
$dataConnectorId = "AzureActiveDirectory"

New-AzSentinelDataConnector -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName -Id $dataConnectorId -Kind "AzureActiveDirectory"

# Office 365 connector configuration
$office365Config = @\\\\{
    tenantId = "<tenant-id>"
    dataTypes = @\\\\{
        exchange = @\\\\{ state = "Enabled" \\\\}
        sharePoint = @\\\\{ state = "Enabled" \\\\}
        teams = @\\\\{ state = "Enabled" \\\\}
    \\\\}
\\\\}

# Azure Security Center connector
$ascConfig = @\\\\{
    subscriptionId = "<subscription-id>"
    dataTypes = @\\\\{
        alerts = @\\\\{ state = "Enabled" \\\\}
        recommendations = @\\\\{ state = "Enabled" \\\\}
    \\\\}
\\\\}
```

### Third-Party Connectors

```bash
# Syslog connector configuration
# Configure rsyslog on Linux systems
sudo nano /etc/rsyslog.d/95-omsagent.conf

# Add configuration for Sentinel
*.* @@<workspace-id>.ods.opinsights.azure.com:514

# Restart rsyslog service
sudo systemctl restart rsyslog

# CEF (Common Event Format) connector
# Configure log forwarding for CEF events
logger -p local4.warn -t CEF "CEF:0|Microsoft|ATA|1.9.0.0|AbnormalSensitiveGroupMembershipChangeSuspiciousActivity|Abnormal modification of sensitive groups|5|start=2018-12-12T18:52:58.0000000Z app=GroupMembershipChangeEvent suser=krbtgt msg=krbtgt has been added to the following sensitive groups: Domain Admins."

# Custom REST API connector
curl -X POST "https://<workspace-id>.ods.opinsights.azure.com/api/logs?api-version=2016-04-01" \
  -H "Authorization: SharedKey <workspace-id>:<shared-key>" \
  -H "Content-Type: application/json" \
  -H "Log-Type: CustomSecurityLog" \
  -d '\\\\{
    "timestamp": "2023-01-01T12:00:00Z",
    "severity": "High",
    "source_ip": "192.168.1.100",
    "event_type": "suspicious_login",
    "user": "admin@company.com"
  \\\\}'
```

### Azure Monitor Agent Configuration

```powershell
# Install Azure Monitor Agent
$vmName = "security-vm"
$resourceGroupName = "security-rg"
$location = "East US"

# Create data collection rule
$dcrConfig = @\\\\{
    location = $location
    properties = @\\\\{
        dataSources = @\\\\{
            windowsEventLogs = @(
                @\\\\{
                    name = "SecurityEvents"
                    streams = @("Microsoft-SecurityEvent")
                    xPathQueries = @(
                        "Security!*[System[(EventID=4624 or EventID=4625 or EventID=4648)]]"
                    )
                \\\\}
            )
            syslog = @(
                @\\\\{
                    name = "SyslogEvents"
                    streams = @("Microsoft-Syslog")
                    facilityNames = @("auth", "authpriv", "daemon")
                    logLevels = @("Warning", "Error", "Critical")
                \\\\}
            )
        \\\\}
        destinations = @\\\\{
            logAnalytics = @(
                @\\\\{
                    workspaceResourceId = "/subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>"
                    name = "SentinelWorkspace"
                \\\\}
            )
        \\\\}
        dataFlows = @(
            @\\\\{
                streams = @("Microsoft-SecurityEvent")
                destinations = @("SentinelWorkspace")
            \\\\}
        )
    \\\\}
\\\\}
```

## KQL (Kusto Query Language) for Security Analytics

### Basic KQL Syntax

```kql
// Simple table query
SecurityEvent
|take 10

// Time range filtering
SecurityEvent
|where TimeGenerated > ago(1h)

// Field filtering
SecurityEvent
|where EventID == 4624
|where Account contains "admin"

// Multiple conditions
SecurityEvent
|where TimeGenerated > ago(24h)
|where EventID in (4624, 4625, 4648)
|where Account !contains "SYSTEM"

// String operations
SecurityEvent
|where Activity contains "Logon"
|where Account startswith "admin"
|where Computer endswith ".contoso.com"
```

### Advanced Analytics Queries

```kql
// Failed login analysis
SecurityEvent
|where EventID == 4625
|where TimeGenerated > ago(1h)
|summarize FailedAttempts = count() by Account, Computer, IpAddress
|where FailedAttempts > 5
|sort by FailedAttempts desc

// Privilege escalation detection
SecurityEvent
|where EventID == 4672
|where TimeGenerated > ago(24h)
|where SubjectUserName !in ("SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE")
|summarize ElevationCount = count() by SubjectUserName, Computer
|where ElevationCount > 10
|sort by ElevationCount desc

// Lateral movement detection
SecurityEvent
|where EventID == 4624
|where LogonType in (3, 10)
|where TimeGenerated > ago(1h)
|summarize UniqueComputers = dcount(Computer) by Account
|where UniqueComputers > 5
|sort by UniqueComputers desc

// Anomalous process execution
SecurityEvent
|where EventID == 4688
|where TimeGenerated > ago(1h)
|where Process contains "powershell.exe" or Process contains "cmd.exe"
|where CommandLine contains "Invoke-" or CommandLine contains "Download"
|project TimeGenerated, Computer, Account, Process, CommandLine
|sort by TimeGenerated desc
```

### Threat Hunting Queries

```kql
// Suspicious PowerShell activity
SecurityEvent
|where EventID == 4688
|where Process endswith "powershell.exe"
|where CommandLine has_any ("Invoke-Expression", "IEX", "Invoke-WebRequest", "DownloadString", "EncodedCommand")
|extend DecodedCommand = base64_decode_tostring(extract(@"-EncodedCommand\s+([A-Za-z0-9+/=]+)", 1, CommandLine))
|project TimeGenerated, Computer, Account, CommandLine, DecodedCommand
|sort by TimeGenerated desc

// Living off the land techniques
SecurityEvent
|where EventID == 4688
|where Process has_any ("certutil.exe", "bitsadmin.exe", "regsvr32.exe", "rundll32.exe", "mshta.exe")
|where CommandLine has_any ("http", "ftp", "download", "urlcache", "split")
|project TimeGenerated, Computer, Account, Process, CommandLine
|sort by TimeGenerated desc

// Credential dumping detection
SecurityEvent
|where EventID in (4656, 4663)
|where ObjectName has_any ("lsass.exe", "SAM", "SECURITY", "SYSTEM")
|where AccessMask in ("0x1010", "0x1400", "0x100000")
|summarize AccessAttempts = count() by Account, Computer, ObjectName
|where AccessAttempts > 3
|sort by AccessAttempts desc

// DNS tunneling detection
DnsEvents
|where TimeGenerated > ago(1h)
|where QueryType == "TXT" or QueryType == "NULL"
|where Name contains "." and strlen(Name) > 50
|summarize QueryCount = count() by ClientIP, Name
|where QueryCount > 10
|sort by QueryCount desc
```

### Machine Learning Analytics

```kql
// User behavior analytics
SigninLogs
|where TimeGenerated > ago(30d)
|where ResultType == "0"
|summarize
    LoginCount = count(),
    UniqueIPs = dcount(IPAddress),
    UniqueLocations = dcount(Location),
    UniqueDevices = dcount(DeviceDetail.deviceId)
    by UserPrincipalName
|extend RiskScore = (UniqueIPs * 2) + (UniqueLocations * 3) + (UniqueDevices * 1)
|where RiskScore > 20
|sort by RiskScore desc

// Anomalous data transfer detection
CommonSecurityLog
|where TimeGenerated > ago(1h)
|where DeviceVendor == "Palo Alto Networks"
|where Activity == "TRAFFIC"
|summarize TotalBytes = sum(SentBytes + ReceivedBytes) by SourceIP, DestinationIP
|extend BytesInMB = TotalBytes / (1024 * 1024)
|where BytesInMB > 1000
|sort by BytesInMB desc

// Behavioral baseline deviation
SecurityEvent
|where TimeGenerated > ago(30d)
|where EventID == 4624
|where LogonType == 2
|summarize
    AvgLoginsPerDay = count() / 30,
    StdDev = stdev(todouble(1))
    by Account
|join kind=inner (
    SecurityEvent
|where TimeGenerated > ago(1d)
|where EventID == 4624
|where LogonType == 2
|summarize TodayLogins = count() by Account
) on Account
|extend Deviation = abs(TodayLogins - AvgLoginsPerDay) / StdDev
|where Deviation > 3
|sort by Deviation desc
```

## Analytics Rules and Detection

### Scheduled Analytics Rules

```kql
// Create scheduled rule for brute force detection
let threshold = 10;
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4625
|summarize FailedAttempts = count() by Account, IpAddress, Computer
|where FailedAttempts >= threshold
|extend
    Severity = case(
        FailedAttempts >= 50, "High",
        FailedAttempts >= 25, "Medium",
        "Low"
    ),
    Tactics = "CredentialAccess",
    Techniques = "T1110"
|project Account, IpAddress, Computer, FailedAttempts, Severity, Tactics, Techniques

// Suspicious file creation rule
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4663
|where ObjectName endswith ".exe" or ObjectName endswith ".dll" or ObjectName endswith ".bat"
|where ObjectName has_any ("temp", "appdata", "programdata")
|where AccessMask == "0x2"
|extend
    Severity = "Medium",
    Tactics = "Execution",
    Techniques = "T1059"
|project TimeGenerated, Computer, Account, ObjectName, Severity, Tactics, Techniques

// Privilege escalation rule
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4672
|where SubjectUserName !in ("SYSTEM", "LOCAL SERVICE", "NETWORK SERVICE")
|where PrivilegeList has_any ("SeDebugPrivilege", "SeTakeOwnershipPrivilege", "SeLoadDriverPrivilege")
|extend
    Severity = "High",
    Tactics = "PrivilegeEscalation",
    Techniques = "T1134"
|project TimeGenerated, Computer, SubjectUserName, PrivilegeList, Severity, Tactics, Techniques
```

### Near Real-Time (NRT) Rules

```kql
// Real-time malware detection
SecurityEvent
|where EventID == 4688
|where Process has_any ("mimikatz", "procdump", "pwdump", "fgdump")
|extend
    Severity = "High",
    Tactics = "CredentialAccess",
    Techniques = "T1003"
|project TimeGenerated, Computer, Account, Process, CommandLine, Severity, Tactics, Techniques

// Immediate threat response
SecurityEvent
|where EventID == 4625
|where Account == "Administrator"
|where IpAddress !startswith "192.168." and IpAddress !startswith "10." and IpAddress !startswith "172."
|extend
    Severity = "Critical",
    Tactics = "InitialAccess",
    Techniques = "T1078"
|project TimeGenerated, Computer, Account, IpAddress, Severity, Tactics, Techniques
```

### Machine Learning Rules

```kql
// Anomaly detection template
let training_data =
    SecurityEvent
|where TimeGenerated between (ago(30d) .. ago(1d))
|where EventID == 4624
|summarize LoginCount = count() by Account, bin(TimeGenerated, 1h)
|summarize AvgLogins = avg(LoginCount), StdDev = stdev(LoginCount) by Account;
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4624
|summarize CurrentLogins = count() by Account
|join kind=inner training_data on Account
|extend AnomalyScore = abs(CurrentLogins - AvgLogins) / StdDev
|where AnomalyScore > 3
|extend
    Severity = case(AnomalyScore > 5, "High", "Medium"),
    Tactics = "InitialAccess",
    Techniques = "T1078"
|project Account, CurrentLogins, AvgLogins, AnomalyScore, Severity, Tactics, Techniques
```

## Incident Management and Investigation

### Incident Creation and Assignment

```powershell
# Create incident via PowerShell
$incidentParams = @\\\\{
    ResourceGroupName = "sentinel-rg"
    WorkspaceName = "sentinel-workspace"
    IncidentId = "incident-001"
    Title = "Suspicious Login Activity Detected"
    Description = "Multiple failed login attempts from external IP address"
    Severity = "High"
    Status = "New"
    Owner = @\\\\{
        email = "analyst@company.com"
        assignedTo = "Security Analyst"
        objectId = "<user-object-id>"
    \\\\}
    Labels = @(
        @\\\\{ labelName = "BruteForce"; labelType = "User" \\\\}
        @\\\\{ labelName = "ExternalIP"; labelType = "User" \\\\}
    )
\\\\}

New-AzSentinelIncident @incidentParams

# Update incident status
$updateParams = @\\\\{
    ResourceGroupName = "sentinel-rg"
    WorkspaceName = "sentinel-workspace"
    IncidentId = "incident-001"
    Status = "Active"
    Classification = "TruePositive"
    ClassificationComment = "Confirmed malicious activity"
    ClassificationReason = "SuspiciousActivity"
\\\\}

Update-AzSentinelIncident @updateParams
```

### Investigation Queries

```kql
// Timeline reconstruction
let incident_time = datetime(2023-01-01T10:00:00Z);
let suspect_user = "john.doe@company.com";
let time_window = 2h;
union
    (SecurityEvent|where TimeGenerated between ((incident_time - time_window) .. (incident_time + time_window))|where Account contains suspect_user),
    (SigninLogs|where TimeGenerated between ((incident_time - time_window) .. (incident_time + time_window))|where UserPrincipalName == suspect_user),
    (AuditLogs|where TimeGenerated between ((incident_time - time_window) .. (incident_time + time_window))|where InitiatedBy.user.userPrincipalName == suspect_user)
|sort by TimeGenerated asc
|project TimeGenerated, Type, Activity, Account, Computer, IPAddress, Location

// Entity behavior analysis
let entity_ip = "192.168.1.100";
union
    (SecurityEvent|where IpAddress == entity_ip),
    (CommonSecurityLog|where SourceIP == entity_ip or DestinationIP == entity_ip),
    (DnsEvents|where ClientIP == entity_ip),
    (NetworkCommunicationEvents|where LocalIP == entity_ip or RemoteIP == entity_ip)
|summarize
    EventCount = count(),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated),
    EventTypes = make_set(Type),
    UniqueDestinations = dcount(DestinationIP)
    by SourceIP
|sort by EventCount desc

// Lateral movement tracking
let start_computer = "WORKSTATION-01";
SecurityEvent
|where EventID == 4624
|where LogonType in (3, 10)
|where Computer == start_computer
|extend NextHop = Computer
|join kind=inner (
    SecurityEvent
|where EventID == 4624
|where LogonType in (3, 10)
|where Computer != start_computer
) on Account
|where TimeGenerated1 > TimeGenerated
|project Account, SourceComputer = Computer, DestinationComputer = Computer1, TimeGenerated, TimeGenerated1
|sort by Account, TimeGenerated asc
```

### Evidence Collection

```kql
// Collect relevant artifacts
let investigation_timeframe = ago(24h);
let entities = dynamic(["suspicious.user@company.com", "192.168.1.100", "COMPROMISED-PC"]);
union
    (SecurityEvent
|where TimeGenerated > investigation_timeframe
|where Account has_any (entities) or Computer has_any (entities) or IpAddress has_any (entities)),
    (SigninLogs
|where TimeGenerated > investigation_timeframe
|where UserPrincipalName has_any (entities) or IPAddress has_any (entities)),
    (DeviceEvents
|where TimeGenerated > investigation_timeframe
|where DeviceName has_any (entities) or InitiatingProcessAccountName has_any (entities)),
    (EmailEvents
|where TimeGenerated > investigation_timeframe
|where SenderFromAddress has_any (entities) or RecipientEmailAddress has_any (entities))
|sort by TimeGenerated desc
|take 1000

// File hash analysis
DeviceFileEvents
|where TimeGenerated > ago(7d)
|where SHA256 in ("hash1", "hash2", "hash3")
|summarize
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated),
    DeviceCount = dcount(DeviceName),
    Devices = make_set(DeviceName)
    by SHA256, FileName
|sort by DeviceCount desc
```

## Automation and Orchestration (SOAR)

### Logic Apps Integration

```json
\\\\{
    "definition": \\\\{
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": \\\\{\\\\},
        "triggers": \\\\{
            "Microsoft_Sentinel_incident": \\\\{
                "type": "ApiConnectionWebhook",
                "inputs": \\\\{
                    "host": \\\\{
                        "connection": \\\\{
                            "name": "@parameters('$connections')['azuresentinel']['connectionId']"
                        \\\\}
                    \\\\},
                    "body": \\\\{
                        "callback_url": "@\\\\{listCallbackUrl()\\\\}"
                    \\\\},
                    "path": "/incident-creation"
                \\\\}
            \\\\}
        \\\\},
        "actions": \\\\{
            "Get_incident": \\\\{
                "type": "ApiConnection",
                "inputs": \\\\{
                    "host": \\\\{
                        "connection": \\\\{
                            "name": "@parameters('$connections')['azuresentinel']['connectionId']"
                        \\\\}
                    \\\\},
                    "method": "get",
                    "path": "/Incidents/subscriptions/@\\\\{encodeURIComponent(triggerBody()?['WorkspaceSubscriptionId'])\\\\}/resourceGroups/@\\\\{encodeURIComponent(triggerBody()?['WorkspaceResourceGroup'])\\\\}/workspaces/@\\\\{encodeURIComponent(triggerBody()?['WorkspaceId'])\\\\}/alerts/@\\\\{encodeURIComponent(triggerBody()?['SystemAlertId'])\\\\}"
                \\\\}
            \\\\},
            "Block_IP_in_firewall": \\\\{
                "type": "Http",
                "inputs": \\\\{
                    "method": "POST",
                    "uri": "https://firewall-api.company.com/block",
                    "headers": \\\\{
                        "Authorization": "Bearer @\\\\{parameters('firewall_token')\\\\}"
                    \\\\},
                    "body": \\\\{
                        "ip_address": "@\\\\{body('Get_incident')?['properties']?['relatedEntities'][0]?['properties']?['address']\\\\}",
                        "reason": "Blocked by Sentinel automation",
                        "duration": "24h"
                    \\\\}
                \\\\}
            \\\\},
            "Send_notification": \\\\{
                "type": "ApiConnection",
                "inputs": \\\\{
                    "host": \\\\{
                        "connection": \\\\{
                            "name": "@parameters('$connections')['teams']['connectionId']"
                        \\\\}
                    \\\\},
                    "method": "post",
                    "path": "/v1.0/teams/@\\\\{encodeURIComponent('security-team-id')\\\\}/channels/@\\\\{encodeURIComponent('incidents')\\\\}/messages",
                    "body": \\\\{
                        "body": \\\\{
                            "content": "[ALERT] High severity incident detected: @\\\\{body('Get_incident')?['properties']?['title']\\\\}\n\nIncident ID: @\\\\{body('Get_incident')?['properties']?['incidentNumber']\\\\}\nSeverity: @\\\\{body('Get_incident')?['properties']?['severity']\\\\}\nStatus: @\\\\{body('Get_incident')?['properties']?['status']\\\\}\n\nAutomatic response: IP address blocked in firewall"
                        \\\\}
                    \\\\}
                \\\\}
            \\\\}
        \\\\}
    \\\\}
\\\\}
```

### PowerShell Automation

```powershell
# Automated incident response script
param(
    [Parameter(Mandatory=$true)]
    [string]$IncidentId,

    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName
)

# Connect to Azure
Connect-AzAccount -Identity

# Get incident details
$incident = Get-AzSentinelIncident -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -IncidentId $IncidentId

# Extract entities
$entities = $incident.RelatedEntities

# Process each entity
foreach ($entity in $entities) \\\\{
    switch ($entity.Kind) \\\\{
        "Account" \\\\{
            # Disable user account
            $userPrincipalName = $entity.Properties.Name
            Write-Output "Disabling user account: $userPrincipalName"

            # Connect to Azure AD
            Connect-AzureAD
            $user = Get-AzureADUser -Filter "userPrincipalName eq '$userPrincipalName'"
            if ($user) \\\\{
                Set-AzureADUser -ObjectId $user.ObjectId -AccountEnabled $false
                Write-Output "User account disabled successfully"
            \\\\}
        \\\\}

        "Ip" \\\\{
            # Block IP address
            $ipAddress = $entity.Properties.Address
            Write-Output "Blocking IP address: $ipAddress"

            # Add to Azure Firewall block list
            $firewallPolicy = Get-AzFirewallPolicy -ResourceGroupName $ResourceGroupName -Name "SecurityPolicy"
            $blockRule = New-AzFirewallPolicyNetworkRule -Name "Block-$ipAddress" -Protocol "Any" -SourceAddress $ipAddress -DestinationAddress "*" -DestinationPort "*" -Action "Deny"

            # Update firewall policy
            $ruleCollection = $firewallPolicy.RuleCollectionGroups[0].Properties.RuleCollections[0]
            $ruleCollection.Rules += $blockRule
            Set-AzFirewallPolicy -InputObject $firewallPolicy
            Write-Output "IP address blocked successfully"
        \\\\}

        "Host" \\\\{
            # Isolate host
            $hostName = $entity.Properties.HostName
            Write-Output "Isolating host: $hostName"

            # Microsoft Defender for Endpoint isolation
            $isolationRequest = @\\\\{
                Comment = "Automated isolation due to security incident $IncidentId"
                IsolationType = "Full"
            \\\\}

            # Call Defender API to isolate machine
            $headers = @\\\\{
                'Authorization' = "Bearer $($env:DEFENDER_TOKEN)"
                'Content-Type' = 'application/json'
            \\\\}

            Invoke-RestMethod -Uri "https://api.securitycenter.microsoft.com/api/machines/$hostName/isolate" -Method Post -Headers $headers -Body ($isolationRequest|ConvertTo-Json)
            Write-Output "Host isolated successfully"
        \\\\}
    \\\\}
\\\\}

# Update incident with automation results
$updateComment = "Automated response completed: Users disabled, IPs blocked, hosts isolated"
Add-AzSentinelIncidentComment -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -IncidentId $IncidentId -Message $updateComment

# Update incident status
Update-AzSentinelIncident -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -IncidentId $IncidentId -Status "Active" -Classification "TruePositive"

Write-Output "Incident response automation completed successfully"
```

### Custom Connectors

```python
# Custom threat intelligence connector
import requests
import json
import hashlib
import hmac
import base64
import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class SentinelConnector:
    def __init__(self, workspace_id, shared_key):
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.log_type = "ThreatIntelligence"

    def build_signature(self, date, content_length, method, content_type, resource):
        x_headers = f"x-ms-date:\\\\{date\\\\}"
        string_to_hash = f"\\\\{method\\\\}\n\\\\{content_length\\\\}\n\\\\{content_type\\\\}\n\\\\{x_headers\\\\}\n\\\\{resource\\\\}"
        bytes_to_hash = bytes(string_to_hash, 'utf-8')
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
        authorization = f"SharedKey \\\\{self.workspace_id\\\\}:\\\\{encoded_hash\\\\}"
        return authorization

    def send_data(self, body):
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)

        signature = self.build_signature(rfc1123date, content_length, method, content_type, resource)

        uri = f"https://\\\\{self.workspace_id\\\\}.ods.opinsights.azure.com\\\\{resource\\\\}?api-version=2016-04-01"

        headers = \\\\{
            'content-type': content_type,
            'Authorization': signature,
            'Log-Type': self.log_type,
            'x-ms-date': rfc1123date
        \\\\}

        response = requests.post(uri, data=body, headers=headers)
        return response.status_code

# Threat intelligence integration
def collect_threat_intelligence():
    # Collect from multiple sources
    threat_data = []

    # VirusTotal integration
    vt_api_key = "your_virustotal_api_key"
    vt_url = "https://www.virustotal.com/vtapi/v2/file/report"

    file_hashes = ["hash1", "hash2", "hash3"]

    for file_hash in file_hashes:
        params = \\\\{'apikey': vt_api_key, 'resource': file_hash\\\\}
        response = requests.get(vt_url, params=params)

        if response.status_code == 200:
            vt_data = response.json()
            threat_data.append(\\\\{
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source": "VirusTotal",
                "indicator_type": "file_hash",
                "indicator_value": file_hash,
                "threat_type": "malware" if vt_data.get('positives', 0) > 0 else "clean",
                "confidence": vt_data.get('positives', 0) / vt_data.get('total', 1) * 100,
                "raw_data": json.dumps(vt_data)
            \\\\})

    # MISP integration
    misp_url = "https://your-misp-instance.com"
    misp_key = "your_misp_api_key"

    misp_headers = \\\\{
        'Authorization': misp_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    \\\\}

    misp_response = requests.get(f"\\\\{misp_url\\\\}/attributes/restSearch", headers=misp_headers)

    if misp_response.status_code == 200:
        misp_data = misp_response.json()
        for attribute in misp_data.get('response', \\\\{\\\\}).get('Attribute', []):
            threat_data.append(\\\\{
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "source": "MISP",
                "indicator_type": attribute.get('type'),
                "indicator_value": attribute.get('value'),
                "threat_type": attribute.get('category'),
                "confidence": 85,
                "raw_data": json.dumps(attribute)
            \\\\})

    return threat_data

# Send to Sentinel
def main():
    workspace_id = "your_workspace_id"
    shared_key = "your_shared_key"

    connector = SentinelConnector(workspace_id, shared_key)
    threat_data = collect_threat_intelligence()

    if threat_data:
        body = json.dumps(threat_data)
        response_code = connector.send_data(body)
        print(f"Data sent to Sentinel. Response code: \\\\{response_code\\\\}")
    else:
        print("No threat intelligence data to send")

if __name__ == "__main__":
    main()
```

## Workbooks and Visualization

### Security Operations Workbook

```kql
// Security overview dashboard queries
// Failed logins by location
SigninLogs
|where TimeGenerated > ago(24h)
|where ResultType != "0"
|summarize FailedLogins = count() by Location
|sort by FailedLogins desc
|take 10

// Top attacked users
SecurityEvent
|where TimeGenerated > ago(24h)
|where EventID == 4625
|summarize FailedAttempts = count() by Account
|sort by FailedAttempts desc
|take 10

// Security alerts by severity
SecurityAlert
|where TimeGenerated > ago(7d)
|summarize AlertCount = count() by AlertSeverity
|render piechart

// Incident response metrics
SecurityIncident
|where TimeGenerated > ago(30d)
|extend TimeToClose = iff(Status == "Closed", ClosedTime - CreatedTime, now() - CreatedTime)
|summarize
    AvgTimeToClose = avg(TimeToClose),
    TotalIncidents = count(),
    OpenIncidents = countif(Status != "Closed")
    by bin(TimeGenerated, 1d)
|render timechart
```

### Threat Hunting Workbook

```kql
// Suspicious process execution timeline
SecurityEvent
|where TimeGenerated > ago(7d)
|where EventID == 4688
|where Process has_any ("powershell.exe", "cmd.exe", "wscript.exe", "cscript.exe")
|where CommandLine has_any ("Invoke-", "Download", "http", "ftp", "base64")
|summarize ProcessCount = count() by bin(TimeGenerated, 1h), Process
|render timechart

// Network communication patterns
CommonSecurityLog
|where TimeGenerated > ago(24h)
|where DeviceVendor == "Palo Alto Networks"
|where Activity == "TRAFFIC"
|summarize
    TotalBytes = sum(SentBytes + ReceivedBytes),
    SessionCount = count()
    by SourceIP, DestinationIP
|where TotalBytes > 1000000000  // 1GB threshold
|sort by TotalBytes desc

// DNS query analysis
DnsEvents
|where TimeGenerated > ago(24h)
|where QueryType in ("TXT", "NULL", "CNAME")
|summarize QueryCount = count() by Name, ClientIP
|where QueryCount > 100
|sort by QueryCount desc

// File creation in suspicious locations
SecurityEvent
|where TimeGenerated > ago(24h)
|where EventID == 4663
|where ObjectName has_any ("\\temp\\", "\\appdata\\", "\\programdata\\")
|where ObjectName endswith ".exe" or ObjectName endswith ".dll" or ObjectName endswith ".bat"
|summarize FileCount = count() by Computer, Account, ObjectName
|sort by FileCount desc
```

## Performance Optimization and Best Practices

### Query Optimization

```kql
// Optimized query structure
SecurityEvent
|where TimeGenerated > ago(1h)  // Filter time first
|where EventID == 4624          // Filter specific events
|where LogonType == 2           // Additional filters early
|project TimeGenerated, Computer, Account, LogonType  // Project only needed columns
|summarize LoginCount = count() by Computer, Account
|where LoginCount > 10
|sort by LoginCount desc

// Use summarize instead of distinct when possible
// Less efficient
SecurityEvent
|where TimeGenerated > ago(1h)
|distinct Computer

// More efficient
SecurityEvent
|where TimeGenerated > ago(1h)
|summarize by Computer

// Optimize joins
// Use smaller table on the right side of join
let SmallTable =
    SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4624
|summarize by Account;
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4625
|join kind=inner SmallTable on Account
```

### Data Retention and Cost Management

```kql
// Monitor data ingestion by table
Usage
|where TimeGenerated > ago(30d)
|where IsBillable == true
|summarize TotalVolumeGB = sum(Quantity) / 1000 by DataType
|sort by TotalVolumeGB desc

// Analyze query costs
// Check scan data volume
SecurityEvent
|where TimeGenerated > ago(1h)
|summarize count()
// This query scans all SecurityEvent data for 1 hour

// Optimize with specific filters
SecurityEvent
|where TimeGenerated > ago(1h)
|where EventID == 4624  // Reduces scan volume significantly
|summarize count()

// Set up data retention policies
// Configure via PowerShell
$retentionPolicy = @\\\\{
    ResourceGroupName = "sentinel-rg"
    WorkspaceName = "sentinel-workspace"
    TableName = "SecurityEvent"
    RetentionInDays = 90
\\\\}

Set-AzOperationalInsightsTable @retentionPolicy
```

### Security and Compliance

```kql
// Monitor privileged access to Sentinel
AuditLogs
|where TimeGenerated > ago(24h)
|where Category == "RoleManagement"
|where ActivityDisplayName has_any ("Add member to role", "Remove member from role")
|where TargetResources[0].displayName has "Sentinel"
|project TimeGenerated, InitiatedBy.user.userPrincipalName, ActivityDisplayName, TargetResources[0].displayName

// Track data access patterns
LAQueryLogs
|where TimeGenerated > ago(7d)
|summarize
    QueryCount = count(),
    DataScannedGB = sum(DataScanned_MB) / 1000,
    UniqueQueries = dcount(QueryText)
    by AADEmail
|sort by DataScannedGB desc

// Compliance reporting
SecurityEvent
|where TimeGenerated > ago(30d)
|where EventID in (4624, 4625, 4648, 4672)
|summarize
    TotalEvents = count(),
    SuccessfulLogins = countif(EventID == 4624),
    FailedLogins = countif(EventID == 4625),
    PrivilegeUse = countif(EventID == 4672)
    by bin(TimeGenerated, 1d)
|extend ComplianceScore = (SuccessfulLogins * 1.0) / (SuccessfulLogins + FailedLogins) * 100
|project TimeGenerated, TotalEvents, ComplianceScore
```

## Troubleshooting and Maintenance

### Common Issues and Solutions

```kql
// Check data connector health
Heartbeat
|where TimeGenerated > ago(1h)
|summarize LastHeartbeat = max(TimeGenerated) by Computer
|where LastHeartbeat < ago(15m)
|project Computer, LastHeartbeat, Status = "Missing"

// Verify data ingestion
Usage
|where TimeGenerated > ago(1h)
|summarize IngestedMB = sum(Quantity) by DataType
|where IngestedMB == 0
|project DataType, Status = "No data ingested"

// Analytics rule performance
SecurityAlert
|where TimeGenerated > ago(24h)
|summarize AlertCount = count() by AlertName
|join kind=leftouter (
    SecurityIncident
|where TimeGenerated > ago(24h)
|summarize IncidentCount = count() by Title
) on $left.AlertName == $right.Title
|extend FalsePositiveRate = (AlertCount - IncidentCount) * 100.0 / AlertCount
|where FalsePositiveRate > 80
|project AlertName, AlertCount, IncidentCount, FalsePositiveRate
```

### Performance Monitoring

```kql
// Query performance analysis
LAQueryLogs
|where TimeGenerated > ago(24h)
|where ResponseCode == 200
|summarize
    AvgDuration = avg(DurationMs),
    MaxDuration = max(DurationMs),
    QueryCount = count()
    by bin(TimeGenerated, 1h)
|render timechart

// Resource utilization
Perf
|where TimeGenerated > ago(1h)
|where ObjectName == "Processor" and CounterName == "% Processor Time"
|summarize AvgCPU = avg(CounterValue) by Computer
|where AvgCPU > 80

// Storage utilization
Usage
|where TimeGenerated > ago(30d)
|summarize TotalGB = sum(Quantity) / 1000 by Solution
|sort by TotalGB desc
```

## Resources

- [Microsoft Sentinel Documentation](https://docs.microsoft.com/en-us/azure/sentinel/)

- [KQL Quick Reference](https://docs.microsoft.com/en-us/azure/data-explorer/kql-quick-reference)

- [Sentinel GitHub Repository](https://github.com/Azure/Azure-Sentinel)

- [Threat Hunting Queries](https://github.com/Azure/Azure-Sentinel/tree/master/Hunting%20Queries)

- [Logic Apps Connectors](https://docs.microsoft.com/en-us/azure/connectors/)

Source: https://1337skills.com/cheatsheets/microsoft-sentinel/
