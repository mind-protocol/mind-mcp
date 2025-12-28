# PATTERNS: Symbol Extraction

## Purpose

Extract code structure (functions, classes, methods, constants) from source files and upsert to graph with rich linking. Enables precise issue targeting, call graphs, health-to-symbol linking, test-to-symbol mapping, and impact analysis.

## Scope

**In Scope:**
- Python AST parsing and symbol extraction
- Node types: file, func, class, method, const
- Link types: contains, calls, imports, tests, inherits, uses, documented_by
- Test inference via naming convention, file convention, explicit markers
- Docs linking via markers, references, module naming

**Out of Scope:**
- TypeScript/JavaScript extraction (future)
- Region-level extraction (Level 3, separate spec)
- Cross-repo symbol linking
- Real-time incremental extraction

## Design Decisions

1. **Level 2 Extraction**: Files + Symbols (not regions). Balance between granularity and performance.

2. **AST-Based**: Uses Python's ast module for accurate parsing. No regex-based symbol detection.

3. **Upsert Semantics**: MERGE queries update existing nodes rather than recreating. Safe for repeated runs.

4. **Soft Delete**: Deleted files get `deleted_at_s` timestamp rather than hard delete.

5. **Phased Extraction**:
   - Phase 1: File discovery
   - Phase 2: Symbol parsing
   - Phase 3: Relationship extraction
   - Phase 4: Test inference
   - Phase 5: Docs linking

6. **Inference Strategies**: Multiple strategies for test and docs linking, with explicit markers taking precedence.

## Integration Points

- **Doctor**: `mind doctor --symbols` runs extraction before health checks
- **CLI**: `mind symbols` runs standalone extraction
- **Graph**: Upserts to FalkorDB graph via GraphOps

## Related Files

- specs/symbol-extraction.yaml - Full specification
- mind/symbol_extractor.py - Implementation
- ALGORITHM_Symbol_Extraction.md - Extraction logic
- IMPLEMENTATION_Symbol_Extraction.md - Code architecture
