# ALGORITHM: Symbol Extraction

DOCS: specs/symbol-extraction.yaml

## Overview

Five-phase extraction process that creates graph nodes for code symbols and links between them.

## Phase 1: File Discovery

```
for each directory in include_dirs:
    walk directory tree
    filter by extension (.py, .ts)
    exclude patterns (node_modules, __pycache__, .git)
    yield source files
```

## Phase 2: Symbol Parsing (Python)

```
parse file with ast.parse()

extract_file(path):
    create thing_FILE node

    for node in ast.iter_child_nodes(tree):
        if FunctionDef or AsyncFunctionDef:
            create thing_FUNC node
            link: file CONTAINS func

        if ClassDef:
            create thing_CLASS node
            link: file CONTAINS class

            for method in class.body:
                create thing_METHOD node
                link: class CONTAINS method

        if Assign with UPPER_SNAKE_CASE name:
            create thing_CONST node
            link: file CONTAINS const
```

## Phase 3: Relationship Extraction

### Calls

```
for each function/method body:
    walk AST for Call nodes
    if callee is in symbol index:
        create link: caller RELATES(calls) callee
        set call_count property
```

### Imports

```
for each ImportFrom node:
    if module is local (mind/, mind/, etc.):
        resolve to file path
        create link: file RELATES(imports) target_file
```

### Inheritance

```
for each class with bases:
    if base class is in symbol index:
        create link: class RELATES(inherits) base_class
```

## Phase 4: Test Inference

Strategies (in order of precedence):

### 1. Explicit Marker
```
# TESTS: function_name, other_func

def test_something():
    ...
```
Links test_something to function_name and other_func.

### 2. Naming Convention
```
test_foo() → links to foo()
test_MyClass_method() → links to MyClass.method()
```

### 3. File Convention
```
tests/test_tick.py → links all test functions to mind/tick.py
```

## Phase 5: Docs Linking

Strategies:

### 1. Explicit Doc Marker
```python
# DOCS: docs/mind/PATTERNS_Engine.md

def run_tick():
    ...
```

### 2. Reference Detection
Scan IMPLEMENTATION*.md, PATTERNS*.md for:
- Code references: `function_name` in backticks
- File paths: mind/physics/tick.py

### 3. Module Convention
```
mind/physics/*.py → docs/mind/physics/IMPLEMENTATION*.md
```

## Graph Upsert

```cypher
MERGE (n:Thing {id: $id})
SET n += {
    node_type: 'thing',
    type: $type,
    name: $name,
    uri: $uri,
    ...
}
```

## Complexity Calculation

Cyclomatic complexity counted from:
- if/elif
- for/while
- try/except
- and/or
- comprehensions
- match/case (Python 3.10+)
- assert

## ID Patterns

| Type   | Pattern                                          |
|--------|--------------------------------------------------|
| File   | thing_FILE_{path_slug}                           |
| Func   | thing_FUNC_{file_slug}_{func_name}               |
| Class  | thing_CLASS_{file_slug}_{class_name}             |
| Method | thing_METHOD_{file_slug}_{class_slug}_{method}   |
| Const  | thing_CONST_{file_slug}_{const_name}             |

slug = lowercase, replace [/\\.\_] with hyphens, remove special chars
