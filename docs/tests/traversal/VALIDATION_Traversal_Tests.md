# Tests/Traversal — Validation

## Test Invariants

**Must hold:**
- All tests must be deterministic (same input → same output)
- Tests must not depend on external state
- Fixtures must be isolated (no shared mutable state)

**Quality gates:**
- Tests pass in CI
- Coverage > 80%
- No flaky tests
