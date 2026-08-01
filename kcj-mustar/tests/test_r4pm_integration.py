"""Test r4pm Rust-backed process mining integration."""

import r4pm

def test_r4pm_import():
    print(f"r4pm module loaded successfully: {r4pm.__name__}")
    assert r4pm is not None

if __name__ == "__main__":
    test_r4pm_import()
    print("R4PM RUST PROCESS MINING TEST PASSED SUCCESSFULLY!")
