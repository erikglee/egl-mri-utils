# egl-mri-utils

Small Python utility library for neuroimaging workflows.

The repo is set up with a minimal `src`-based package layout so it can grow
cleanly into an installable project later without forcing packaging decisions
right now.

## Structure

```text
egl-mri-utils/
├── pyproject.toml
├── README.md
├── src/
│   └── egl_mri_utils/
│       ├── __init__.py
│       ├── nifti.py
│       ├── paths.py
│       └── py.typed
└── tests/
    └── test_package.py
```

## Included starters

- `egl_mri_utils.nifti`: lightweight helpers for `.nii` and `.nii.gz` paths
- `egl_mri_utils.paths`: shared filesystem helpers

## Local development

Create a virtual environment, then install the package in editable mode.
This will pull in the core neuroimaging dependencies (`numpy` and `nibabel`)
plus the optional dev tools:

```bash
python -m pip install -e ".[dev]"
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Next steps

- Add new modules under `src/egl_mri_utils/` as focused utilities grow
- Keep heavier domain-specific dependencies optional unless they are broadly
  useful across the library
- Add CLI entry points later if you want a few scripts alongside the library
