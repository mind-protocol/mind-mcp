# DatabaseAdapter — Health

```
STATUS: DESIGNING
VERSION: v0.1
CREATED: 2025-12-26
```

---

## CHAIN

```
OBJECTIVES:     ./OBJECTIVES_DatabaseAdapter.md
PATTERNS:       ./PATTERNS_DatabaseAdapter.md
BEHAVIORS:      ./BEHAVIORS_DatabaseAdapter.md
ALGORITHM:      ./ALGORITHM_DatabaseAdapter.md
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
THIS:           HEALTH_DatabaseAdapter.md (you are here)
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Runtime health signals for the DatabaseAdapter. What to monitor in production.

---

## HEALTH SIGNALS

### H1: Connection Status

| Signal | Check | Threshold | Action |
|--------|-------|-----------|--------|
| `db.connected` | `adapter.health_check()` | Must be True | Alert on False |
| `db.latency_ms` | Time to execute `RETURN 1` | < 100ms | Warn > 100ms, Error > 500ms |

### H2: Query Performance

| Signal | Check | Threshold | Action |
|--------|-------|-----------|--------|
| `db.query_time_avg_ms` | Rolling average query time | < 50ms | Warn > 100ms |
| `db.query_count_1m` | Queries in last minute | Baseline +/- 50% | Warn on anomaly |
| `db.error_rate_1m` | Errors / Total queries | < 1% | Error > 5% |

### H3: Backend-Specific

#### FalkorDB

| Signal | Check | Threshold | Action |
|--------|-------|-----------|--------|
| `falkor.redis_memory_mb` | Redis `INFO memory` | < 80% of max | Warn > 80% |
| `falkor.graph_node_count` | `MATCH (n) RETURN count(n)` | Baseline | Track growth |

#### Neo4j

| Signal | Check | Threshold | Action |
|--------|-------|-----------|--------|
| `neo4j.heap_usage_pct` | JVM heap usage | < 80% | Warn > 80% |
| `neo4j.connection_pool` | Active/Available connections | > 20% available | Warn < 20% |

---

## HEALTH CHECK IMPLEMENTATION

```python
# mind/infrastructure/database/health.py

def check_database_health() -> dict:
    """Run all database health checks."""
    adapter = get_database_adapter()
    results = {}

    # H1: Connection status
    start = time.time()
    results["connected"] = adapter.health_check()
    results["latency_ms"] = (time.time() - start) * 1000

    if not results["connected"]:
        results["status"] = "ERROR"
        results["message"] = "Database unreachable"
        return results

    # H1: Latency threshold
    if results["latency_ms"] > 500:
        results["status"] = "ERROR"
        results["message"] = f"High latency: {results['latency_ms']:.0f}ms"
    elif results["latency_ms"] > 100:
        results["status"] = "WARN"
        results["message"] = f"Elevated latency: {results['latency_ms']:.0f}ms"
    else:
        results["status"] = "OK"

    return results
```

---

## MONITORING INTEGRATION

### Prometheus Metrics (if applicable)

```python
from prometheus_client import Gauge, Counter, Histogram

db_connected = Gauge('db_connected', 'Database connection status')
db_latency = Histogram('db_query_latency_seconds', 'Query latency')
db_errors = Counter('db_errors_total', 'Database errors')

def query_with_metrics(cypher, params=None):
    with db_latency.time():
        try:
            return adapter.query(cypher, params)
        except Exception as e:
            db_errors.inc()
            raise
```

### Log Patterns

```
[INFO] Database connected: backend=falkordb latency_ms=12
[WARN] Database latency elevated: latency_ms=150
[ERROR] Database unreachable: backend=neo4j error="Connection refused"
```

---

## RUNBOOK

### Database Unreachable

1. Check if database process is running
   - FalkorDB: `redis-cli ping`
   - Neo4j: `cypher-shell "RETURN 1"`

2. Check network connectivity
   - Can application host reach database host?
   - Firewall rules?

3. Check authentication
   - Neo4j: password correct?
   - FalkorDB: Redis AUTH if enabled?

4. Check resource exhaustion
   - FalkorDB: Redis memory limit?
   - Neo4j: JVM heap exhausted?

### High Latency

1. Check database load
   - Active queries?
   - Lock contention?

2. Check indexes
   - Missing indexes on frequently queried properties?

3. Check query patterns
   - Unbounded MATCH without LIMIT?
   - Full graph scans?

4. Check infrastructure
   - Network latency between app and db?
   - Disk I/O saturation?

---

## VERIFICATION

- [ ] Health signals defined with thresholds
- [ ] Backend-specific signals documented
- [ ] Runbook covers common failures

