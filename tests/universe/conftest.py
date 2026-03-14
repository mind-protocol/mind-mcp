"""
Test fixtures for universe graph tests.

Provides a FakeAdapter that simulates a graph database in memory,
supporting the subset of Cypher patterns used by the universe module.
"""

import json
import re
from contextlib import contextmanager
from typing import Dict, Any, List, Optional

import pytest

from runtime.infrastructure.database.adapter import DatabaseAdapter, TransactionAdapter


class FakeNode:
    """In-memory graph node."""
    def __init__(self, labels: set, props: Dict[str, Any]):
        self.labels = labels
        self.props = dict(props)

    def matches_label(self, label: str) -> bool:
        return label in self.labels

    def get(self, key: str, default=None):
        return self.props.get(key, default)

    def __repr__(self):
        return f"FakeNode(labels={self.labels}, id={self.props.get('id')})"


class FakeLink:
    """In-memory graph link (relationship)."""
    def __init__(self, src_id: str, dst_id: str, rel_type: str, props: Dict[str, Any]):
        self.src_id = src_id
        self.dst_id = dst_id
        self.rel_type = rel_type
        self.props = dict(props)

    def get(self, key: str, default=None):
        return self.props.get(key, default)

    def __repr__(self):
        return f"FakeLink({self.src_id}->{self.dst_id}, type={self.rel_type})"


class FakeAdapter(DatabaseAdapter):
    """
    In-memory graph database adapter for testing.

    Supports the specific Cypher patterns used by the universe module:
    - CREATE (n:Label { ... })
    - MATCH (n:Label {id: $param}) and multi-MATCH
    - MATCH ... CREATE ... (node creation after match)
    - MATCH ... WHERE ... RETURN
    - MATCH ... SET ...
    - MATCH ... DELETE ...
    - OPTIONAL MATCH
    - count(), ORDER BY, LIMIT

    This is NOT a general Cypher engine. It handles the specific patterns
    used in the codebase via pattern matching on the query string.
    """

    def __init__(self, graph_name_str: str = "test_universe"):
        self._graph_name = graph_name_str
        self.nodes: Dict[str, FakeNode] = {}
        self.links: List[FakeLink] = []

    @property
    def graph_name(self) -> str:
        return self._graph_name

    def add_node(self, node_id: str, labels: set, props: Dict[str, Any]) -> None:
        """Direct node insertion for test setup."""
        props.setdefault("id", node_id)
        self.nodes[node_id] = FakeNode(labels, props)

    def add_link(self, src_id: str, dst_id: str, rel_type: str, props: Dict[str, Any]) -> None:
        """Direct link insertion for test setup."""
        self.links.append(FakeLink(src_id, dst_id, rel_type, props))

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        params = params or {}
        cypher_clean = _normalize(cypher)
        return self._dispatch_query(cypher_clean, params)

    def execute(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> None:
        params = params or {}
        cypher_clean = _normalize(cypher)
        self._dispatch_execute(cypher_clean, params)

    @contextmanager
    def transaction(self):
        yield self

    def create_index(self, label: str, property_name: str) -> None:
        pass

    def health_check(self) -> bool:
        return True

    def close(self) -> None:
        pass

    # =========================================================================
    # DISPATCH
    # =========================================================================

    def _dispatch_execute(self, cypher: str, params: Dict[str, Any]) -> None:
        """Route a mutation Cypher to the appropriate handler."""
        if "CREATE" in cypher and "MATCH" not in cypher:
            self._handle_create_node(cypher, params)
        elif "MATCH" in cypher and "CREATE" in cypher:
            self._handle_match_create(cypher, params)
        elif "MATCH" in cypher and "DELETE" in cypher:
            self._handle_match_delete(cypher, params)
        elif "MATCH" in cypher and "SET" in cypher:
            self._handle_match_set(cypher, params)
        else:
            pass  # Unknown pattern, silently ignore

    def _dispatch_query(self, cypher: str, params: Dict[str, Any]) -> List[Any]:
        """Route a query Cypher to the appropriate handler."""
        if "count(" in cypher.lower():
            return self._handle_count_query(cypher, params)
        elif "RETURN" in cypher:
            return self._handle_match_return(cypher, params)
        return []

    # =========================================================================
    # CREATE NODE (no MATCH prefix)
    # =========================================================================

    def _handle_create_node(self, cypher: str, params: Dict[str, Any]) -> None:
        """Handle: CREATE (n:Label { ... })"""
        label_match = re.search(r'CREATE\s*\(\w+:(\w+)\s*\{', cypher)
        if not label_match:
            return
        label = label_match.group(1)

        props = self._extract_create_props(cypher, params)
        node_id = props.get("id")
        if node_id is None:
            return

        self.nodes[node_id] = FakeNode({label, props.get("node_type", "").capitalize()}, props)

    # =========================================================================
    # MATCH + CREATE (relationship or node after match)
    # =========================================================================

    def _handle_match_create(self, cypher: str, params: Dict[str, Any]) -> None:
        """Handle: MATCH (a:Label {id: $x}) MATCH (b:Label {id: $y}) CREATE (a)-[:rel {...}]->(b)"""
        # Extract the CREATE part
        create_idx = cypher.index("CREATE")
        create_part = cypher[create_idx:]

        # Check if this is a relationship creation
        rel_match = re.search(r'CREATE\s*\(\w+\)-\[:(\w+)\s*\{', create_part)
        if rel_match:
            self._handle_create_relationship(cypher, params, create_part)
            return

        # Otherwise it might be a node creation after MATCH -- treat as node create
        self._handle_create_node(create_part, params)

    def _handle_create_relationship(self, cypher: str, params: Dict[str, Any], create_part: str) -> None:
        """Create a relationship from MATCH+CREATE pattern."""
        # Extract relationship props
        props = self._extract_create_props(create_part, params)

        # Determine src and dst from params
        src_id = props.get("node_a")
        dst_id = props.get("node_b")

        if src_id is None or dst_id is None:
            # Try to infer from MATCH clauses
            match_ids = re.findall(r'\{id:\s*\$(\w+)\}', cypher)
            param_values = [params.get(m) for m in match_ids]
            if len(param_values) >= 2:
                src_id = src_id or param_values[0]
                dst_id = dst_id or param_values[1]

        if src_id is None or dst_id is None:
            return

        # Determine the rel_type from props or from Cypher
        rel_type = "link"

        self.links.append(FakeLink(src_id, dst_id, rel_type, props))

    # =========================================================================
    # MATCH + RETURN (queries)
    # =========================================================================

    def _handle_match_return(self, cypher: str, params: Dict[str, Any]) -> List[Any]:
        """Handle various MATCH ... RETURN queries."""
        # Parse MATCH clauses to determine what we're looking for
        matches = self._parse_match_clauses(cypher, params)

        # Parse WHERE conditions
        where_conditions = self._parse_where(cypher, params)

        # Parse RETURN clause
        return_fields = self._parse_return(cypher)

        # Determine if this is a relationship query or node query
        if "-[" in cypher or "]->" in cypher or "]-(" in cypher:
            return self._execute_relationship_query(
                cypher, params, matches, where_conditions, return_fields
            )
        else:
            return self._execute_node_query(
                cypher, params, matches, where_conditions, return_fields
            )

    def _execute_node_query(
        self, cypher, params, matches, where_conditions, return_fields
    ) -> List[Any]:
        """Execute a pure node query (no relationships)."""
        results = []

        for node_id, node in self.nodes.items():
            if self._node_matches(node, matches, where_conditions, params):
                row = self._build_return_row(return_fields, node=node)
                if row is not None:
                    results.append(row)

        # Handle ORDER BY
        if "ORDER BY" in cypher:
            order_match = re.search(r'ORDER BY\s+(\w+\.\w+)', cypher)
            if order_match:
                field = order_match.group(1).split(".")[-1]
                results.sort(key=lambda r: r[-1] if r else 0)

        # Handle LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', cypher)
        if limit_match:
            limit = int(limit_match.group(1))
            results = results[:limit]

        return results

    def _execute_relationship_query(
        self, cypher, params, matches, where_conditions, return_fields
    ) -> List[Any]:
        """Execute a query involving relationships."""
        results = []

        # Parse source and target constraints
        src_constraint = self._parse_endpoint_constraint(cypher, "source", params)
        dst_constraint = self._parse_endpoint_constraint(cypher, "target", params)

        # Extract variable names from the MATCH pattern for RETURN mapping
        var_map = self._extract_var_names(cypher)

        for link in self.links:
            src_node = self.nodes.get(link.src_id)
            dst_node = self.nodes.get(link.dst_id)
            if src_node is None or dst_node is None:
                continue

            if not self._link_matches(link, src_node, dst_node, src_constraint, dst_constraint, where_conditions, params):
                continue

            row = self._build_return_row_with_link(return_fields, src_node, link, dst_node, var_map)
            if row is not None:
                results.append(row)

        # Handle ORDER BY
        if "ORDER BY" in cypher:
            order_match = re.search(r'ORDER BY\s+([\w.]+)\s*(DESC)?', cypher)
            if order_match:
                desc = order_match.group(2) is not None
                results.sort(key=lambda r: (r[-1] if r else 0) or 0, reverse=desc)

        # Handle LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', cypher)
        if limit_match:
            limit = int(limit_match.group(1))
            results = results[:limit]

        return results

    # =========================================================================
    # MATCH + DELETE
    # =========================================================================

    def _handle_match_delete(self, cypher: str, params: Dict[str, Any]) -> None:
        """Handle: MATCH (n:Label {id: $x}) ... DELETE ..."""
        # Determine what to delete from the DELETE clause
        delete_match = re.search(r'DELETE\s+(.*?)$', cypher)
        if not delete_match:
            return
        delete_targets = [t.strip() for t in delete_match.group(1).split(",")]

        # Find matched node IDs
        match_ids = re.findall(r'\{id:\s*\$(\w+)\}', cypher)
        node_ids_to_check = [params.get(m) for m in match_ids if params.get(m)]

        # Get link type constraint from WHERE
        type_cond = self._extract_where_type(cypher, params)

        # Check if this is a relationship-based delete pattern
        has_relationship = "-[" in cypher

        if has_relationship:
            # Relationship match pattern: delete matching links
            # and optionally the matched nodes
            delete_rels = any(t in ("r",) for t in delete_targets)
            delete_node_vars = [t for t in delete_targets if t not in ("r",)]

            if delete_rels:
                # Delete links that match the constraint
                # Need to find src/dst from matched nodes
                src_constraint = self._parse_endpoint_constraint(cypher, "source", params)
                dst_constraint = self._parse_endpoint_constraint(cypher, "target", params)

                new_links = []
                for link in self.links:
                    src_node = self.nodes.get(link.src_id)
                    dst_node = self.nodes.get(link.dst_id)
                    if src_node is None or dst_node is None:
                        new_links.append(link)
                        continue

                    matches = self._link_matches(
                        link, src_node, dst_node,
                        src_constraint, dst_constraint,
                        self._parse_where(cypher, params), params
                    )
                    if matches:
                        continue  # Skip = delete this link
                    new_links.append(link)
                self.links = new_links

            # Delete matched nodes if requested
            for var in delete_node_vars:
                # Map var to matched node ID
                # s = Space node (typically the second match)
                if var == "s" and len(node_ids_to_check) >= 1:
                    # Find the Space node ID
                    for nid in node_ids_to_check:
                        node = self.nodes.get(nid)
                        if node and (node.matches_label("Space") or node.props.get("node_type") == "space"):
                            self.nodes.pop(nid, None)
                            # Also remove any remaining links to/from this node
                            self.links = [l for l in self.links if l.src_id != nid and l.dst_id != nid]
                            break

        elif "OPTIONAL MATCH" in cypher:
            # Pattern: MATCH (s:Space {id: $id}) OPTIONAL MATCH (s)-[r]-() DELETE r, s
            for node_id in node_ids_to_check:
                if "r" in delete_targets:
                    self.links = [l for l in self.links if l.src_id != node_id and l.dst_id != node_id]
                if "s" in delete_targets or node_id in [params.get(m) for m in match_ids]:
                    self.nodes.pop(node_id, None)
        else:
            # Simple node delete
            for node_id in node_ids_to_check:
                if node_id:
                    self.nodes.pop(node_id, None)
                    self.links = [l for l in self.links if l.src_id != node_id and l.dst_id != node_id]

    # =========================================================================
    # MATCH + SET
    # =========================================================================

    def _handle_match_set(self, cypher: str, params: Dict[str, Any]) -> None:
        """Handle: MATCH ... SET r.prop = $val ..."""
        # Find matching links
        match_ids = re.findall(r'\{id:\s*\$(\w+)\}', cypher)
        node_ids = [params.get(m) for m in match_ids]

        type_cond = self._extract_where_type(cypher, params)

        for link in self.links:
            if link.src_id in node_ids and link.dst_id in node_ids:
                if type_cond is None or link.props.get("type") == type_cond:
                    # Apply SET clauses
                    set_match = re.findall(r'SET\s+(.*?)(?:$)', cypher)
                    if set_match:
                        for assignment in set_match[0].split(","):
                            assignment = assignment.strip()
                            prop_match = re.match(r'r\.(\w+)\s*=\s*\$(\w+)', assignment)
                            if prop_match:
                                prop_name = prop_match.group(1)
                                param_name = prop_match.group(2)
                                if param_name in params:
                                    link.props[prop_name] = params[param_name]

    # =========================================================================
    # COUNT queries
    # =========================================================================

    def _handle_count_query(self, cypher: str, params: Dict[str, Any]) -> List[Any]:
        """Handle queries with count()."""
        matches = self._parse_match_clauses(cypher, params)
        where_conditions = self._parse_where(cypher, params)

        count = 0
        for node_id, node in self.nodes.items():
            if self._node_matches(node, matches, where_conditions, params):
                count += 1

        return [[count]]

    # =========================================================================
    # PARSING HELPERS
    # =========================================================================

    def _extract_create_props(self, cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract properties from a CREATE clause, resolving $param references."""
        props = {}
        # Find all key: $param patterns
        prop_matches = re.findall(r'(\w+)\s*:\s*\$(\w+)', cypher)
        for key, param_name in prop_matches:
            if param_name in params:
                props[key] = params[param_name]

        # Find literal values: key: value
        literal_matches = re.findall(r"(\w+)\s*:\s*'([^']*)'", cypher)
        for key, value in literal_matches:
            if key not in props:
                props[key] = value

        # Find literal numbers: key: 1.0
        num_matches = re.findall(r'(\w+)\s*:\s*(-?\d+\.?\d*)', cypher)
        for key, value in num_matches:
            if key not in props and key != "id":
                try:
                    props[key] = float(value) if "." in value else int(value)
                except ValueError:
                    pass

        # Handle NULL values
        null_matches = re.findall(r'(\w+)\s*:\s*NULL', cypher)
        for key in null_matches:
            if key not in props:
                props[key] = None

        return props

    def _parse_match_clauses(self, cypher: str, params: Dict[str, Any]) -> List[Dict]:
        """Parse MATCH clauses to get label and property constraints."""
        matches = []
        # Pattern: (var:Label {prop: $param, ...})
        pattern = r'\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)'
        for match in re.finditer(pattern, cypher):
            var_name = match.group(1)
            label = match.group(2)
            prop_str = match.group(3) or ""

            constraints = {"_var": var_name, "_label": label}
            for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                key = prop_match.group(1)
                param_name = prop_match.group(2)
                if param_name in params:
                    constraints[key] = params[param_name]

            matches.append(constraints)

        return matches

    def _parse_where(self, cypher: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse WHERE clause conditions."""
        conditions = {}
        where_match = re.search(r'WHERE\s+(.*?)(?:RETURN|ORDER|LIMIT|$)', cypher, re.DOTALL)
        if not where_match:
            return conditions

        where_str = where_match.group(1).strip()

        # Parse r.type = 'value' conditions
        for match in re.finditer(r"(\w+)\.(\w+)\s*=\s*'([^']*)'", where_str):
            var = match.group(1)
            prop = match.group(2)
            val = match.group(3)
            conditions[f"{var}.{prop}"] = val

        # Parse r.prop = $param conditions
        for match in re.finditer(r'(\w+)\.(\w+)\s*=\s*\$(\w+)', where_str):
            var = match.group(1)
            prop = match.group(2)
            param = match.group(3)
            if param in params:
                conditions[f"{var}.{prop}"] = params[param]

        # Parse r.prop IS NOT NULL
        for match in re.finditer(r'(\w+)\.(\w+)\s+IS\s+NOT\s+NULL', where_str):
            var = match.group(1)
            prop = match.group(2)
            conditions[f"{var}.{prop}__not_null"] = True

        # Parse r.prop > value
        for match in re.finditer(r'(\w+)\.(\w+)\s*>\s*(\d+\.?\d*)', where_str):
            var = match.group(1)
            prop = match.group(2)
            val = float(match.group(3))
            conditions[f"{var}.{prop}__gt"] = val

        # Parse r.type <> 'value'
        for match in re.finditer(r"(\w+)\.(\w+)\s*<>\s*'([^']*)'", where_str):
            var = match.group(1)
            prop = match.group(2)
            val = match.group(3)
            conditions[f"{var}.{prop}__neq"] = val

        return conditions

    def _parse_return(self, cypher: str) -> List[str]:
        """Parse RETURN clause field list."""
        return_match = re.search(r'RETURN\s+(.*?)(?:ORDER|LIMIT|$)', cypher, re.DOTALL)
        if not return_match:
            return []
        return_str = return_match.group(1).strip()
        fields = [f.strip() for f in return_str.split(",")]
        return fields

    def _parse_endpoint_constraint(self, cypher: str, role: str, params: Dict[str, Any]) -> Dict:
        """Parse source or target node constraint from relationship MATCH pattern."""
        constraint = {}

        # Try full pattern: (var:Label {props})-[r:link]->(var:Label {props})
        rel_match = re.search(
            r'\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)\s*-\[.*?\]->\s*\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)',
            cypher
        )
        if rel_match:
            if role == "source":
                label = rel_match.group(2)
                prop_str = rel_match.group(3) or ""
            else:  # target
                label = rel_match.group(5)
                prop_str = rel_match.group(6) or ""

            constraint["_label"] = label
            for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                key = prop_match.group(1)
                param_name = prop_match.group(2)
                if param_name in params:
                    constraint[key] = params[param_name]
            return constraint

        # Try pattern with wildcard source: ()-[r:link]->(var:Label {props})
        wild_src = re.search(
            r'\(\)\s*-\[.*?\]->\s*\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)',
            cypher
        )
        if wild_src:
            if role == "source":
                return {}  # Wildcard: no constraint on source
            else:
                label = wild_src.group(2)
                prop_str = wild_src.group(3) or ""
                constraint["_label"] = label
                for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                    key = prop_match.group(1)
                    param_name = prop_match.group(2)
                    if param_name in params:
                        constraint[key] = params[param_name]
                return constraint

        # Try pattern with wildcard target: (var:Label {props})-[r:link]->()
        wild_dst = re.search(
            r'\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)\s*-\[.*?\]->\s*\(\)',
            cypher
        )
        if wild_dst:
            if role == "target":
                return {}  # Wildcard: no constraint on target
            else:
                label = wild_dst.group(2)
                prop_str = wild_dst.group(3) or ""
                constraint["_label"] = label
                for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                    key = prop_match.group(1)
                    param_name = prop_match.group(2)
                    if param_name in params:
                        constraint[key] = params[param_name]
                return constraint

        # Try with MATCH (n {id: $id}) pattern (no label)
        no_label = re.search(
            r'\(\w+\s*\{([^}]*)\}\s*\)\s*-\[.*?\]->\s*\((\w+):(\w+)\s*(?:\{([^}]*)\})?\s*\)',
            cypher
        )
        if no_label:
            if role == "source":
                prop_str = no_label.group(1) or ""
                for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                    key = prop_match.group(1)
                    param_name = prop_match.group(2)
                    if param_name in params:
                        constraint[key] = params[param_name]
            else:
                label = no_label.group(3)
                prop_str = no_label.group(4) or ""
                constraint["_label"] = label
                for prop_match in re.finditer(r'(\w+)\s*:\s*\$(\w+)', prop_str):
                    key = prop_match.group(1)
                    param_name = prop_match.group(2)
                    if param_name in params:
                        constraint[key] = params[param_name]
            return constraint

        return constraint

    def _extract_where_type(self, cypher: str, params: Dict[str, Any]) -> Optional[str]:
        """Extract r.type = '...' from WHERE clause."""
        match = re.search(r"r\.type\s*=\s*'([^']*)'", cypher)
        if match:
            return match.group(1)
        return None

    def _extract_var_names(self, cypher: str) -> Dict[str, str]:
        """Extract variable name -> role mapping from MATCH pattern.

        Returns dict like {"a": "src", "r": "link", "s": "dst"}
        """
        var_map = {}

        # Try full pattern: (srcVar:Label)-[relVar:Type]->(dstVar:Label)
        full = re.search(
            r'\((\w+)(?::[\w]+)?[^)]*\)\s*-\[(\w+):',
            cypher
        )
        if full:
            var_map[full.group(1)] = "src"
            var_map[full.group(2)] = "link"

        # Find the target var after ->
        target = re.search(
            r'->\s*\((\w+)(?::[\w]+)?',
            cypher
        )
        if target:
            var_map[target.group(1)] = "dst"

        # Handle wildcard source ()-[r:link]->
        if "()" in cypher.split("-[")[0] if "-[" in cypher else "":
            # No source var
            pass

        return var_map

    # =========================================================================
    # MATCHING HELPERS
    # =========================================================================

    def _node_matches(self, node: FakeNode, matches: list, where_conds: dict, params: dict) -> bool:
        """Check if a node satisfies the match constraints."""
        if not matches:
            return True

        for match_constraint in matches:
            label = match_constraint.get("_label", "")

            # Check label
            if label and not node.matches_label(label):
                # Also check node_type
                if node.props.get("node_type", "").lower() != label.lower():
                    continue

            # Check property constraints
            all_match = True
            for key, value in match_constraint.items():
                if key.startswith("_"):
                    continue
                if node.props.get(key) != value:
                    all_match = False
                    break

            if all_match:
                # Also check where conditions on this node's var
                var = match_constraint.get("_var", "")
                for cond_key, cond_val in where_conds.items():
                    if cond_key.startswith(f"{var}."):
                        prop = cond_key.split(".", 1)[1]
                        if prop.endswith("__not_null"):
                            real_prop = prop.replace("__not_null", "")
                            if node.props.get(real_prop) is None:
                                all_match = False
                                break
                        elif prop.endswith("__gt"):
                            real_prop = prop.replace("__gt", "")
                            node_val = node.props.get(real_prop, 0)
                            if node_val is None or float(node_val) <= cond_val:
                                all_match = False
                                break
                        elif prop.endswith("__neq"):
                            real_prop = prop.replace("__neq", "")
                            if node.props.get(real_prop) == cond_val:
                                all_match = False
                                break
                        else:
                            if node.props.get(prop) != cond_val:
                                all_match = False
                                break

                if all_match:
                    return True

        return False

    def _link_matches(
        self,
        link: FakeLink,
        src_node: FakeNode,
        dst_node: FakeNode,
        src_constraint: Dict,
        dst_constraint: Dict,
        where_conditions: Dict,
        params: Dict,
    ) -> bool:
        """Check if a link matches the query constraints."""
        # Check source constraint
        if src_constraint:
            label = src_constraint.get("_label", "")
            if label:
                if not src_node.matches_label(label) and src_node.props.get("node_type", "").lower() != label.lower():
                    return False
            for key, value in src_constraint.items():
                if key.startswith("_"):
                    continue
                if src_node.props.get(key) != value:
                    return False

        # Check destination constraint
        if dst_constraint:
            label = dst_constraint.get("_label", "")
            if label:
                if not dst_node.matches_label(label) and dst_node.props.get("node_type", "").lower() != label.lower():
                    return False
            for key, value in dst_constraint.items():
                if key.startswith("_"):
                    continue
                if dst_node.props.get(key) != value:
                    return False

        # Check WHERE conditions on link (r.*) and node vars
        for cond_key, cond_val in where_conditions.items():
            if cond_key.startswith("r."):
                prop = cond_key[2:]
                if prop.endswith("__not_null"):
                    real_prop = prop.replace("__not_null", "")
                    if link.props.get(real_prop) is None:
                        return False
                elif prop.endswith("__gt"):
                    real_prop = prop.replace("__gt", "")
                    link_val = link.props.get(real_prop, 0)
                    if link_val is None or float(link_val) <= cond_val:
                        return False
                elif prop.endswith("__neq"):
                    real_prop = prop.replace("__neq", "")
                    if link.props.get(real_prop) == cond_val:
                        return False
                else:
                    if link.props.get(prop) != cond_val:
                        return False
                continue

            # Check conditions on source/destination node vars
            # Map known source vars and target vars
            dot_pos = cond_key.find(".")
            if dot_pos < 0:
                continue
            var = cond_key[:dot_pos]
            prop = cond_key[dot_pos + 1:]

            # Determine which node the var refers to based on match parsing
            # Source vars: typically first matched (a, parent, m for Thing->Space)
            # Target vars: typically second matched (s, b, child, n for ->Narrative)
            src_vars = {"a", "parent", "m"}
            dst_vars = {"s", "b", "child", "n"}

            target_node = None
            if var in src_vars:
                target_node = src_node
            elif var in dst_vars:
                target_node = dst_node
            else:
                # Try to determine from the MATCH clause variable names
                # Fallback: check both nodes
                pass

            if target_node is not None:
                if not self._check_where_prop(target_node, prop, cond_val):
                    return False

        # Check WHERE on hierarchy specifically (common pattern)
        if "r.hierarchy" in where_conditions:
            if link.props.get("hierarchy") != where_conditions["r.hierarchy"]:
                return False

        return True

    @staticmethod
    def _check_where_prop(node: 'FakeNode', prop: str, expected) -> bool:
        """Check a WHERE condition on a node property."""
        if prop.endswith("__not_null"):
            real_prop = prop.replace("__not_null", "")
            return node.props.get(real_prop) is not None
        elif prop.endswith("__gt"):
            real_prop = prop.replace("__gt", "")
            val = node.props.get(real_prop, 0)
            return val is not None and float(val) > expected
        elif prop.endswith("__neq"):
            real_prop = prop.replace("__neq", "")
            return node.props.get(real_prop) != expected
        else:
            return node.props.get(prop) == expected

    def _build_return_row(self, return_fields: List[str], node: FakeNode) -> Optional[List]:
        """Build a result row from return fields for a node query."""
        row = []
        for field in return_fields:
            field = field.strip()
            if "." in field:
                parts = field.split(".")
                prop = parts[-1]
                row.append(node.props.get(prop))
            elif field.startswith("count("):
                row.append(1)
            else:
                row.append(None)
        return row

    def _build_return_row_with_link(
        self, return_fields: List[str], src: FakeNode, link: FakeLink, dst: FakeNode,
        var_map: Optional[Dict[str, str]] = None,
    ) -> Optional[List]:
        """Build a result row from return fields for a relationship query."""
        var_map = var_map or {}
        row = []
        for field in return_fields:
            field = field.strip()
            if "." in field:
                parts = field.split(".")
                var = parts[0]
                prop = parts[1]

                # Use var_map first, then fall back to heuristics
                role = var_map.get(var)
                if role == "link":
                    row.append(link.props.get(prop))
                elif role == "src":
                    row.append(src.props.get(prop))
                elif role == "dst":
                    row.append(dst.props.get(prop))
                elif var == "r":
                    row.append(link.props.get(prop))
                else:
                    # Fallback: try src then dst
                    val = src.props.get(prop)
                    if val is None:
                        val = dst.props.get(prop)
                    row.append(val)
            elif field.startswith("count("):
                row.append(1)
            else:
                row.append(None)
        return row


def _normalize(cypher: str) -> str:
    """Normalize whitespace in a Cypher query."""
    return " ".join(cypher.split())


# =========================================================================
# FIXTURES
# =========================================================================

@pytest.fixture
def adapter():
    """Provide a fresh FakeAdapter for each test."""
    return FakeAdapter()


@pytest.fixture
def adapter_with_actor(adapter):
    """Provide an adapter with a pre-created Actor node."""
    adapter.add_node("actor_alice", {"Actor"}, {
        "id": "actor_alice",
        "name": "Alice",
        "node_type": "actor",
        "type": None,
        "weight": 1.0,
        "energy": 0.0,
        "stability": 0.5,
        "recency": 1.0,
    })
    return adapter


@pytest.fixture
def adapter_with_two_actors(adapter_with_actor):
    """Provide an adapter with two Actor nodes."""
    adapter_with_actor.add_node("actor_bob", {"Actor"}, {
        "id": "actor_bob",
        "name": "Bob",
        "node_type": "actor",
        "type": None,
        "weight": 1.0,
        "energy": 0.0,
        "stability": 0.5,
        "recency": 1.0,
    })
    return adapter_with_actor


@pytest.fixture
def space_manager(adapter_with_actor):
    """Provide a SpaceManager with one actor."""
    from runtime.universe.space_and_hierarchy_manager import SpaceManager
    return SpaceManager(adapter_with_actor)


@pytest.fixture
def access_resolver(adapter_with_two_actors):
    """Provide an AccessResolver with two actors."""
    from runtime.universe.space_and_hierarchy_manager import SpaceManager
    from runtime.universe.access_resolution_and_link_manager import AccessResolver
    sm = SpaceManager(adapter_with_two_actors)
    return AccessResolver(adapter_with_two_actors, sm)
