"""Main entry point for the fueltracker package.

Run with: `python -m fueltracker`.
"""

from . import __version__


def main() -> None:
    """Display a simple banner with version information."""
    lines = [
        "[FIRE] Fuel Integrity & Reconciliation Engine",
        f"Version: {__version__}",
        "Formerly: " "Fuel Tracker" " (no functional changes in this release)",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
