"""Helpers for common NIfTI filename handling."""

from __future__ import annotations

from pathlib import Path

_NIFTI_EXTENSIONS = (".nii.gz", ".nii")


def split_nifti_extension(path: str | Path) -> tuple[Path, str]:
    """Split a path into its stem and NIfTI extension.

    Returns the original path with the NIfTI suffix removed plus the matched
    extension. If no NIfTI extension is present, the extension value is empty.
    """

    raw_path = Path(path)
    raw_value = str(raw_path)

    for extension in _NIFTI_EXTENSIONS:
        if raw_value.endswith(extension):
            stem = raw_value[: -len(extension)]
            return Path(stem), extension

    return raw_path, ""


def is_nifti_path(path: str | Path) -> bool:
    """Return ``True`` when the path ends with a NIfTI file extension."""

    return split_nifti_extension(path)[1] != ""

