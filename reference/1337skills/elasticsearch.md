# Elasticsearch Commands intermediate

Elasticsearch is a distributed search and analytics engine built on Apache Lucene.

## Installation

### Docker (Recommended)

```bash
# Run Elasticsearch single node
docker run -d --name elasticsearch \
  -e discovery.type=single-node \
  -p 9200:9200 \
  -p 9300:9300 \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0

# Run with docker-compose
docker-compose up
```

### Linux/macOS

```bash
# Download and extract
curl -L https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.0.0-linux-x86_64.tar.gz | tar xz
cd elasticsearch-8.0.0
./bin/elasticsearch
```

### Verify Installation

```bash
curl http://localhost:9200/
```

## Basic API Calls

| Command | Description |
| --- | --- |
| `curl http://localhost:9200/` | Check cluster health |
| `curl http://localhost:9200/_cat/indices` | List indices |
| `curl http://localhost:9200/_cat/nodes` | List nodes |
| `curl http://localhost:9200/_cat/shards` | Show shard allocation |

## Index Management

```bash
# Create index
curl -X PUT "http://localhost:9200/my-index" -H "Content-Type: application/json" -d '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "status": { "type": "keyword" },
      "published": { "type": "date" }
    }
  }
}'

# List all indices
curl http://localhost:9200/_cat/indices?v

# Get index mapping
curl http://localhost:9200/my-index/_mapping

# Delete index
curl -X DELETE "http://localhost:9200/my-index"

# Reindex data
curl -X POST "http://localhost:9200/_reindex" -H "Content-Type: application/json" -d '{
  "source": { "index": "old-index" },
  "dest": { "index": "new-index" }
}'

# Close index
curl -X POST "http://localhost:9200/my-index/_close"

# Open index
curl -X POST "http://localhost:9200/my-index/_open"
```

## Indexing Documents

```bash
# Index single document with auto ID
curl -X POST "http://localhost:9200/posts/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Post",
    "content": "Post content",
    "author": "John",
    "published": "2026-01-15"
  }'

# Index with specific ID
curl -X PUT "http://localhost:9200/posts/_doc/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "First Post",
    "content": "Content here"
  }'

# Bulk indexing
curl -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/json" \
  -d '{
{ "index": { "_index": "posts", "_id": "1" } }
{ "title": "Post 1", "author": "John" }
{ "index": { "_index": "posts", "_id": "2" } }
{ "title": "Post 2", "author": "Jane" }
}'

# Update document
curl -X POST "http://localhost:9200/posts/_doc/1/_update" \
  -H "Content-Type: application/json" \
  -d '{
    "doc": {
      "status": "published"
    }
  }'

# Delete document
curl -X DELETE "http://localhost:9200/posts/_doc/1"
```

## Search Queries

### Basic Search

```bash
# Simple match query
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  }'

# Match all
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match_all": {}
    }
  }'
```

### Bool Query

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          { "match": { "title": "elasticsearch" } }
        ],
        "filter": [
          { "term": { "status": "published" } }
        ],
        "should": [
          { "term": { "featured": true } }
        ],
        "minimum_should_match": 0
      }
    }
  }'
```

### Range Query

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "range": {
        "published": {
          "gte": "2026-01-01",
          "lte": "2026-12-31"
        }
      }
    }
  }'
```

### Full-Text Search

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "multi_match": {
        "query": "elasticsearch tutorial",
        "fields": ["title^2", "content"]
      }
    }
  }'
```

## Aggregations

```bash
# Count documents by status
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 0,
    "aggs": {
      "status_counts": {
        "terms": {
          "field": "status"
        }
      }
    }
  }'

# Average score
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "aggs": {
      "avg_score": {
        "avg": {
          "field": "score"
        }
      }
    }
  }'

# Date histogram
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "aggs": {
      "posts_per_month": {
        "date_histogram": {
          "field": "published",
          "calendar_interval": "month"
        }
      }
    }
  }'
```

## Filters and Pagination

```bash
# With pagination
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "from": 10,
    "size": 20,
    "query": {
      "match_all": {}
    }
  }'

# With sorting
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": { "match_all": {} },
    "sort": [
      { "published": { "order": "desc" } },
      "_score"
    ]
  }'

# Highlighting
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": { "match": { "content": "elasticsearch" } },
    "highlight": {
      "fields": { "content": {} }
    }
  }'
```

## Index Aliases

```bash
# Create alias
curl -X POST "http://localhost:9200/_aliases" \
  -H "Content-Type: application/json" \
  -d '{
    "actions": [
      { "add": { "index": "posts-2026", "alias": "posts" } }
    ]
  }'

# View aliases
curl http://localhost:9200/_cat/aliases

# Delete alias
curl -X POST "http://localhost:9200/_aliases" \
  -H "Content-Type: application/json" \
  -d '{
    "actions": [
      { "remove": { "index": "posts-2026", "alias": "posts" } }
    ]
  }'
```

## Cluster Management

```bash
# Cluster health
curl http://localhost:9200/_cluster/health

# Cluster stats
curl http://localhost:9200/_cluster/stats

# Node information
curl http://localhost:9200/_nodes

# Get settings
curl http://localhost:9200/_cluster/settings

# Update settings
curl -X PUT "http://localhost:9200/_cluster/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "transient": {
      "indices.queries.cache.size": "20%"
    }
  }'
```

## Templates (Index Patterns)

```bash
# Create template
curl -X PUT "http://localhost:9200/_index_template/logs-template" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["logs-*"],
    "template": {
      "settings": {
        "number_of_shards": 1
      },
      "mappings": {
        "properties": {
          "timestamp": { "type": "date" },
          "level": { "type": "keyword" }
        }
      }
    }
  }'
```

## Snapshots and Backups

```bash
# Create repository
curl -X PUT "http://localhost:9200/_snapshot/my_backup" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/mount/backups/es-backups"
    }
  }'

# Create snapshot
curl -X PUT "http://localhost:9200/_snapshot/my_backup/snap1"

# View snapshots
curl http://localhost:9200/_snapshot/my_backup/_all

# Restore snapshot
curl -X POST "http://localhost:9200/_snapshot/my_backup/snap1/_restore"
```

## Analysis and Analyzers

```bash
# Test analyzer
curl -X GET "http://localhost:9200/_analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "analyzer": "standard",
    "text": "The quick brown fox"
  }'

# Create custom analyzer
curl -X PUT "http://localhost:9200/my-index" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "analysis": {
        "analyzer": {
          "my_analyzer": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["lowercase", "stop"]
          }
        }
      }
    }
  }'
```

## Monitoring

```bash
# Index stats
curl http://localhost:9200/posts/_stats

# Segment information
curl http://localhost:9200/posts/_segments

# Force merge
curl -X POST "http://localhost:9200/posts/_forcemerge"

# Cache stats
curl http://localhost:9200/_nodes/stats/indices/fielddata
```

## Common Queries

### Search with Filters

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          { "match": { "title": "python" } }
        ],
        "filter": [
          { "range": { "published": { "gte": "2026-01-01" } } }
        ]
      }
    }
  }'
```

### Prefix Search

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "prefix": {
        "title": "ela"
      }
    }
  }'
```

### Wildcard Search

```bash
curl -X GET "http://localhost:9200/posts/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "wildcard": {
        "title": "ela*search"
      }
    }
  }'
```

## Best Practices

- Use appropriate number of shards and replicas for your use case

- Use bulk API for indexing large amounts of data

- Implement proper refresh intervals (default 1s)

- Monitor cluster health regularly

- Use index aliases for zero-downtime reindexing

- Create snapshots regularly

- Use filters instead of queries when possible (caching)

- Optimize mappings for your query patterns

- Monitor disk space and memory usage

- Use appropriate refresh policies

## Resources

- [Official Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

- [REST API Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html)

- [Query DSL Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)

- [Mapping Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)

---

_Last updated: 2026-03-30|Elasticsearch 8.0+_

Source: https://1337skills.com/cheatsheets/elasticsearch/
