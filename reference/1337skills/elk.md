# ELK Stack advanced

The ELK Stack (Elasticsearch, Logstash, Kibana) is a powerful open-source platform for searching, analyzing, and visualizing log data in real-time. This guide covers installation, configuration, queries, dashboards, and operational tasks.

## Installation

### Docker Compose (Recommended for Development)

```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elastic-data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    environment:
      - "xpack.monitoring.enabled=false"

volumes:
  elastic-data:

# Start services
docker-compose up -d
```

### Linux/Ubuntu Manual Installation

```bash
# Import Elastic GPG key
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -

# Add Elastic repository
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | \
  tee /etc/apt/sources.list.d/elastic-8.x.list

# Update and install
sudo apt-get update
sudo apt-get install elasticsearch kibana logstash

# Start services
sudo systemctl start elasticsearch
sudo systemctl start kibana
sudo systemctl start logstash
```

## Elasticsearch

### Basic Operations

```bash
# Check cluster health
curl -X GET "localhost:9200/_cluster/health"

# Get cluster info
curl -X GET "localhost:9200/_info"

# List indices
curl -X GET "localhost:9200/_cat/indices"

# Get index mappings
curl -X GET "localhost:9200/my-index/_mapping"

# Get index settings
curl -X GET "localhost:9200/my-index/_settings"
```

### Creating Indices

```bash
# Create index with custom settings
curl -X PUT "localhost:9200/my-logs" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" },
      "host": { "type": "keyword" },
      "source": { "type": "keyword" }
    }
  }
}'

# Delete index
curl -X DELETE "localhost:9200/my-logs"

# Reindex from one index to another
curl -X POST "localhost:9200/_reindex" -d'
{
  "source": { "index": "old-index" },
  "dest": { "index": "new-index" }
}'
```

### Indexing Documents

```bash
# Index a document
curl -X POST "localhost:9200/my-logs/_doc" -H 'Content-Type: application/json' -d'
{
  "timestamp": "2025-03-30T10:30:00Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "host": "server-01",
  "source": "database.py"
}'

# Bulk indexing
curl -X POST "localhost:9200/_bulk" -H 'Content-Type: application/json' -d'
{ "index": { "_index": "my-logs" } }
{ "timestamp": "2025-03-30T10:30:00Z", "level": "INFO", "message": "App started" }
{ "index": { "_index": "my-logs" } }
{ "timestamp": "2025-03-30T10:31:00Z", "level": "ERROR", "message": "Error occurred" }
'
```

### Querying

```bash
# Basic match query
curl -X GET "localhost:9200/my-logs/_search" -d'
{
  "query": {
    "match": {
      "message": "database"
    }
  }
}'

# Range query
curl -X GET "localhost:9200/my-logs/_search" -d'
{
  "query": {
    "range": {
      "timestamp": {
        "gte": "2025-03-30T10:00:00Z",
        "lte": "2025-03-30T11:00:00Z"
      }
    }
  }
}'

# Boolean query (AND/OR/NOT)
curl -X GET "localhost:9200/my-logs/_search" -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } }
      ],
      "filter": [
        { "term": { "host": "server-01" } }
      ]
    }
  }
}'

# Full-text search
curl -X GET "localhost:9200/my-logs/_search" -d'
{
  "query": {
    "multi_match": {
      "query": "connection error",
      "fields": ["message", "level"]
    }
  }
}'

# Aggregation (statistics)
curl -X GET "localhost:9200/my-logs/_search" -d'
{
  "size": 0,
  "aggs": {
    "log_levels": {
      "terms": {
        "field": "level",
        "size": 10
      }
    }
  }
}'
```

## Logstash

### Basic Configuration

```ini
# logstash.conf
input {
  file {
    path => "/var/log/syslog"
    start_position => "beginning"
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
    }
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} \[%{DATA:service}\] %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }

  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }

  stdout {
    codec => rubydebug
  }
}
```

### Testing Configuration

```bash
# Test logstash config syntax
logstash -f logstash.conf --config.test_and_exit

# Run with verbose output
logstash -f logstash.conf --debug

# Run specific pipeline
logstash -f config/ --pipeline.id main
```

### Input Plugins

```ini
# File input
input {
  file {
    path => "/var/log/*.log"
    start_position => "beginning"
  }
}

# Syslog input
input {
  syslog {
    port => 514
    type => "syslog"
  }
}

# HTTP input
input {
  http {
    host => "0.0.0.0"
    port => 8080
  }
}

# TCP input
input {
  tcp {
    port => 5000
    codec => json
  }
}

# Beats input (Filebeat)
input {
  beats {
    port => 5044
  }
}
```

### Filter Plugins

```ini
# Grok pattern matching
filter {
  grok {
    match => { "message" => "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes}" }
  }
}

# Mutate filter
filter {
  mutate {
    add_field => { "[@metadata][index_type]" => "logs" }
    remove_field => [ "host", "path" ]
    rename => { "message" => "log_message" }
  }
}

# Date filter
filter {
  date {
    match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
    target => "@timestamp"
  }
}

# JSON filter
filter {
  json {
    source => "message"
    target => "parsed"
  }
}
```

### Output Plugins

```ini
# Elasticsearch output
output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "my-app-%{+YYYY.MM.dd}"
    user => "elastic"
    password => "changeme"
  }
}

# Stdout output (debugging)
output {
  stdout {
    codec => rubydebug
  }
}

# File output
output {
  file {
    path => "/var/log/processed-%{host}.log"
  }
}
```

## Kibana

### Access Kibana

```plaintext
http://localhost:5601
```

### Creating Dashboards

1. Go to Analytics > Dashboards

1. Click Create Dashboard

1. Add panels:

  - Visualization (charts, maps)

  - Metric

  - Table

1. Save dashboard

### Creating Visualizations

```javascript
// Example: Count of log levels over time
{
  "aggs": [
    {
      "type": "date_histogram",
      "params": {
        "field": "@timestamp",
        "interval": "1h"
      }
    },
    {
      "type": "terms",
      "params": {
        "field": "level",
        "size": 10
      }
    }
  ]
}
```

### Creating Alerts

1. Navigate to Stack Management > Alerting

1. Create Rule

1. Define trigger condition

1. Set notification action

1. Configure recipient

### Discovery

```plaintext
Kibana > Discover

Filter examples:
- level : "ERROR"
- timestamp : "last 24h"
- host : "server-01" OR host : "server-02"
```

## Common Use Cases

### Monitor Application Logs

```ini
input {
  file {
    path => "/var/log/app/*.log"
    tags => ["app"]
  }
}

filter {
  json { source => "message" }
}

output {
  elasticsearch {
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

### Parse Nginx Logs

```ini
input {
  file {
    path => "/var/log/nginx/access.log"
  }
}

filter {
  grok {
    match => { "message" => "%{NGINXACCESS}" }
  }
  geoip {
    source => "clientip"
  }
}

output {
  elasticsearch {
    index => "nginx-%{+YYYY.MM.dd}"
  }
}
```

### Monitor System Metrics

```ini
input {
  beats {
    port => 5044
  }
}

filter {
  if [metricset.name] == "cpu" {
    # CPU metrics processing
  }
  else if [metricset.name] == "memory" {
    # Memory metrics processing
  }
}

output {
  elasticsearch {
    index => "metrics-%{[metricset.name]}-%{+YYYY.MM.dd}"
  }
}
```

## Performance Tuning

### Elasticsearch

```bash
# Increase heap size (in elasticsearch.yml)
-Xms4g
-Xmx4g

# Adjust shard allocation
curl -X PUT "localhost:9200/_cluster/settings" -d'
{
  "transient": {
    "cluster.routing.allocation.node_initial_primaries_recoveries": 8
  }
}'
```

### Logstash

```ini
# Optimize worker threads
pipeline.workers: 4
pipeline.batch.size: 125
pipeline.batch.delay: 50
```

## Maintenance

```bash
# Backup indices
curl -X POST "localhost:9200/_snapshot" -d'
{
  "type": "fs",
  "settings": {
    "location": "/mnt/backup"
  }
}'

# Delete old indices (daily cleanup)
curl -X DELETE "localhost:9200/logs-$(date -d '30 days ago' +%Y.%m.%d)"

# Optimize indices
curl -X POST "localhost:9200/my-logs/_forcemerge"
```

## Troubleshooting

### Check Node Status

```bash
curl -X GET "localhost:9200/_nodes/stats"

# Check memory usage
curl -X GET "localhost:9200/_nodes/stats/jvm"
```

### Fix Shard Issues

```bash
# Allocate unassigned shards
curl -X POST "localhost:9200/_cluster/reroute" -d'
{
  "commands": [
    {
      "allocate": {
        "index": "my-index",
        "shard": 0,
        "node": "node-name",
        "allow_primary": true
      }
    }
  ]
}'
```

## Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/)

- [Logstash Guide](https://www.elastic.co/guide/en/logstash/)

- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/)

- [Elastic Community](https://discuss.elastic.co/)

---

_Last updated: 2025-03-30_

Source: https://1337skills.com/cheatsheets/elk/
