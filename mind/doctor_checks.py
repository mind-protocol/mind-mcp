"""
Doctor check aggregator. Re-exports each health check so clients can import a single namespace.

DOCS: docs/protocol/doctor/IMPLEMENTATION_Project_Health_Doctor.md
"""

from .doctor_checks_content import (
    doctor_check_doc_duplication,
    doctor_check_long_strings,
    doctor_check_new_undoc_code,
    doctor_check_recent_log_errors,
    doctor_check_special_markers,
)
from .doctor_checks_core import (
    doctor_check_monolith,
    doctor_check_stale_sync,
    doctor_check_undocumented,
)
from .doctor_checks_docs import (
    doctor_check_doc_template_drift,
    doctor_check_docs_not_ingested,
    doctor_check_incomplete_chain,
    doctor_check_large_doc_module,
    doctor_check_nonstandard_doc_type,
    doctor_check_orphan_docs,
    doctor_check_placeholder_docs,
    doctor_check_sections_without_node_id,
    doctor_check_stale_impl,
    doctor_check_validation_behaviors_list,
)
from .doctor_checks_metadata import (
    doctor_check_missing_tests,
    doctor_check_yaml_drift,
)
from .doctor_checks_naming import doctor_check_naming_conventions
from .doctor_checks_prompt_integrity import (
    doctor_check_code_doc_delta_coupling,
    doctor_check_doc_link_integrity,
    doctor_check_prompt_checklist,
    doctor_check_prompt_doc_reference,
    doctor_check_prompt_view_table,
)
from .doctor_checks_reference import (
    doctor_check_broken_impl_links,
    doctor_check_no_docs_ref,
)
from .doctor_checks_quality import (
    doctor_check_hardcoded_secrets,
    doctor_check_magic_values,
)
from .doctor_checks_stub import (
    doctor_check_incomplete_impl,
    doctor_check_stub_impl,
    doctor_check_undoc_impl,
)
from .doctor_checks_sync import (
    doctor_check_conflicts,
    doctor_check_doc_gaps,
    doctor_check_suggestions,
)
from .doctor_checks_membrane import (
    doctor_check_membrane_health,
    doctor_check_membrane_protocols,
)

__all__ = [
    "doctor_check_monolith",
    "doctor_check_undocumented",
    "doctor_check_stale_sync",
    "doctor_check_placeholder_docs",
    "doctor_check_no_docs_ref",
    "doctor_check_broken_impl_links",
    "doctor_check_stub_impl",
    "doctor_check_incomplete_impl",
    "doctor_check_undoc_impl",
    "doctor_check_yaml_drift",
    "doctor_check_large_doc_module",
    "doctor_check_incomplete_chain",
    "doctor_check_doc_template_drift",
    "doctor_check_validation_behaviors_list",
    "doctor_check_nonstandard_doc_type",
    "doctor_check_missing_tests",
    "doctor_check_orphan_docs",
    "doctor_check_stale_impl",
    "doctor_check_prompt_doc_reference",
    "doctor_check_prompt_view_table",
    "doctor_check_prompt_checklist",
    "doctor_check_doc_link_integrity",
    "doctor_check_code_doc_delta_coupling",
    "doctor_check_magic_values",
    "doctor_check_hardcoded_secrets",
    "doctor_check_naming_conventions",
    "doctor_check_conflicts",
    "doctor_check_doc_gaps",
    "doctor_check_suggestions",
    "doctor_check_doc_duplication",
    "doctor_check_long_strings",
    "doctor_check_new_undoc_code",
    "doctor_check_recent_log_errors",
    "doctor_check_special_markers",
    "doctor_check_membrane_health",
    "doctor_check_membrane_protocols",
]
