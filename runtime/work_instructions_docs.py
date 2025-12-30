# DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
"""
Documentation-related work instructions.

This module contains work prompts for documentation issues:
UNDOCUMENTED, PLACEHOLDER, INCOMPLETE_CHAIN, NO_DOCS_REF, UNDOC_IMPL,
ORPHAN_DOCS, DOC_DUPLICATION, LARGE_DOC_MODULE, DOC_GAPS, STALE_IMPL

Extracted from work_instructions.py to reduce file size.
"""

from pathlib import Path
from typing import Any, Dict

# Import DoctorIssue type for type hints
from .doctor import DoctorIssue


def get_doc_instructions(issue: DoctorIssue, target_dir: Path) -> Dict[str, Any]:
    """Get instructions for documentation-related issues."""

    instructions = {
        "UNDOCUMENTED": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Create documentation for undocumented code",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                ".mind/PROTOCOL.md",
                ".mind/templates/OBJECTIVES_TEMPLATE.md",
                ".mind/templates/PATTERNS_TEMPLATE.md",
                ".mind/templates/SYNC_TEMPLATE.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Document Module

**Target:** `{issue.path}`
**Problem:** {issue.message}

## CRITICAL: Check for existing docs first

Before creating anything, search for existing documentation:
- `grep -r "{issue.path}" docs/` - check if this path is mentioned in existing docs
- Search `docs/**/IMPLEMENTATION_*.md` for references to this code
- Check `modules.yaml` for existing mappings that might cover this code
- If docs exist elsewhere, UPDATE the mapping instead of creating duplicates

## Steps:

1. Read the VIEW, PROTOCOL.md, and template docs listed above
2. Search for existing docs that might cover this code
3. If found: update `modules.yaml` mapping to link existing docs
4. If not found:
   a. Check `modules.yaml` and `docs/` to see existing naming patterns
   b. Read the code in `{issue.path}` to understand what it does
   c. Choose a descriptive module name (e.g., `cli`, `auth`) not the code path
   d. Follow the pattern: `docs/{{module}}/` or `docs/{{area}}/{{module}}/`
   e. Add mapping to `modules.yaml`
   f. Create minimum viable docs: OBJECTIVES_*.md + PATTERNS_*.md + SYNC_*.md
5. Add DOCS: reference to main source file
6. Update SYNC_Project_State.md

## Success Criteria:
- modules.yaml has mapping (new or updated)
- PATTERNS doc exists with actual content
- SYNC doc exists
- NO duplicate documentation created

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [
                "modules.yaml",
                ".mind/state/SYNC_Project_State.md",
            ],
        },

        "PLACEHOLDER": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Fill in placeholder content",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                issue.path,
            ],
            "prompt": f"""## Task: Fill In Placeholders

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Placeholders found:** {issue.details.get('placeholders', [])}

## Steps:

1. Read the VIEW doc and the file with placeholders
2. Identify each placeholder (like {{MODULE_NAME}}, {{DESCRIPTION}}, etc.)
3. Read related code/docs to understand what should replace each placeholder
4. Replace all placeholders with actual content
5. Ensure the document makes sense and is complete

## Success Criteria:
- No {{PLACEHOLDER}} patterns remain
- Content is meaningful, not generic
- Document is useful for agents

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "INCOMPLETE_CHAIN": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Complete documentation chain",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Complete Documentation Chain

**Target:** `{issue.path}`
**Missing docs:** {issue.details.get('missing', [])}
**Existing docs:** {issue.details.get('present', [])}

## CRITICAL: Check for existing docs first

Before creating any missing doc type:
- Search `docs/` for existing docs of that type that might cover this module
- Check if the missing doc exists in a different location or with different name
- If found elsewhere, link to it instead of creating a duplicate

## IMPLEMENTATION doc guidance

One IMPLEMENTATION doc per module that documents ALL files in that module.

**File Responsibilities table MUST include:**
- Line count for each file (approximate)
- Status: OK (<400L), WATCH (400-700L), or SPLIT (>700L)
- Any WATCH/SPLIT files need extraction candidates in GAPS section

**DESIGN PATTERNS section MUST include:**
- Architecture pattern (MVC, Layered, Pipeline, etc.) and WHY
- Code patterns in use (Factory, Strategy, etc.) and WHERE
- Anti-patterns to avoid in this module
- Boundary definitions (what's inside vs outside)

**Structure:**
- List all files in CODE STRUCTURE section
- Document each file's purpose in File Responsibilities table
- Define design patterns and boundaries
- Show data flows between files

If the IMPLEMENTATION doc exceeds ~300 lines, split into folder:
```
IMPLEMENTATION/
├── IMPLEMENTATION_Overview.md      # Entry point, high-level structure
├── IMPLEMENTATION_DataFlow.md      # How data moves
├── IMPLEMENTATION_Components.md    # Individual file details
```

## Steps:

1. Read the VIEW doc and modules.yaml
2. Read existing docs in `{issue.path}` to understand the module
3. For EACH missing doc type:
   a. Search for existing docs: `grep -r "PATTERN_TYPE" docs/`
   b. If found: update CHAIN to link to existing doc
   c. If not found: create using templates from `.mind/templates/`
4. Ensure CHAIN sections link all docs together
5. Update SYNC with what you created/linked

## Success Criteria:
- Missing doc types are present (created or linked)
- NO duplicate documentation created
- CHAIN sections link correctly

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "NO_DOCS_REF": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Add DOCS: reference to source file",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
            ],
            "prompt": f"""## Task: Add DOCS Reference

**Target:** `{issue.path}`
**Problem:** {issue.message}

## Steps:

1. Find the documentation for this code (check docs/ and modules.yaml)
2. Add a DOCS: reference near the top of the file:
   - Python: `# DOCS: docs/path/to/PATTERNS_*.md`
   - JS/TS: `// DOCS: docs/path/to/PATTERNS_*.md`
3. If no docs exist, create minimum OBJECTIVES + PATTERNS + SYNC docs first

## Success Criteria:
- Source file has DOCS: reference in header
- Reference points to existing doc file

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "UNDOC_IMPL": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Document implementation file",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Document Implementation File

**Target:** `{issue.path}`
**Problem:** {issue.message}

## CRITICAL: Find existing docs first

Before creating anything:
- `grep -r "{issue.path}" docs/` - check if already documented
- Search `docs/**/IMPLEMENTATION_*.md` for references to this file
- Check `modules.yaml` for module that should contain this file
- If documented elsewhere, update that doc instead of creating new

## IMPLEMENTATION doc structure

One IMPLEMENTATION doc per module documents ALL files in that module.
- Add this file to the existing module's IMPLEMENTATION doc
- Do NOT create a separate IMPLEMENTATION doc per file

**When adding a file, include:**
- Line count (approximate) - use `wc -l` to check
- Status: OK (<400L), WATCH (400-700L), or SPLIT (>700L)
- If WATCH/SPLIT: add extraction candidates to GAPS section

**Also update DESIGN PATTERNS if needed:**
- Does this file introduce new patterns?
- Does it affect module boundaries?

If adding makes the doc exceed ~300 lines, consider splitting into folder:
```
IMPLEMENTATION/
├── IMPLEMENTATION_Overview.md
├── IMPLEMENTATION_DataFlow.md
├── IMPLEMENTATION_Components.md
```

## Steps:

1. Search for existing documentation of this file
2. Find which module owns this code (check modules.yaml)
3. Count the file's lines: `wc -l {issue.path}`
4. Find that module's IMPLEMENTATION doc
5. Add the file with:
   - File path and brief description
   - Key functions/classes it contains
   - Line count and OK/WATCH/SPLIT status
6. If file is WATCH/SPLIT: add extraction candidates to GAPS
7. Update SYNC

## Success Criteria:
- File is referenced in the module's IMPLEMENTATION doc
- NO separate IMPLEMENTATION doc created for single file
- Bidirectional link established

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "ORPHAN_DOCS": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Fix orphan documentation",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Fix Orphan Documentation

**Target:** `{issue.path}`
**Problem:** {issue.message}

Orphan docs are documentation files not linked from any code or modules.yaml.

## Steps:

1. Read the orphan doc to understand what it documents
2. Search for related code: `grep -r "keyword" src/`
3. Decide:
   a. If code exists: add DOCS: reference to code, add to modules.yaml
   b. If code was deleted: delete the orphan doc
   c. If doc is for a concept: move to `docs/concepts/`
4. Update SYNC

## Success Criteria:
- Doc is linked from code OR modules.yaml OR moved to concepts OR deleted
- No orphan docs remain

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "DOC_DUPLICATION": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Consolidate duplicate documentation",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                issue.path,
            ],
            "prompt": f"""## Task: Consolidate Duplicate Documentation

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

Documentation duplication wastes context and creates inconsistency risk.

## Duplication Types

1. **Same file in multiple IMPLEMENTATION docs**
   - One file should be documented in exactly one IMPLEMENTATION doc
   - Remove references from all but the primary module's doc

2. **Multiple docs of same type in same folder**
   - Merge into single doc (e.g., two PATTERNS files -> one)
   - Or split into subfolders if genuinely different modules

3. **Similar content across docs**
   - If >60% similar, one is probably redundant
   - Consolidate into the canonical location
   - Remove or replace the duplicate with a reference

## Steps:

1. Read the flagged doc and its "similar" doc
2. Determine which is the canonical source:
   - More complete? More recently updated? In better location?
3. For file references: keep in the owning module's IMPLEMENTATION only
4. For content duplication:
   - Merge unique content into canonical doc
   - Replace duplicate with: `See [Doc Name](path/to/canonical.md)`
   - Or delete if truly redundant
5. Update CHAIN sections to reflect new structure
6. Update SYNC with consolidation done

## Success Criteria:
- No duplicate file references
- No redundant content
- Clear canonical location for each topic
- CHAIN links updated
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "LARGE_DOC_MODULE": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Reduce documentation module size",
            "docs_to_read": [
                ".mind/views/VIEW_Refactor_Improve_Code_Structure.md",
                issue.path,
            ],
            "prompt": f"""## Task: Reduce Documentation Size

**Target:** `{issue.path}`
**Problem:** {issue.message}
**File sizes:** {[(f['file'], f'{f["chars"]//1000}K') for f in issue.details.get('file_sizes', [])[:5]]}

## Steps:

1. Read the docs in the module folder
2. Identify content that can be reduced:
   - Old/archived sections -> move to dated archive file
   - Duplicate information -> consolidate
   - Verbose explanations -> make concise
   - Implementation details that changed -> update or remove
3. For large individual files (~300+ lines), split into a folder:
   - Any doc type can become a folder when too large
   - Example: `ALGORITHM.md` -> `ALGORITHM/ALGORITHM_Overview.md`, `ALGORITHM_Details.md`
   - Keep an overview file as entry point
4. Update CHAIN sections after any splits
5. Update SYNC with what was reorganized

## Splitting pattern for any doc type:
```
DOC_TYPE.md (too large) -> DOC_TYPE/
├── DOC_TYPE_Overview.md      # Entry point, high-level
├── DOC_TYPE_Part1.md         # Focused section
├── DOC_TYPE_Part2.md         # Another section
```

## Archiving pattern:
- Create `{issue.path}/archive/SYNC_archive_2024-12.md` for old content
- Keep only current state in main docs

## Success Criteria:
- Total chars under 50K
- Individual files under ~300 lines
- Content is current and relevant
- No duplicate information
- CHAIN links still work

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "DOC_GAPS": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Complete gaps from previous agent",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
                issue.path,
            ],
            "prompt": f"""## Task: Complete Gaps From Previous Agent

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Gaps to complete:**
{chr(10).join(f"- [ ] {g}" for g in issue.details.get('gaps', []))}

A previous work agent couldn't complete all work and left these tasks in a GAPS section.

## Steps:

1. Read the SYNC file to understand context
2. For each gap item:
   - Understand what was intended
   - Complete the task (create doc, implement feature, fix issue, etc.)
   - Mark it [x] done in the GAPS section
3. If you complete ALL gaps:
   - Remove the ## GAPS section entirely
   - Update SYNC with summary of what was completed
4. If you can't complete some gaps:
   - Mark completed ones [x]
   - Leave incomplete ones [ ] with updated notes on blockers
   - Add your own notes about why you couldn't complete

## Success Criteria:
- All completable gaps are done and marked [x]
- Incomplete gaps have clear notes about blockers
- GAPS section removed if all done
- SYNC updated with completion summary

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "STALE_IMPL": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Update stale IMPLEMENTATION doc",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                issue.path,
            ],
            "prompt": f"""## Task: Update Stale IMPLEMENTATION Doc

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Missing files:** {issue.details.get('missing_files', [])}
**New files:** {issue.details.get('new_files', [])}

The IMPLEMENTATION doc doesn't match the actual files in the codebase.

## Steps:

1. Read the current IMPLEMENTATION doc
2. Compare against actual files in the module
3. For missing files (referenced but don't exist):
   - If renamed: update the path
   - If deleted: remove from doc
4. For new files (exist but not documented):
   - Add to CODE STRUCTURE section
   - Add to File Responsibilities table
5. Update data flow diagrams if needed
6. Update SYNC

## Success Criteria:
- All files in doc exist in codebase
- All files in codebase are in doc
- File descriptions are accurate

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },
    }

    return instructions.get(issue.task_type, {})
