"""Utilities for lightweight neuroimaging workflows."""

from .nifti import is_nifti_path, split_nifti_extension
from .paths import ensure_directory

__all__ = [
    "ensure_directory",
    "is_nifti_path",
    "split_nifti_extension",
]

__version__ = "0.1.0"

