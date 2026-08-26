# Elastic SIEM Cheatsheet intermediate

Elastic SIEM (Security Information and Event Management) is a comprehensive security analytics solution built on the Elastic Stack (Elasticsearch, Logstash, Kibana, and Beats). It provides real-time threat detection, investigation capabilities, and response orchestration for modern security operations centers. Elastic SIEM leverages machine learning, behavioral analytics, and threat intelligence to detect advanced persistent threats, insider threats, and sophisticated attack campaigns across hybrid cloud environments.

## Platform Overview

### Elastic Stack Architecture

Elastic SIEM is built on the foundation of the Elastic Stack, which provides a distributed, scalable platform for ingesting, storing, searching, and visualizing security data at massive scale. The architecture consists of several core components that work together to provide comprehensive security monitoring and analytics capabilities.

Elasticsearch serves as the distributed search and analytics engine that stores and indexes security data from across the enterprise. It provides real-time search capabilities, advanced aggregations, and machine learning features that enable rapid threat detection and investigation. The distributed nature of Elasticsearch allows organizations to scale their security data lake horizontally to accommodate growing data volumes and user demands.

Logstash acts as the data processing pipeline that ingests, transforms, and enriches security data from diverse sources before sending it to Elasticsearch. It supports hundreds of input plugins for collecting data from security tools, network devices, cloud platforms, and custom applications. Logstash can parse, normalize, and enrich data in real-time, adding context such as geolocation, threat intelligence, and asset information.

Kibana provides the user interface for security analysts to search, visualize, and analyze security data. It includes pre-built dashboards, detection rules, case management capabilities, and investigation workflows specifically designed for security operations. Kibana's visualization capabilities enable analysts to create custom dashboards, perform ad-hoc analysis, and generate executive reports.

Beats are lightweight data shippers that collect and forward data from endpoints, servers, and network devices to Logstash or Elasticsearch. Security-focused beats include Winlogbeat for Windows event logs, Auditbeat for system audit data, Packetbeat for network traffic analysis, and Filebeat for log file collection.

### Key Features

```bash
# Core SIEM Capabilities
- Real-time threat detection and alerting
- Advanced behavioral analytics and machine learning
- Threat hunting and investigation workflows
- Case management and incident response
- Timeline analysis and event correlation
- Threat intelligence integration
- Custom detection rule creation
- Executive dashboards and reporting
```

## Installation and Setup

### Elasticsearch Installation

```bash
# Download and install Elasticsearch
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0

# Configure Elasticsearch for SIEM
cat > config/elasticsearch.yml ``<< EOF
cluster.name: elastic-siem
node.name: siem-node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

# Security settings
xpack.security.enabled: true
xpack.security.enrollment.enabled: true
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: certs/http.p12
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: certs/transport.p12
xpack.security.transport.ssl.truststore.path: certs/transport.p12
EOF

# Start Elasticsearch
./bin/elasticsearch

# Set up passwords for built-in users
./bin/elasticsearch-setup-passwords auto

# Create SIEM-specific index templates
curl -X PUT "localhost:9200/_index_template/siem-logs" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\{
    "index_patterns": ["siem-*"],
    "template": \\\{
      "settings": \\\{
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "index.lifecycle.name": "siem-policy",
        "index.lifecycle.rollover_alias": "siem-logs"
      \\\},
      "mappings": \\\{
        "properties": \\\{
          "@timestamp": \\\{"type": "date"\\\},
          "event.category": \\\{"type": "keyword"\\\},
          "event.action": \\\{"type": "keyword"\\\},
          "source.ip": \\\{"type": "ip"\\\},
          "destination.ip": \\\{"type": "ip"\\\},
          "user.name": \\\{"type": "keyword"\\\},
          "host.name": \\\{"type": "keyword"\\\},
          "process.name": \\\{"type": "keyword"\\\},
          "file.hash.sha256": \\\{"type": "keyword"\\\}
        \\\}
      \\\}
    \\\}
  \\\}'
```

### Kibana Installation and Configuration

```bash
# Download and install Kibana
wget https://artifacts.elastic.co/downloads/kibana/kibana-8.11.0-linux-x86_64.tar.gz
tar -xzf kibana-8.11.0-linux-x86_64.tar.gz
cd kibana-8.11.0

# Configure Kibana for SIEM
cat >`` config/kibana.yml << EOF
server.port: 5601
server.host: "0.0.0.0"
server.name: "elastic-siem-kibana"
elasticsearch.hosts: ["https://localhost:9200"]
elasticsearch.username: "kibana_system"
elasticsearch.password: "kibana_password"
elasticsearch.ssl.certificateAuthorities: ["/path/to/elasticsearch/config/certs/http_ca.crt"]

# SIEM-specific settings
xpack.security.enabled: true
xpack.encryptedSavedObjects.encryptionKey: "a7a6311933d3503b89bc2dbc36572c33a6c10925682e591bffcab6911c06786d"
xpack.reporting.encryptionKey: "a7a6311933d3503b89bc2dbc36572c33a6c10925682e591bffcab6911c06786d"
xpack.security.encryptionKey: "a7a6311933d3503b89bc2dbc36572c33a6c10925682e591bffcab6911c06786d"

# Enable SIEM app
xpack.siem.enabled: true
xpack.securitySolution.enabled: true
EOF

# Start Kibana
./bin/kibana

# Access Kibana SIEM interface
# Navigate to http://localhost:5601/app/security
```

### Logstash Configuration for SIEM

```bash
# Install Logstash
wget https://artifacts.elastic.co/downloads/logstash/logstash-8.11.0-linux-x86_64.tar.gz
tar -xzf logstash-8.11.0-linux-x86_64.tar.gz
cd logstash-8.11.0

# Create SIEM pipeline configuration
cat > config/siem-pipeline.conf << 'EOF'
input \\\\{
  # Windows Event Logs via Winlogbeat
  beats \\\\{
    port => 5044
    type => "winlogbeat"
  \\\\}

  # Syslog from network devices
  syslog \\\\{
    port => 514
    type => "syslog"
  \\\\}

  # CEF logs from security tools
  tcp \\\\{
    port => 5140
    codec => cef
    type => "cef"
  \\\\}

  # File input for custom logs
  file \\\\{
    path => "/var/log/security/*.log"
    start_position => "beginning"
    type => "security_logs"
  \\\\}
\\\\}

filter \\\\{
  # Parse Windows Security Events
  if [type] == "winlogbeat" \\\\{
    if [winlog][event_id] == 4624 \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "authentication" \\\\}
        add_field => \\\\{ "event.action" => "logon" \\\\}
        add_field => \\\\{ "event.outcome" => "success" \\\\}
      \\\\}
    \\\\}

    if [winlog][event_id] == 4625 \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "authentication" \\\\}
        add_field => \\\\{ "event.action" => "logon" \\\\}
        add_field => \\\\{ "event.outcome" => "failure" \\\\}
      \\\\}
    \\\\}

    if [winlog][event_id] == 4688 \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "process" \\\\}
        add_field => \\\\{ "event.action" => "start" \\\\}
      \\\\}
    \\\\}
  \\\\}

  # Parse syslog messages
  if [type] == "syslog" \\\\{
    grok \\\\{
      match => \\\\{ "message" => "%\\\\{SYSLOGTIMESTAMP:timestamp\\\\} %\\\\{IPORHOST:host\\\\} %\\\\{WORD:program\\\\}(?:\[%\\\\{POSINT:pid\\\\}\])?: %\\\\{GREEDYDATA:message\\\\}" \\\\}
    \\\\}

    date \\\\{
      match => [ "timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    \\\\}
  \\\\}

  # Enrich with GeoIP data
  if [source][ip] \\\\{
    geoip \\\\{
      source => "[source][ip]"
      target => "[source][geo]"
    \\\\}
  \\\\}

  if [destination][ip] \\\\{
    geoip \\\\{
      source => "[destination][ip]"
      target => "[destination][geo]"
    \\\\}
  \\\\}

  # Add threat intelligence
  translate \\\\{
    field => "[source][ip]"
    destination => "[threat][indicator][type]"
    dictionary_path => "/etc/logstash/threat_intel.yml"
    fallback => "unknown"
  \\\\}

  # Normalize timestamps
  date \\\\{
    match => [ "@timestamp", "ISO8601" ]
  \\\\}
\\\\}

output \\\\{
  # Send to Elasticsearch
  elasticsearch \\\\{
    hosts => ["https://localhost:9200"]
    user => "logstash_writer"
    password => "logstash_password"
    ssl => true
    ssl_certificate_verification => false
    index => "siem-logs-%\\\\{+YYYY.MM.dd\\\\}"
    template_name => "siem-logs"
  \\\\}

  # Debug output
  stdout \\\\{
    codec => rubydebug
  \\\\}
\\\\}
EOF

# Start Logstash with SIEM pipeline
./bin/logstash -f config/siem-pipeline.conf
```

## Data Collection and Ingestion

### Beats Configuration for Security Data

```bash
# Winlogbeat for Windows Event Logs
cat > winlogbeat.yml << 'EOF'
winlogbeat.event_logs:
  - name: Security
    event_id: 4624, 4625, 4648, 4672, 4688, 4689, 4697, 4698, 4699, 4700, 4701, 4702
  - name: System
    event_id: 7034, 7035, 7036, 7040
  - name: Application
    event_id: 1000, 1001, 1002

output.elasticsearch:
  hosts: ["https://localhost:9200"]
  username: "winlogbeat_writer"
  password: "winlogbeat_password"
  ssl.certificate_authorities: ["/path/to/ca.crt"]
  index: "winlogbeat-%\\\\{+yyyy.MM.dd\\\\}"

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/winlogbeat
  name: winlogbeat
  keepfiles: 7
  permissions: 0644
EOF

# Auditbeat for system audit data
cat > auditbeat.yml << 'EOF'
auditbeat.modules:
- module: auditd
  audit_rule_files: [ '$\\\\{path.config\\\\}/audit.rules.d/*.conf' ]
  audit_rules:|
    # Monitor file access
    -w /etc/passwd -p wa -k identity
    -w /etc/group -p wa -k identity
    -w /etc/shadow -p wa -k identity

    # Monitor privilege escalation
    -a always,exit -F arch=b64 -S execve -F euid=0 -F auid>=1000 -F auid!=4294967295 -k privilege_escalation

    # Monitor network connections
    -a always,exit -F arch=b64 -S socket -F a0=2 -k network_connect

    # Monitor file modifications
    -w /bin/ -p wa -k binaries
    -w /sbin/ -p wa -k binaries
    -w /usr/bin/ -p wa -k binaries
    -w /usr/sbin/ -p wa -k binaries

- module: file_integrity
  paths:
  - /bin
  - /usr/bin
  - /sbin
  - /usr/sbin
  - /etc

- module: system
  datasets:
    - host
    - login
    - package
    - process
    - socket
    - user
  period: 10s

output.elasticsearch:
  hosts: ["https://localhost:9200"]
  username: "auditbeat_writer"
  password: "auditbeat_password"
  ssl.certificate_authorities: ["/path/to/ca.crt"]
  index: "auditbeat-%\\\\{+yyyy.MM.dd\\\\}"
EOF

# Packetbeat for network traffic analysis
cat > packetbeat.yml << 'EOF'
packetbeat.interfaces.device: any

packetbeat.flows:
  timeout: 30s
  period: 10s

packetbeat.protocols:
  dns:
    ports: [53]
    include_authorities: true
    include_additionals: true

  http:
    ports: [80, 8080, 8000, 5000, 8002]

  tls:
    ports: [443, 993, 995, 5223, 8443, 8883, 9243]

  ssh:
    ports: [22]

output.elasticsearch:
  hosts: ["https://localhost:9200"]
  username: "packetbeat_writer"
  password: "packetbeat_password"
  ssl.certificate_authorities: ["/path/to/ca.crt"]
  index: "packetbeat-%\\\\{+yyyy.MM.dd\\\\}"

processors:
  - add_host_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~
EOF
```

### Custom Log Parsing

```bash
# Create custom parsing rules for security tools
cat > /etc/logstash/conf.d/security-tools.conf << 'EOF'
filter \\\\{
  # Parse Suricata IDS logs
  if [type] == "suricata" \\\\{
    json \\\\{
      source => "message"
    \\\\}

    if [event_type] == "alert" \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "intrusion_detection" \\\\}
        add_field => \\\\{ "event.action" => "alert" \\\\}
        add_field => \\\\{ "rule.name" => "%\\\\{[alert][signature]\\\\}" \\\\}
        add_field => \\\\{ "rule.id" => "%\\\\{[alert][signature_id]\\\\}" \\\\}
      \\\\}
    \\\\}
  \\\\}

  # Parse Zeek/Bro logs
  if [type] == "zeek" \\\\{
    if [log_type] == "conn" \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "network" \\\\}
        add_field => \\\\{ "event.action" => "connection" \\\\}
      \\\\}
    \\\\}

    if [log_type] == "dns" \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "network" \\\\}
        add_field => \\\\{ "event.action" => "dns_query" \\\\}
      \\\\}
    \\\\}

    if [log_type] == "http" \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "network" \\\\}
        add_field => \\\\{ "event.action" => "http_request" \\\\}
      \\\\}
    \\\\}
  \\\\}

  # Parse OSSEC/Wazuh logs
  if [type] == "ossec" \\\\{
    grok \\\\{
      match => \\\\{ "message" => "%\\\\{TIMESTAMP_ISO8601:timestamp\\\\} %\\\\{WORD:hostname\\\\} %\\\\{WORD:component\\\\}: %\\\\{GREEDYDATA:alert_message\\\\}" \\\\}
    \\\\}

    if [rule_id] \\\\{
      mutate \\\\{
        add_field => \\\\{ "event.category" => "host" \\\\}
        add_field => \\\\{ "event.action" => "alert" \\\\}
        add_field => \\\\{ "rule.id" => "%\\\\{rule_id\\\\}" \\\\}
      \\\\}
    \\\\}
  \\\\}
\\\\}
EOF
```

## Detection Rules and Analytics

### Pre-built Detection Rules

```json
// Suspicious PowerShell Activity
\\\\{
  "rule": \\\\{
    "name": "Suspicious PowerShell Execution",
    "description": "Detects potentially malicious PowerShell commands",
    "severity": "high",
    "risk_score": 75,
    "query": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "event.category": "process"
            \\\\}
          \\\\},
          \\\\{
            "term": \\\\{
              "process.name": "powershell.exe"
            \\\\}
          \\\\},
          \\\\{
            "bool": \\\\{
              "should": [
                \\\\{
                  "wildcard": \\\\{
                    "process.command_line": "*Invoke-Expression*"
                  \\\\}
                \\\\},
                \\\\{
                  "wildcard": \\\\{
                    "process.command_line": "*DownloadString*"
                  \\\\}
                \\\\},
                \\\\{
                  "wildcard": \\\\{
                    "process.command_line": "*EncodedCommand*"
                  \\\\}
                \\\\},
                \\\\{
                  "wildcard": \\\\{
                    "process.command_line": "*-nop*"
                  \\\\}
                \\\\},
                \\\\{
                  "wildcard": \\\\{
                    "process.command_line": "*-w hidden*"
                  \\\\}
                \\\\}
              ]
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\},
    "filters": [],
    "timeline_id": "timeline_powershell",
    "timeline_title": "PowerShell Investigation Timeline"
  \\\\}
\\\\}

// Brute Force Login Attempts
\\\\{
  "rule": \\\\{
    "name": "Brute Force Login Attempts",
    "description": "Detects multiple failed login attempts from the same source",
    "severity": "medium",
    "risk_score": 50,
    "query": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "event.category": "authentication"
            \\\\}
          \\\\},
          \\\\{
            "term": \\\\{
              "event.outcome": "failure"
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\},
    "threshold": \\\\{
      "field": "source.ip",
      "value": 10,
      "cardinality": [
        \\\\{
          "field": "user.name",
          "value": 5
        \\\\}
      ]
    \\\\},
    "timeline_id": "timeline_brute_force",
    "timeline_title": "Brute Force Investigation Timeline"
  \\\\}
\\\\}

// Lateral Movement Detection
\\\\{
  "rule": \\\\{
    "name": "Lateral Movement via Remote Services",
    "description": "Detects potential lateral movement using remote services",
    "severity": "high",
    "risk_score": 80,
    "query": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "event.category": "authentication"
            \\\\}
          \\\\},
          \\\\{
            "term": \\\\{
              "event.outcome": "success"
            \\\\}
          \\\\},
          \\\\{
            "terms": \\\\{
              "winlog.logon.type": ["3", "10"]
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\},
    "threshold": \\\\{
      "field": "user.name",
      "value": 1,
      "cardinality": [
        \\\\{
          "field": "host.name",
          "value": 5
        \\\\}
      ]
    \\\\}
  \\\\}
\\\\}
```

### Machine Learning Jobs

```json
// Anomalous Network Traffic
\\\\{
  "job_id": "anomalous_network_traffic",
  "description": "Detects anomalous network traffic patterns",
  "analysis_config": \\\\{
    "bucket_span": "15m",
    "detectors": [
      \\\\{
        "function": "high_count",
        "field_name": "network.bytes",
        "by_field_name": "source.ip"
      \\\\},
      \\\\{
        "function": "rare",
        "field_name": "destination.port",
        "by_field_name": "source.ip"
      \\\\}
    ],
    "influencers": ["source.ip", "destination.ip", "destination.port"]
  \\\\},
  "data_description": \\\\{
    "time_field": "@timestamp",
    "time_format": "epoch_ms"
  \\\\},
  "datafeed_config": \\\\{
    "indices": ["packetbeat-*"],
    "query": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "event.category": "network"
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\}
  \\\\}
\\\\}

// Unusual Process Execution
\\\\{
  "job_id": "unusual_process_execution",
  "description": "Detects unusual process execution patterns",
  "analysis_config": \\\\{
    "bucket_span": "15m",
    "detectors": [
      \\\\{
        "function": "rare",
        "field_name": "process.name",
        "by_field_name": "host.name"
      \\\\},
      \\\\{
        "function": "freq_rare",
        "field_name": "process.command_line",
        "by_field_name": "user.name"
      \\\\}
    ],
    "influencers": ["host.name", "user.name", "process.name"]
  \\\\},
  "data_description": \\\\{
    "time_field": "@timestamp",
    "time_format": "epoch_ms"
  \\\\},
  "datafeed_config": \\\\{
    "indices": ["winlogbeat-*", "auditbeat-*"],
    "query": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "event.category": "process"
            \\\\}
          \\\\},
          \\\\{
            "term": \\\\{
              "event.action": "start"
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\}
  \\\\}
\\\\}
```

### Custom Detection Rules

```bash
# Create custom detection rule via API
curl -X POST "localhost:5601/api/detection_engine/rules" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "name": "Credential Dumping Activity",
    "description": "Detects potential credential dumping tools and techniques",
    "severity": "critical",
    "risk_score": 90,
    "rule_id": "credential-dumping-001",
    "type": "query",
    "query": "event.category:process AND (process.name:(mimikatz.exe OR procdump.exe OR pwdump.exe OR fgdump.exe) OR process.command_line:(*sekurlsa* OR *logonpasswords* OR *lsadump* OR *sam* OR *security*))",
    "language": "kuery",
    "filters": [],
    "from": "now-6m",
    "to": "now",
    "interval": "5m",
    "enabled": true,
    "tags": ["credential_access", "T1003"],
    "threat": [
      \\\\{
        "framework": "MITRE ATT&CK",
        "tactic": \\\\{
          "id": "TA0006",
          "name": "Credential Access",
          "reference": "https://attack.mitre.org/tactics/TA0006/"
        \\\\},
        "technique": [
          \\\\{
            "id": "T1003",
            "name": "OS Credential Dumping",
            "reference": "https://attack.mitre.org/techniques/T1003/"
          \\\\}
        ]
      \\\\}
    ]
  \\\\}'

# Create threshold-based rule
curl -X POST "localhost:5601/api/detection_engine/rules" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "name": "Multiple Failed SSH Logins",
    "description": "Detects multiple failed SSH login attempts",
    "severity": "medium",
    "risk_score": 60,
    "rule_id": "ssh-brute-force-001",
    "type": "threshold",
    "query": "event.category:authentication AND event.outcome:failure AND service.name:ssh",
    "language": "kuery",
    "threshold": \\\\{
      "field": "source.ip",
      "value": 20,
      "cardinality": [
        \\\\{
          "field": "user.name",
          "value": 5
        \\\\}
      ]
    \\\\},
    "from": "now-5m",
    "to": "now",
    "interval": "5m",
    "enabled": true,
    "tags": ["initial_access", "T1078"]
  \\\\}'
```

## Investigation and Threat Hunting

### Timeline Analysis

```bash
# Create investigation timeline
curl -X POST "localhost:5601/api/timeline" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "timeline": \\\\{
      "title": "Incident Investigation Timeline",
      "description": "Timeline for investigating security incident",
      "timelineType": "default",
      "templateTimelineId": null,
      "templateTimelineVersion": null,
      "dataProviders": [
        \\\\{
          "id": "host-investigation",
          "name": "Host Investigation",
          "enabled": true,
          "excluded": false,
          "kqlQuery": "",
          "queryMatch": \\\\{
            "field": "host.name",
            "value": "suspicious-host",
            "operator": ":"
          \\\\}
        \\\\}
      ],
      "kqlQuery": \\\\{
        "filterQuery": \\\\{
          "kuery": \\\\{
            "kind": "kuery",
            "expression": "host.name: suspicious-host"
          \\\\}
        \\\\}
      \\\\},
      "dateRange": \\\\{
        "start": "2023-01-01T00:00:00.000Z",
        "end": "2023-01-02T00:00:00.000Z"
      \\\\}
    \\\\}
  \\\\}'

# Query timeline events
curl -X POST "localhost:5601/api/timeline/_search" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "defaultIndex": ["winlogbeat-*", "auditbeat-*", "packetbeat-*"],
    "timerange": \\\\{
      "from": "2023-01-01T00:00:00.000Z",
      "to": "2023-01-02T00:00:00.000Z",
      "interval": "12h"
    \\\\},
    "filterQuery": \\\\{
      "bool": \\\\{
        "must": [
          \\\\{
            "term": \\\\{
              "host.name": "suspicious-host"
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\},
    "pagination": \\\\{
      "activePage": 0,
      "querySize": 25
    \\\\},
    "sort": \\\\{
      "columnId": "@timestamp",
      "sortDirection": "desc"
    \\\\}
  \\\\}'
```

### Threat Hunting Queries

```bash
# Hunt for living off the land techniques
GET /winlogbeat-*/_search
\\\\{
  "query": \\\\{
    "bool": \\\\{
      "must": [
        \\\\{
          "term": \\\\{
            "event.category": "process"
          \\\\}
        \\\\},
        \\\\{
          "terms": \\\\{
            "process.name": [
              "certutil.exe",
              "bitsadmin.exe",
              "regsvr32.exe",
              "rundll32.exe",
              "mshta.exe",
              "wmic.exe"
            ]
          \\\\}
        \\\\},
        \\\\{
          "bool": \\\\{
            "should": [
              \\\\{
                "wildcard": \\\\{
                  "process.command_line": "*http*"
                \\\\}
              \\\\},
              \\\\{
                "wildcard": \\\\{
                  "process.command_line": "*download*"
                \\\\}
              \\\\},
              \\\\{
                "wildcard": \\\\{
                  "process.command_line": "*urlcache*"
                \\\\}
              \\\\}
            ]
          \\\\}
        \\\\}
      ]
    \\\\}
  \\\\},
  "aggs": \\\\{
    "by_host": \\\\{
      "terms": \\\\{
        "field": "host.name",
        "size": 10
      \\\\},
      "aggs": \\\\{
        "by_process": \\\\{
          "terms": \\\\{
            "field": "process.name",
            "size": 10
          \\\\}
        \\\\}
      \\\\}
    \\\\}
  \\\\}
\\\\}

# Hunt for persistence mechanisms
GET /winlogbeat-*/_search
\\\\{
  "query": \\\\{
    "bool": \\\\{
      "should": [
        \\\\{
          "bool": \\\\{
            "must": [
              \\\\{
                "term": \\\\{
                  "winlog.event_id": 4698
                \\\\}
              \\\\},
              \\\\{
                "wildcard": \\\\{
                  "winlog.event_data.TaskName": "*Microsoft*"
                \\\\}
              \\\\}
            ]
          \\\\}
        \\\\},
        \\\\{
          "bool": \\\\{
            "must": [
              \\\\{
                "term": \\\\{
                  "event.category": "registry"
                \\\\}
              \\\\},
              \\\\{
                "terms": \\\\{
                  "registry.path": [
                    "*\\Software\\Microsoft\\Windows\\CurrentVersion\\Run*",
                    "*\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce*",
                    "*\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon*"
                  ]
                \\\\}
              \\\\}
            ]
          \\\\}
        \\\\},
        \\\\{
          "bool": \\\\{
            "must": [
              \\\\{
                "term": \\\\{
                  "event.category": "file"
                \\\\}
              \\\\},
              \\\\{
                "terms": \\\\{
                  "file.path": [
                    "*\\Startup\\*",
                    "*\\Start Menu\\Programs\\Startup\\*"
                  ]
                \\\\}
              \\\\}
            ]
          \\\\}
        \\\\}
      ]
    \\\\}
  \\\\}
\\\\}

# Hunt for data exfiltration
GET /packetbeat-*/_search
\\\\{
  "query": \\\\{
    "bool": \\\\{
      "must": [
        \\\\{
          "range": \\\\{
            "@timestamp": \\\\{
              "gte": "now-24h"
            \\\\}
          \\\\}
        \\\\},
        \\\\{
          "term": \\\\{
            "network.direction": "outbound"
          \\\\}
        \\\\}
      ]
    \\\\}
  \\\\},
  "aggs": \\\\{
    "large_transfers": \\\\{
      "filter": \\\\{
        "range": \\\\{
          "network.bytes": \\\\{
            "gte": 100000000
          \\\\}
        \\\\}
      \\\\},
      "aggs": \\\\{
        "by_source": \\\\{
          "terms": \\\\{
            "field": "source.ip",
            "size": 10
          \\\\},
          "aggs": \\\\{
            "total_bytes": \\\\{
              "sum": \\\\{
                "field": "network.bytes"
              \\\\}
            \\\\},
            "destinations": \\\\{
              "terms": \\\\{
                "field": "destination.ip",
                "size": 5
              \\\\}
            \\\\}
          \\\\}
        \\\\}
      \\\\}
    \\\\}
  \\\\}
\\\\}
```

### Case Management

```bash
# Create security case
curl -X POST "localhost:5601/api/cases" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "title": "Suspicious PowerShell Activity Investigation",
    "description": "Investigation of suspicious PowerShell commands detected on multiple hosts",
    "tags": ["powershell", "malware", "investigation"],
    "severity": "high",
    "assignees": [
      \\\\{
        "uid": "analyst1"
      \\\\}
    ],
    "connector": \\\\{
      "id": "none",
      "name": "none",
      "type": ".none",
      "fields": null
    \\\\},
    "settings": \\\\{
      "syncAlerts": true
    \\\\}
  \\\\}'

# Add comment to case
curl -X POST "localhost:5601/api/cases/\\\\{case_id\\\\}/comments" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "comment": "Initial analysis shows PowerShell commands attempting to download and execute malicious payloads. Affected hosts: HOST-001, HOST-002, HOST-003",
    "type": "user"
  \\\\}'

# Attach alert to case
curl -X POST "localhost:5601/api/cases/\\\\{case_id\\\\}/comments" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "alertId": "alert-id-123",
    "index": "winlogbeat-2023.01.01",
    "type": "alert"
  \\\\}'
```

## Dashboards and Visualization

### Security Overview Dashboard

```json
\\\\{
  "dashboard": \\\\{
    "title": "Security Operations Center Overview",
    "description": "High-level security metrics and alerts",
    "panelsJSON": "[\\\\{\"version\":\"8.11.0\",\"gridData\":\\\\{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"1\"\\\\},\"panelIndex\":\"1\",\"embeddableConfig\":\\\\{\\\\},\"panelRefName\":\"panel_1\"\\\\}]",
    "optionsJSON": "\\\\{\"useMargins\":true,\"syncColors\":false,\"hidePanelTitles\":false\\\\}",
    "version": 1,
    "timeRestore": true,
    "timeTo": "now",
    "timeFrom": "now-24h",
    "refreshInterval": \\\\{
      "pause": false,
      "value": 300000
    \\\\},
    "kibanaSavedObjectMeta": \\\\{
      "searchSourceJSON": "\\\\{\"query\":\\\\{\"query\":\"\",\"language\":\"kuery\"\\\\},\"filter\":[]\\\\}"
    \\\\}
  \\\\},
  "references": [
    \\\\{
      "name": "panel_1",
      "type": "visualization",
      "id": "security-alerts-timeline"
    \\\\}
  ]
\\\\}
```

### Threat Hunting Dashboard

```bash
# Create threat hunting visualizations
curl -X POST "localhost:5601/api/saved_objects/visualization" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "attributes": \\\\{
      "title": "Process Execution Timeline",
      "visState": "\\\\{\"title\":\"Process Execution Timeline\",\"type\":\"histogram\",\"params\":\\\\{\"grid\":\\\\{\"categoryLines\":false,\"style\":\\\\{\"color\":\"#eee\"\\\\}\\\\},\"categoryAxes\":[\\\\{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"bottom\",\"show\":true,\"style\":\\\\{\\\\},\"scale\":\\\\{\"type\":\"linear\"\\\\},\"labels\":\\\\{\"show\":true,\"truncate\":100\\\\},\"title\":\\\\{\\\\}\\\\}],\"valueAxes\":[\\\\{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"left\",\"show\":true,\"style\":\\\\{\\\\},\"scale\":\\\\{\"type\":\"linear\",\"mode\":\"normal\"\\\\},\"labels\":\\\\{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":100\\\\},\"title\":\\\\{\"text\":\"Count\"\\\\}\\\\}],\"seriesParams\":[\\\\{\"show\":true,\"type\":\"histogram\",\"mode\":\"stacked\",\"data\":\\\\{\"label\":\"Count\",\"id\":\"1\"\\\\},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true\\\\}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false\\\\},\"aggs\":[\\\\{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":\\\\{\\\\}\\\\},\\\\{\"id\":\"2\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":\\\\{\"field\":\"@timestamp\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":\\\\{\\\\}\\\\}\\\\},\\\\{\"id\":\"3\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"group\",\"params\":\\\\{\"field\":\"process.name\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\"\\\\}\\\\}]\\\\}",
      "uiStateJSON": "\\\\{\\\\}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": \\\\{
        "searchSourceJSON": "\\\\{\"index\":\"winlogbeat-*\",\"query\":\\\\{\"match\":\\\\{\"event.category\":\"process\"\\\\}\\\\},\"filter\":[]\\\\}"
      \\\\}
    \\\\}
  \\\\}'

# Network traffic analysis visualization
curl -X POST "localhost:5601/api/saved_objects/visualization" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -u elastic:password \
  -d '\\\\{
    "attributes": \\\\{
      "title": "Network Traffic by Destination Port",
      "visState": "\\\\{\"title\":\"Network Traffic by Destination Port\",\"type\":\"pie\",\"params\":\\\\{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":true\\\\},\"aggs\":[\\\\{\"id\":\"1\",\"enabled\":true,\"type\":\"sum\",\"schema\":\"metric\",\"params\":\\\\{\"field\":\"network.bytes\"\\\\}\\\\},\\\\{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":\\\\{\"field\":\"destination.port\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\"\\\\}\\\\}]\\\\}",
      "uiStateJSON": "\\\\{\\\\}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": \\\\{
        "searchSourceJSON": "\\\\{\"index\":\"packetbeat-*\",\"query\":\\\\{\"match_all\":\\\\{\\\\}\\\\},\"filter\":[]\\\\}"
      \\\\}
    \\\\}
  \\\\}'
```

## Performance Optimization

### Index Management

```bash
# Create index lifecycle policy
curl -X PUT "localhost:9200/_ilm/policy/siem-policy" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\\{
    "policy": \\\\{
      "phases": \\\\{
        "hot": \\\\{
          "actions": \\\\{
            "rollover": \\\\{
              "max_size": "10GB",
              "max_age": "1d"
            \\\\},
            "set_priority": \\\\{
              "priority": 100
            \\\\}
          \\\\}
        \\\\},
        "warm": \\\\{
          "min_age": "7d",
          "actions": \\\\{
            "set_priority": \\\\{
              "priority": 50
            \\\\},
            "allocate": \\\\{
              "number_of_replicas": 0
            \\\\},
            "forcemerge": \\\\{
              "max_num_segments": 1
            \\\\}
          \\\\}
        \\\\},
        "cold": \\\\{
          "min_age": "30d",
          "actions": \\\\{
            "set_priority": \\\\{
              "priority": 0
            \\\\},
            "allocate": \\\\{
              "number_of_replicas": 0
            \\\\}
          \\\\}
        \\\\},
        "delete": \\\\{
          "min_age": "90d",
          "actions": \\\\{
            "delete": \\\\{\\\\}
          \\\\}
        \\\\}
      \\\\}
    \\\\}
  \\\\}'

# Optimize search performance
curl -X PUT "localhost:9200/siem-logs-*/_settings" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\\{
    "index": \\\\{
      "refresh_interval": "30s",
      "number_of_replicas": 1,
      "codec": "best_compression"
    \\\\}
  \\\\}'

# Create search templates for common queries
curl -X PUT "localhost:9200/_scripts/security-event-search" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\\{
    "script": \\\\{
      "lang": "mustache",
      "source": \\\\{
        "query": \\\\{
          "bool": \\\\{
            "must": [
              \\\\{
                "range": \\\\{
                  "@timestamp": \\\\{
                    "gte": "\\\\{\\\\{from\\\\}\\\\}",
                    "lte": "\\\\{\\\\{to\\\\}\\\\}"
                  \\\\}
                \\\\}
              \\\\},
              \\\\{
                "term": \\\\{
                  "event.category": "\\\\{\\\\{category\\\\}\\\\}"
                \\\\}
              \\\\}
            ],
            "filter": [
              \\\\{\\\\{#host\\\\}\\\\}
              \\\\{
                "term": \\\\{
                  "host.name": "\\\\{\\\\{host\\\\}\\\\}"
                \\\\}
              \\\\}
              \\\\{\\\\{/host\\\\}\\\\}
            ]
          \\\\}
        \\\\},
        "sort": [
          \\\\{
            "@timestamp": \\\\{
              "order": "desc"
            \\\\}
          \\\\}
        ]
      \\\\}
    \\\\}
  \\\\}'
```

### Monitoring and Alerting

```bash
# Monitor cluster health
curl -X GET "localhost:9200/_cluster/health?pretty" -u elastic:password

# Monitor index statistics
curl -X GET "localhost:9200/_cat/indices/siem-*?v&s=store.size:desc" -u elastic:password

# Set up cluster monitoring
curl -X PUT "localhost:9200/_cluster/settings" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\\{
    "persistent": \\\\{
      "cluster.routing.allocation.disk.watermark.low": "85%",
      "cluster.routing.allocation.disk.watermark.high": "90%",
      "cluster.routing.allocation.disk.watermark.flood_stage": "95%"
    \\\\}
  \\\\}'

# Create watcher for disk space monitoring
curl -X PUT "localhost:9200/_watcher/watch/disk_space_monitor" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '\\\\{
    "trigger": \\\\{
      "schedule": \\\\{
        "interval": "5m"
      \\\\}
    \\\\},
    "input": \\\\{
      "http": \\\\{
        "request": \\\\{
          "host": "localhost",
          "port": 9200,
          "path": "/_nodes/stats/fs",
          "auth": \\\\{
            "basic": \\\\{
              "username": "elastic",
              "password": "password"
            \\\\}
          \\\\}
        \\\\}
      \\\\}
    \\\\},
    "condition": \\\\{
      "script": \\\\{
        "source": "ctx.payload.nodes.values().stream().anyMatch(node -> node.fs.total.available_in_bytes / node.fs.total.total_in_bytes < 0.1)"
      \\\\}
    \\\\},
    "actions": \\\\{
      "send_email": \\\\{
        "email": \\\\{
          "to": ["admin@company.com"],
          "subject": "Elasticsearch Disk Space Alert",
          "body": "Disk space is running low on Elasticsearch cluster"
        \\\\}
      \\\\}
    \\\\}
  \\\\}'
```

## Resources

- [Elastic Security Documentation](https://www.elastic.co/guide/en/security/current/index.html)

- [Elasticsearch Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/index.html)

- [Elastic SIEM GitHub Repository](https://github.com/elastic/detection-rules)

- [Elastic Community](https://discuss.elastic.co/)

Source: https://1337skills.com/cheatsheets/elastic-siem/
