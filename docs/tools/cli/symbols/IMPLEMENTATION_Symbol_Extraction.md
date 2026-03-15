# IMPLEMENTATION: Symbol Extraction

## File Structure

```
mind/
├── symbol_extractor.py    # Main implementation
├── cli.py                 # CLI integration
specs/
└── symbol-extraction.yaml # Full specification
```

## Core Classes

### mind/symbol_extractor.py

```python
class ExtractedSymbol:
    """Data class for extracted symbols."""
    id: str
    node_type: str  # 'thing'
    type: str       # 'file', 'func', 'class', 'method', 'const'
    name: str
    uri: str
    line_start: int
    line_end: int
    # ... additional type-specific fields

class ExtractedLink:
    """Data class for symbol relationships."""
    id: str
    node_a: str
    node_b: str
    type: str       # 'contains', 'relates'
    direction: str  # 'calls', 'imports', 'tests', etc.

class ExtractionResult:
    """Result of extraction run."""
    files: int
    symbols: int
    links: int
    errors: List[str]
```

### PythonExtractor

Handles Python-specific AST parsing.

```python
class PythonExtractor:
    def extract_file(self, file_path) -> Tuple[List[ExtractedSymbol], List[ExtractedLink]]
    def _extract_function(self, node, ...) -> Tuple[List, List]
    def _extract_class(self, node, ...) -> Tuple[List, List]
    def _extract_method(self, node, ...) -> Tuple[List, List]
    def _extract_constants(self, node, ...) -> Tuple[List, List]
    def _extract_calls(self, tree, ...) -> List[ExtractedLink]
    def _extract_import_links(self, tree, ...) -> List[ExtractedLink]
```

### TestInferrer

Infers test-to-source relationships.

```python
class TestInferrer:
    def infer_test_links(self, symbols, test_files) -> List[ExtractedLink]
    # Strategies: naming, file_convention, explicit
```

### DocsLinker

Links symbols to documentation.

```python
class DocsLinker:
    def link_docs(self, symbols, docs_dir) -> List[ExtractedLink]
    # Strategies: markers, references, module_convention
```

### SymbolExtractor

Main coordinator class.

```python
class SymbolExtractor:
    def __init__(self, graph_name, host, port, base_path)
    def extract_directory(self, directory, upsert) -> ExtractionResult
    def _upsert_to_graph(self, symbols, links) -> List[str]
    def _upsert_symbol(self, symbol)
    def _upsert_link(self, link)
```

## CLI Integration

### Commands

```bash
# Standalone extraction
mind symbols [--folder DIR] [--graph NAME] [--dry-run] [--verbose]

# With doctor scan
mind doctor --symbols [--graph NAME]
```

### Handler (cli.py)

```python
elif args.command == "symbols":
    result = extract_symbols_command(
        directory=args.folder,
        graph_name=args.graph,
        dry_run=args.dry_run
    )

elif args.command == "doctor":
    if args.symbols:
        extract_symbols_command(...)
    doctor_command(...)
```

## Data Flow

```
Source Files
    ↓
PythonExtractor.extract_file()
    ↓
ExtractedSymbol + ExtractedLink (containment, calls, imports)
    ↓
TestInferrer.infer_test_links()
    ↓
DocsLinker.link_docs()
    ↓
SymbolExtractor._upsert_to_graph()
    ↓
FalkorDB Graph (via GraphOps)
```

## Graph Schema

### Nodes

All symbols use label `Thing` with properties:
- `id`: Unique identifier
- `node_type`: Always 'thing'
- `type`: 'file', 'func', 'class', 'method', 'const'
- `name`, `uri`, `description`
- Type-specific properties (signature, complexity, etc.)

### Links

- `CONTAINS`: file→symbol, class→method
- `RELATES`: calls, imports, tests, inherits, uses, documented_by

## Configuration

```python
# In SymbolExtractor.__init__
include_dirs = ['mind/', 'mind/', 'tools/', 'tests/']
exclude_patterns = [
    '**/node_modules/**',
    '**/__pycache__/**',
    '**/.git/**',
    # ...
]
```

## Entry Points

1. CLI: `mind symbols`
2. CLI: `mind doctor --symbols`
3. Python: `from mind.symbol_extractor import SymbolExtractor`
4. Direct: `python -m mind.symbol_extractor --help`
