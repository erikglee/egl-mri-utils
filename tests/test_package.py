from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from egl_mri_utils import ensure_directory, is_nifti_path, split_nifti_extension


class PackageSmokeTests(unittest.TestCase):
    def test_split_nifti_extension_handles_nii_gz(self) -> None:
        stem, extension = split_nifti_extension("sub-01_T1w.nii.gz")
        self.assertEqual(stem, Path("sub-01_T1w"))
        self.assertEqual(extension, ".nii.gz")

    def test_is_nifti_path_detects_supported_extensions(self) -> None:
        self.assertTrue(is_nifti_path("brain.nii"))
        self.assertTrue(is_nifti_path("brain.nii.gz"))
        self.assertFalse(is_nifti_path("brain.mgz"))

    def test_ensure_directory_creates_nested_path(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "output"
            created = ensure_directory(target)
            self.assertEqual(created, target)
            self.assertTrue(created.is_dir())


if __name__ == "__main__":
    unittest.main()
