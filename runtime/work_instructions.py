# DOCS: docs/cli/core/PATTERNS_Why_CLI_Over_Copy.md
"""
Issue instructions for mind work agents.

This module contains code/test/config work instructions.
Documentation-related instructions are in work_instructions_docs.py.
"""

from pathlib import Path
from typing import Any, Dict

# Import DoctorIssue type for type hints
from .doctor import DoctorIssue
from .work_instructions_docs import get_doc_instructions


def get_issue_instructions(issue: DoctorIssue, target_dir: Path) -> Dict[str, Any]:
    """Generate specific instructions for each issue type."""

    instructions = {
        "MONOLITH": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Split a monolith file into smaller modules",
            "docs_to_read": [
                ".mind/views/VIEW_Refactor_Improve_Code_Structure.md",
                ".mind/PRINCIPLES.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Split Monolith File

**Target:** `{issue.path}`
**Problem:** {issue.message}
{f"**Suggestion:** {issue.suggestion}" if issue.suggestion else ""}

## Steps:

1. Read the VIEW and PRINCIPLES docs listed above
2. Read the target file to understand its structure
3. Find the IMPLEMENTATION doc for this module (check modules.yaml for docs path)
4. Identify the largest function/class mentioned in the suggestion
5. Create a new file for the extracted code (e.g., `{Path(issue.path).stem}_utils.py`)
6. Move the function/class to the new file
7. Update imports in the original file
8. Run any existing tests to verify nothing broke

## MANDATORY: Update Documentation

**Refactoring is NOT complete without documentation updates.**

9. Update IMPLEMENTATION doc:
   - Add new file to CODE STRUCTURE tree
   - Add new file to File Responsibilities table
   - Count lines: `wc -l` for both original and new file
   - Update Status column (OK/WATCH/SPLIT) for both files
   - Update internal dependencies diagram

10. Update modules.yaml:
    - Add new file to appropriate section (subsystems or internal)
    - Add note about extraction if file still needs splitting

11. Update SYNC with:
    - Files extracted and their new names
    - Line counts before/after
    - What still needs extraction (if any)

## Success Criteria:
- Original file is shorter
- New file created with extracted code
- Code still works (tests pass if they exist)
- Imports are correct
- **IMPLEMENTATION doc updated with new file**
- **modules.yaml updated with new file**
- **Line counts recorded in File Responsibilities**
- SYNC updated with extraction summary

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [".mind/state/SYNC_Project_State.md"],
        },

        "STALE_SYNC": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Update stale SYNC file",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
                issue.path,  # The stale SYNC file itself
            ],
            "prompt": f"""## Task: Update Stale SYNC File

**Target:** `{issue.path}`
**Problem:** {issue.message}

## Steps:

1. Read the VIEW doc and the current SYNC file
2. Read the code/docs that this SYNC file describes
3. Compare current state with what SYNC says
4. Update SYNC to reflect reality:
   - Update LAST_UPDATED to today's date
   - Update STATUS if needed
   - Update CURRENT STATE section
   - Remove outdated information
   - Add any new developments
5. If the SYNC is for a module, also check if the module's code has changed

## Success Criteria:
- LAST_UPDATED is today's date
- Content reflects current reality
- No outdated information

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "BROKEN_IMPL_LINK": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Fix broken file references in IMPLEMENTATION doc",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                issue.path,
            ],
            "prompt": f"""## Task: Fix Broken Implementation Links

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Missing files:** {issue.details.get('missing_files', [])}

## Steps:

1. Read the IMPLEMENTATION doc
2. For each missing file reference:
   - Search the codebase for the actual file location
   - If file was moved: update the path in the doc
   - If file was renamed: update the reference
   - If file was deleted: remove the reference or note it's deprecated
3. Verify all remaining file references point to existing files
4. Update SYNC with what you fixed

## Success Criteria:
- All file references in IMPLEMENTATION doc point to existing files
- No broken links remain
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "STUB_IMPL": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Implement stub functions",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
                ".mind/PRINCIPLES.md",
            ],
            "prompt": f"""## Task: Implement Stub Functions

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Stub indicators:** {issue.details.get('stubs', [])}

## Steps:

1. Read the file and identify all stub patterns (TODO, NotImplementedError, pass, etc.)
2. For each stub function:
   - Understand what it should do from context (docstring, function name, callers)
   - Implement the actual logic
   - Remove the stub marker
3. If you cannot implement (missing requirements), document why in SYNC
4. Run any existing tests to verify implementations work

## Success Criteria:
- Stub functions have real implementations
- No NotImplementedError, TODO in function bodies
- Tests pass (if they exist)
- SYNC updated with what was implemented

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [".mind/state/SYNC_Project_State.md"],
        },

        "INCOMPLETE_IMPL": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Complete empty functions",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
            ],
            "prompt": f"""## Task: Complete Empty Functions

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Empty functions:** {[f['name'] for f in issue.details.get('empty_functions', [])]}

## Steps:

1. Read the file and find empty functions (only have pass, docstring, or trivial body)
2. For each empty function:
   - Understand its purpose from name, docstring, and how it's called
   - Implement the logic
3. If a function should remain empty (abstract base, protocol), add a comment explaining why
4. Update SYNC with implementations added

## Success Criteria:
- Empty functions have real implementations
- Or have comments explaining why they're intentionally empty
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [".mind/state/SYNC_Project_State.md"],
        },

        "YAML_DRIFT": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Fix modules.yaml drift",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Fix YAML Drift

**Target:** `{issue.path}`
**Module:** {issue.details.get('module', 'unknown')}
**Issues:** {issue.details.get('issues', [])}

## Steps:

1. Read modules.yaml and find the module entry
2. For each drift issue:
   - **Path not found**: Search for where the code/docs actually are, update the path
   - **Dependency not defined**: Either add the missing module or remove the dependency
3. If the module was completely removed, delete its entry from modules.yaml
4. Verify all paths now exist
5. Update SYNC with what was fixed

## Success Criteria:
- All code/docs/tests paths in the module entry point to existing directories
- All dependencies reference defined modules
- modules.yaml reflects reality

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": ["modules.yaml"],
        },

        "MISSING_TESTS": {
            "view": "VIEW_Health_Define_Health_Checks_And_Verify.md",
            "description": "Add tests for module",
            "docs_to_read": [
                ".mind/views/VIEW_Health_Define_Health_Checks_And_Verify.md",
                "modules.yaml",
            ],
            "prompt": f"""## Task: Add Tests for Module

**Target:** `{issue.path}`
**Problem:** {issue.message}

## Steps:

1. Read modules.yaml to understand the module structure
2. Read the source code to understand what needs testing
3. Check for existing test patterns in the project (pytest, unittest, etc.)
4. Create test file(s) following existing conventions:
   - If `tests/` exists, put tests there
   - Mirror the source structure (e.g., `src/foo/bar.py` → `tests/foo/test_bar.py`)
5. Write tests for key functions/classes
6. Run tests to verify they pass
7. Update modules.yaml with tests path if needed
8. Update SYNC

## Success Criteria:
- Test file(s) created following project conventions
- Tests pass when run
- Key functionality is covered
- modules.yaml updated with tests path

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": ["modules.yaml"],
        },

        "ESCALATION": {
            "view": "VIEW_Specify_Design_Vision_And_Architecture.md",
            "description": "Resolve conflict with human decision",
            "docs_to_read": [
                ".mind/views/VIEW_Specify_Design_Vision_And_Architecture.md",
                issue.path,
            ],
            "prompt": f"""## Task: Implement Conflict Resolution

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Conflicts:** {issue.details.get('conflicts', [])}

The human has made decisions about these conflicts. Implement them.

## Human Decisions:
{{escalation_decisions}}

## Steps:

1. Read the SYNC file to understand each conflict
2. For each decision:
   - Update the conflicting docs/code to match the decision
   - Change ESCALATION to DECISION in the CONFLICTS section
   - Add "Resolved:" note explaining what was changed
3. Verify consistency - both sources should now agree
4. If CONFLICTS section is now all DECISION items, consider removing it
5. Update SYNC

## Success Criteria:
- All decided conflicts are resolved (docs/code updated)
- ESCALATION items converted to DECISION items
- No contradictions remain for resolved items

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "SUGGESTION": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Implement agent suggestion",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
                issue.path,
            ],
            "prompt": f"""## Task: Implement Agent Suggestion

**Source:** `{issue.path}`
**Suggestion:** {issue.details.get('suggestion', issue.message)}

A previous agent made this suggestion for improvement. The user has accepted it.

## Steps:

1. Read the source SYNC file to understand context
2. Understand what the suggestion is asking for
3. Implement the improvement:
   - If it's a code change: modify the code
   - If it's a refactoring: restructure as suggested
   - If it's adding something: create it
4. Mark the suggestion as done in the SYNC file:
   - Change `[ ]` to `[x]` for this suggestion
5. Update SYNC with what you implemented
6. If implementation reveals more work needed, add new suggestions

## Success Criteria:
- Suggestion is implemented
- Suggestion marked [x] in source SYNC
- SYNC updated with implementation notes
- Any follow-up suggestions added

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "NEW_UNDOC_CODE": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Update documentation for changed code",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
                issue.details.get('impl_doc', issue.path),
            ],
            "prompt": f"""## Task: Update Documentation for Changed Code

**Source file:** `{issue.path}`
**Problem:** {issue.message}
**IMPLEMENTATION doc:** `{issue.details.get('impl_doc', 'unknown')}`

The source code has been modified more recently than its documentation.

## Steps:

1. Read the source file to understand what changed
2. Count lines: `wc -l {issue.path}` - check if size status changed
3. Read the IMPLEMENTATION doc to see what's documented
4. Compare and identify gaps:
   - New functions/classes not documented
   - Changed signatures not reflected
   - Removed code still documented
   - File size changed (update Lines/Status columns)
5. Update the IMPLEMENTATION doc:
   - Add new code to FILE RESPONSIBILITIES
   - Update function signatures
   - Update line count and OK/WATCH/SPLIT status
   - Remove references to deleted code
   - Update data flow if changed
6. If file is now WATCH/SPLIT: add extraction candidates to GAPS
7. Update SYNC with what was updated

## Success Criteria:
- IMPLEMENTATION doc reflects current code
- New functions/classes are documented
- Line count and status are current
- No stale references to deleted code
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.details.get('impl_doc', '')],
        },

        "COMPONENT_NO_STORIES": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Add Storybook stories for component",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
            ],
            "prompt": f"""## Task: Add Storybook Stories for Component

**Component:** `{issue.path}`
**Problem:** {issue.message}

Frontend components should have Storybook stories for visual documentation and testing.

## Steps:

1. Read the component file to understand:
   - What props it accepts
   - What variants/states it has
   - What it renders
2. Create a stories file (e.g., `{Path(issue.path).stem}.stories.tsx`)
3. Add stories covering:
   - Default state
   - Key prop variations
   - Edge cases (loading, error, empty states)
   - Interactive states if applicable
4. Test stories render correctly in Storybook
5. Update SYNC

## Story Template:
```tsx
import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {Path(issue.path).stem} }} from './{Path(issue.path).stem}';

const meta: Meta<typeof {Path(issue.path).stem}> = {{
  component: {Path(issue.path).stem},
  title: 'Components/{Path(issue.path).stem}',
}};
export default meta;

type Story = StoryObj<typeof {Path(issue.path).stem}>;

export const Default: Story = {{
  args: {{}},
}};
```

## Success Criteria:
- Stories file exists next to component
- Default story renders component
- Key variants are covered
- Stories work in Storybook

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "HOOK_UNDOC": {
            "view": "VIEW_Document_Create_Module_Documentation.md",
            "description": "Document custom React hook",
            "docs_to_read": [
                ".mind/views/VIEW_Document_Create_Module_Documentation.md",
            ],
            "prompt": f"""## Task: Document Custom Hook

**Hook:** `{issue.path}`
**Problem:** {issue.message}

Custom React hooks should have JSDoc documentation explaining their purpose and usage.

## Steps:

1. Read the hook file to understand:
   - What it does
   - What parameters it takes
   - What it returns
   - Any side effects
2. Add JSDoc comment above the hook:
```tsx
/**
 * Brief description of what this hook does.
 *
 * @param param1 - Description of first parameter
 * @param param2 - Description of second parameter
 * @returns Description of return value
 *
 * @example
 * ```tsx
 * const {{ data, loading }} = useMyHook(arg1, arg2);
 * ```
 */
```
3. Add `// DOCS:` reference if module docs exist
4. Update SYNC

## Success Criteria:
- Hook has JSDoc with description
- Parameters documented with @param
- Return value documented with @returns
- Usage example provided
- DOCS: reference if applicable

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "HARDCODED_SECRET": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Remove hardcoded secret from code",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
                ".mind/PRINCIPLES.md",
            ],
            "prompt": f"""## Task: Remove Hardcoded Secret (SECURITY CRITICAL)

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

This is a CRITICAL security issue. Secrets must never be in source code.

## Steps:

1. Read the file and locate the secret
2. Determine where the secret should come from:
   - Environment variable (most common)
   - Secrets manager (AWS Secrets Manager, Vault, etc.)
   - Config file that's in .gitignore
3. Replace the hardcoded value with environment variable lookup:
   - Python: `os.environ.get('SECRET_NAME')` or `os.getenv('SECRET_NAME')`
   - Node.js: `process.env.SECRET_NAME`
4. Add the secret name to a `.env.example` file with placeholder value
5. Ensure `.env` is in `.gitignore`
6. Update any documentation about required environment variables
7. Update SYNC with security fix

## Success Criteria:
- No hardcoded secret in code
- Secret loaded from environment variable
- `.env.example` updated
- `.gitignore` includes `.env`
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [".mind/state/SYNC_Project_State.md"],
        },

        "HARDCODED_CONFIG": {
            "view": "VIEW_Implement_Write_Or_Modify_Code.md",
            "description": "Externalize hardcoded configuration",
            "docs_to_read": [
                ".mind/views/VIEW_Implement_Write_Or_Modify_Code.md",
            ],
            "prompt": f"""## Task: Externalize Hardcoded Configuration

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

Configuration values like URLs, ports, and IPs should not be hardcoded.

## Steps:

1. Read the file and identify the hardcoded config value
2. Determine the appropriate configuration method:
   - Environment variable for runtime config
   - Config file (config.yaml, settings.py) for app config
   - Constants file for truly static values
3. Extract the value:
   - Create or update config file if needed
   - Replace hardcoded value with config lookup
4. Add default value handling for development
5. Update SYNC with changes

## Success Criteria:
- Hardcoded value replaced with config lookup
- Config file or env var documented
- Default values for development
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "MAGIC_VALUES": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Extract magic numbers to constants",
            "docs_to_read": [
                ".mind/views/VIEW_Refactor_Improve_Code_Structure.md",
            ],
            "prompt": f"""## Task: Extract Magic Numbers to Constants

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Examples:** {issue.details.get('examples', [])}

Magic numbers make code hard to understand and maintain.

## Steps:

1. Read the file and identify magic numbers
2. For each magic number:
   - Determine what it represents
   - Create a named constant with descriptive name
   - Replace the number with the constant
3. Place constants appropriately:
   - Module-level constants at top of file
   - Or in a dedicated constants.py if shared across files
4. Use UPPER_CASE naming convention
5. Add brief comment explaining each constant if not obvious

## Example:
```python
# Before
if timeout > 300:
    raise TimeoutError()

# After
REQUEST_TIMEOUT_SECONDS = 300  # Maximum time to wait for API response

if timeout > REQUEST_TIMEOUT_SECONDS:
    raise TimeoutError()
```

## Success Criteria:
- Magic numbers replaced with named constants
- Constants have descriptive names
- Code behavior unchanged
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "LONG_PROMPT": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Move prompts to prompts/ directory",
            "docs_to_read": [
                ".mind/views/VIEW_Refactor_Improve_Code_Structure.md",
            ],
            "prompt": f"""## Task: Externalize Long Prompts

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

Long prompt strings embedded in code are hard to edit and review.

## Steps:

1. Read the file and identify the long prompt string(s)
2. Create prompts/ directory if it doesn't exist
3. For each prompt:
   - Create a new file: `prompts/{{purpose}}.md` or `prompts/{{purpose}}.txt`
   - Move the prompt content to the file
   - Replace inline string with file read:
     ```python
     from pathlib import Path
     prompt = (Path(__file__).parent / "prompts" / "my_prompt.md").read_text()
     ```
4. If prompt has variables, use string formatting or templating
5. Update SYNC with what was externalized

## Benefits:
- Easier to edit prompts in markdown
- Better version control diffs
- Can review prompts separately from code

## Success Criteria:
- Prompts moved to prompts/ directory
- Code loads prompts from files
- Functionality unchanged
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "LONG_SQL": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Move SQL queries to .sql files",
            "docs_to_read": [
                ".mind/views/VIEW_Refactor_Improve_Code_Structure.md",
            ],
            "prompt": f"""## Task: Externalize Long SQL Queries

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

Long SQL queries embedded in code are hard to maintain and test.

## Steps:

1. Read the file and identify the long SQL query/queries
2. Create sql/ directory if it doesn't exist
3. For each query:
   - Create a new file: `sql/{{purpose}}.sql`
   - Move the SQL to the file
   - Replace inline string with file read
4. For queries with parameters, use SQL placeholders
5. Update SYNC with what was externalized

## Example:
```python
# Before
query = \"\"\"
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
\"\"\"

# After
# sql/active_users_with_orders.sql contains the query
query = (Path(__file__).parent / "sql" / "active_users_with_orders.sql").read_text()
```

## Success Criteria:
- SQL queries moved to .sql files
- Code loads SQL from files
- Parameters handled correctly
- SYNC updated

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [],
        },

        "LEGACY_MARKER": {
            "view": "VIEW_Refactor_Improve_Code_Structure.md",
            "description": "Convert legacy marker to new format",
            "docs_to_read": [
                ".mind/PRINCIPLES.md",
                issue.path,
            ],
            "prompt": f"""## Task: Convert Legacy Marker Format

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Details:** {issue.details}

The file contains legacy marker formats that should be converted to the new @mind: format.

## Marker Format Reference (from PRINCIPLES.md):
- `@mind:todo` - Actionable tasks that need doing
- `@mind:proposition` - Improvement ideas, suggestions for features/refactors
- `@mind:escalation` - Blockers needing human decision, missing requirements

## Steps:

1. Read the file to find all legacy markers
2. Convert each pattern:
   - `## GAPS / IDEAS / QUESTIONS` → `## MARKERS`
   - `- [ ] <text>` → `<!-- @mind:todo <text> -->`
   - `- IDEA: <text>` → `<!-- @mind:proposition <text> -->`
   - `- QUESTION: <text>` → `<!-- @mind:escalation <text> -->`
3. Add reference to PRINCIPLES.md if missing:
   `> See PRINCIPLES.md "Feedback Loop" section for marker format.`
4. Verify the converted markers are valid HTML comments
5. Update SYNC if significant changes were made

## Success Criteria:
- No legacy marker patterns remain
- All markers use @mind: format in HTML comments
- Section header is `## MARKERS` not `## GAPS / IDEAS / QUESTIONS`

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },

        "UNRESOLVED_QUESTION": {
            "view": "VIEW_Debug_Investigate_And_Fix_Issues.md",
            "description": "Investigate and resolve unresolved question",
            "docs_to_read": [
                ".mind/PRINCIPLES.md",
                issue.path,
            ],
            "prompt": f"""## Task: Investigate and Resolve Unresolved Question

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Questions found:** {issue.details.get('questions', [])}

The file contains questions that haven't been resolved or properly tracked.

## Decision Tree:

1. **Can you answer the question directly?**
   - YES → Answer it and remove/update the question
   - NO → Convert to proper marker (step 2)

2. **What type of question is it?**
   - Needs human decision → `<!-- @mind:escalation <question> -->`
   - Improvement idea → `<!-- @mind:proposition <question> -->`
   - Actionable task → `<!-- @mind:todo <question> -->`

## Steps:

1. Read the file and locate each question
2. For each question, determine:
   - Context: what section/topic is it about?
   - Urgency: is this blocking something?
   - Type: decision needed vs suggestion vs task
3. Take action:
   - If answerable: research/investigate and provide answer inline
   - If needs human input: convert to @mind:escalation
   - If it's an idea: convert to @mind:proposition
   - If it's a task: convert to @mind:todo
4. Update SYNC with what was resolved or converted

## Success Criteria:
- Each question is either:
  - Answered/resolved (question removed, answer documented)
  - Converted to appropriate @mind: marker
- No orphan questions remain outside MARKERS section

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
            "docs_to_update": [issue.path],
        },
    }

    # First check for doc-related instructions
    doc_instructions = get_doc_instructions(issue, target_dir)
    if doc_instructions:
        return doc_instructions

    # Then check local code/test/config instructions
    return instructions.get(issue.issue_type, {
        "view": "VIEW_Implement_Write_Or_Modify_Code.md",
        "description": f"Fix {issue.issue_type} issue",
        "docs_to_read": [".mind/PROTOCOL.md"],
        "prompt": f"""## Task: Fix Issue

**Target:** `{issue.path}`
**Problem:** {issue.message}
**Suggestion:** {issue.suggestion}

Review and fix this issue following the mind.

Report "WORK COMPLETE" when done, or "WORK FAILED: <reason>" if you cannot complete.

MANDATORY FINAL LINE:
- End your response with a standalone line: `WORK COMPLETE`
- If you fail, end with: `WORK FAILED: <reason>`

""",
        "docs_to_update": [],
    })
