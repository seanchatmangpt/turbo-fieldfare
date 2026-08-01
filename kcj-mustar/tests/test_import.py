"""Test kcj-mustar."""

import kcj_mustar


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(kcj_mustar.__name__, str)
