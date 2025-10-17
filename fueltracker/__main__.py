"""Main entry point for the fueltracker package.

Run with: `python -m fueltracker`.
"""

from . import __version__


def main() -> None:
    """Display a simple banner with version information."""
    lines = [
        "Fuel Tracker",
        f"Version: {__version__}",
        "A compliance-focused pipeline for fuel forecasting.",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
