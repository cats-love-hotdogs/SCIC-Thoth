"""
views package - Các màn hình giao diện trực quan cho ICSC CLI.
"""

from . import base_view
from . import home_view
from . import exam_view
from . import explorer_view
from . import ingestion_view
from . import history_view
from . import tags_view
from . import diagnostics_view

__all__ = [
    "base_view",
    "home_view",
    "exam_view",
    "explorer_view",
    "ingestion_view",
    "history_view",
    "tags_view",
    "diagnostics_view",
]
