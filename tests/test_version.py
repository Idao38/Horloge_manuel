from __future__ import annotations

import re
from pathlib import Path

from horloge_jdr.version import __version__


def test_version_is_semver_three_parts():
    parts = __version__.split(".")
    assert len(parts) == 3
    for p in parts:
        assert p.isdigit()


def test_version_matches_pyproject_toml():
    """Vérifie que version.py et pyproject.toml sont synchronisés."""
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    assert match is not None, "version non trouvée dans pyproject.toml"
    pyproject_version = match.group(1)
    assert __version__ == pyproject_version, (
        f"version.py ({__version__}) et pyproject.toml ({pyproject_version}) doivent être identiques"
    )
