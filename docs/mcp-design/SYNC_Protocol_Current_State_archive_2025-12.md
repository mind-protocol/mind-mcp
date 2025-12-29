# Archived: SYNC_Protocol_Current_State.md

Archived on: 2025-12-29
Original file: SYNC_Protocol_Current_State.md

---

## NEW MARKERS (2025-12-29 Review)

<!-- @mind:escalation
title: "docs/mcp-design/ is REDUNDANT with .mind/FRAMEWORK.md"
priority: 2
context: |
  The docs/mcp-design/PATTERNS_Bidirectional_Documentation_Chain_For_AI_Agents.md
  describes the same concepts now canonically defined in .mind/FRAMEWORK.md.
  This creates confusion about which is authoritative.
question: |
  Should docs/mcp-design/ be:
  a) Removed entirely (framework is in .mind/)
  b) Kept as historical reference with deprecation notice
  c) Consolidated: move unique content to .mind/ then remove
-->

<!-- @mind:escalation
title: "Path mismatch: docs reference .mind/ but actual path is .mind/"
priority: 1
context: |
  All 64 occurrences in docs/mcp-design/ reference '.mind/' (with hyphen).
  The actual implementation uses '.mind/' (no hyphen).
  This breaks all documentation paths and agent navigation.
question: |
  Is the correct path:
  a) .mind/ (current implementation)
  b) .mind/ (documentation)
  All references need to be normalized to match actual structure.
-->

<!-- @mind:proposition
title: "Reorganize docs/mcp-design/ as module documentation"
suggestion: |
  The docs/mcp-design/ directory should be restructured:

  1. ROOT LEVEL (PATTERNS, BEHAVIORS, etc.):
     - These describe the framework itself, which is now in .mind/FRAMEWORK.md
     - Should be REMOVED or merged into .mind/

  2. doctor/ SUBDIRECTORY:
     - This is proper MODULE documentation for the doctor command
     - Should REMAIN as docs/mcp-design/doctor/ or move to docs/cli/doctor/

  3. features/ SUBDIRECTORY:
     - Contains unimplemented Agent Trace Logging
     - Should be moved to docs/proposed/ or removed

  4. ALGORITHM/ and IMPLEMENTATION/ SUBDIRECTORIES:
     - Overlap with .mind/FRAMEWORK.md
     - Should be consolidated
-->

