from __future__ import annotations

from horloge_jdr.version import __version__


def test_version_is_semver_three_parts():
    parts = __version__.split(".")
    assert len(parts) == 3
    for p in parts:
        assert p.isdigit()
