"""Context loading module for pre-fetching database information.

This module provides a dispatch system for accessing service layer functions
across all business areas and utilities for loading data into agent context.
"""

from .dispatch import DISPATCH
from .loader import (
    load_category_context,
    load_full_context,
    load_order_context,
    load_product_context,
    load_user_context,
)

__all__ = [
    "DISPATCH",
    "load_user_context",
    "load_product_context",
    "load_category_context",
    "load_order_context",
    "load_full_context",
]
