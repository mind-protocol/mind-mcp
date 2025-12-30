# Tests/Traversal — Objectives

```
MODULE: tests/traversal
TYPE: test_module
```

---

## Goals

1. **Verify traversal correctness** — Ensure SubEntity exploration produces expected results
2. **Test embedding integration** — Validate similarity-based node selection
3. **Regression prevention** — Catch traversal bugs before production

---

## Non-Goals

- Performance benchmarking (separate perf tests)
- Integration with live databases (use fixtures)

---

## Success Criteria

- [ ] 80%+ test coverage for traversal algorithms
- [ ] All traversal edge cases have test cases
- [ ] Tests run in < 5 seconds
