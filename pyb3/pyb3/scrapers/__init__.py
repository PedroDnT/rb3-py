"""Specialized scrapers for B3 data.

This module provides specialized scrapers for different types of B3 data.
"""

from .cotahist import cotahist_get, cotahist_filter_equity
from .futures import futures_get
from .yc import yc_brl_get
from .indexes import indexes_get, indexes_composition_get