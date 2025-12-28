# DatabaseAdapter — Algorithm

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
THIS:           ALGORITHM_DatabaseAdapter.md (you are here)
VALIDATION:     ./VALIDATION_DatabaseAdapter.md
IMPLEMENTATION: ./IMPLEMENTATION_DatabaseAdapter.md
HEALTH:         ./HEALTH_DatabaseAdapter.md
SYNC:           ./SYNC_DatabaseAdapter.md
```

---

## PURPOSE

Procedural logic for the DatabaseAdapter. How operations work internally.

---

## A1: Factory Initialization

```
FUNCTION get_database_adapter():
    IF _instance is None:
        config = load_yaml("mind/data/database_config.yaml")
        backend = config.database.backend  # "falkordb" or "neo4j"

        IF backend == "falkordb":
            _instance = FalkorDBAdapter(config.database.falkordb)
        ELSE IF backend == "neo4j":
            _instance = Neo4jAdapter(config.database.neo4j)
        ELSE:
            RAISE ValueError("Unknown backend")

    RETURN _instance
```

---

## A2: FalkorDB Query Execution

```
CLASS FalkorDBAdapter:

    FUNCTION __init__(config):
        self.db = FalkorDB(host=config.host, port=config.port)
        self.graph = self.db.select_graph(config.graph_name)

    FUNCTION query(cypher, params=None):
        TRY:
            result = self.graph.query(cypher, params or {})
            RETURN normalize_result(result)
        EXCEPT RedisError as e:
            IF is_connection_error(e):
                self.reconnect()
                RETURN self.query(cypher, params)  # Retry once
            RAISE DatabaseError(str(e))

    FUNCTION normalize_result(result):
        rows = []
        FOR row IN result.result_set:
            row_dict = {}
            FOR i, column IN enumerate(result.header):
                value = row[i]
                row_dict[column] = convert_to_primitive(value)
            rows.append(row_dict)
        RETURN rows

    FUNCTION convert_to_primitive(value):
        IF value is Node:
            RETURN {"id": value.id, "labels": value.labels, **value.properties}
        ELSE IF value is Edge:
            RETURN {"type": value.relation, **value.properties}
        ELSE:
            RETURN value  # Already primitive
```

---

## A3: Neo4j Query Execution

```
CLASS Neo4jAdapter:

    FUNCTION __init__(config):
        self.driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password)
        )
        self.database = config.database

    FUNCTION query(cypher, params=None):
        WITH self.driver.session(database=self.database) as session:
            result = session.run(cypher, params or {})
            RETURN [self.normalize_record(r) for r in result]

    FUNCTION normalize_record(record):
        row_dict = {}
        FOR key, value IN record.items():
            row_dict[key] = self.convert_to_primitive(value)
        RETURN row_dict

    FUNCTION convert_to_primitive(value):
        IF value is neo4j.Node:
            RETURN {"id": value.element_id, "labels": list(value.labels), **dict(value)}
        ELSE IF value is neo4j.Relationship:
            RETURN {"type": value.type, **dict(value)}
        ELSE:
            RETURN value
```

---

## A4: Transaction Handling

### FalkorDB Transactions

```
CLASS FalkorDBAdapter:

    FUNCTION transaction():
        # FalkorDB doesn't have explicit transactions in the same way
        # Queries are atomic individually
        # For multi-query atomicity, use MULTI/EXEC at Redis level
        RETURN FalkorDBTransaction(self.graph)

CLASS FalkorDBTransaction:

    FUNCTION __enter__():
        self.commands = []
        RETURN self

    FUNCTION execute(cypher, params=None):
        self.commands.append((cypher, params))

    FUNCTION __exit__(exc_type, exc_val, exc_tb):
        IF exc_type is None:
            FOR cypher, params IN self.commands:
                self.graph.query(cypher, params or {})
        # On exception, commands not executed = implicit rollback
```

### Neo4j Transactions

```
CLASS Neo4jAdapter:

    FUNCTION transaction():
        RETURN Neo4jTransaction(self.driver, self.database)

CLASS Neo4jTransaction:

    FUNCTION __enter__():
        self.session = self.driver.session(database=self.database)
        self.tx = self.session.begin_transaction()
        RETURN self

    FUNCTION execute(cypher, params=None):
        self.tx.run(cypher, params or {})

    FUNCTION __exit__(exc_type, exc_val, exc_tb):
        IF exc_type is None:
            self.tx.commit()
        ELSE:
            self.tx.rollback()
        self.session.close()
```

---

## A5: Index Creation

```
CLASS FalkorDBAdapter:

    FUNCTION create_index(label, property):
        cypher = f"CREATE INDEX FOR (n:{label}) ON (n.{property})"
        self.execute(cypher)

CLASS Neo4jAdapter:

    FUNCTION create_index(label, property):
        index_name = f"{label.lower()}_{property.lower()}"
        cypher = f"CREATE INDEX {index_name} FOR (n:{label}) ON (n.{property})"
        self.execute(cypher)
```

---

## A6: Health Check

```
CLASS FalkorDBAdapter:

    FUNCTION health_check():
        TRY:
            self.graph.query("RETURN 1")
            RETURN True
        EXCEPT:
            RETURN False

CLASS Neo4jAdapter:

    FUNCTION health_check():
        TRY:
            WITH self.driver.session() as session:
                session.run("RETURN 1")
            RETURN True
        EXCEPT:
            RETURN False
```

---

## A7: Connection Recovery

```
CLASS FalkorDBAdapter:

    FUNCTION reconnect():
        TRY:
            self.db = FalkorDB(host=self.config.host, port=self.config.port)
            self.graph = self.db.select_graph(self.config.graph_name)
        EXCEPT:
            RAISE DatabaseConnectionError("Failed to reconnect to FalkorDB")

CLASS Neo4jAdapter:

    FUNCTION reconnect():
        # Neo4j driver handles connection pooling internally
        # Just verify connectivity
        IF NOT self.health_check():
            RAISE DatabaseConnectionError("Failed to reconnect to Neo4j")
```

---

## VERIFICATION

- [ ] All algorithms have pseudocode
- [ ] Both backends covered
- [ ] Edge cases documented

