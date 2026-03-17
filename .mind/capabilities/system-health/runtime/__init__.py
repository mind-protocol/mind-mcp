"""
Runtime: system-health capability

Exports health checks for capability runtime self-monitoring.
"""

from .checks import CHECKS

__all__ = ["CHECKS"]
