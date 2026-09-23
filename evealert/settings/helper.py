"""Helper utilities for EVE Alert application.

Provides resource path resolution and constants.
"""

import sys
from pathlib import Path

# Path to application icon
ICON = "img/eve.ico"

# Absolute path to the evealert package root
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Directory containing the running executable/script (writable location)
EXEC_ROOT = Path(sys.argv[0]).resolve().parent


def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource file.

    In development, resources are loaded from the evealert package.
    In a PyInstaller build, bundled read-only resources are loaded from
    sys._MEIPASS while writable settings.json stays next to the executable.

    Args:
        relative_path: Path like "sound/alarm.wav" or "img/icon.png"

    Returns:
        Absolute path to the resource file
    """
    if not relative_path:
        raise ValueError("relative_path must be provided")

    relative = Path(relative_path)

    if relative.is_absolute():
        return str(relative)

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent

        # Keep user-editable settings outside the one-file bundle.
        if relative == Path("settings.json"):
            return str((exe_dir / relative).resolve())

        bundle_root = Path(getattr(sys, "_MEIPASS", exe_dir))

        # Support both root-level bundled resources and the current
        # GitHub Actions layout (evealert/img, evealert/sound, ...).
        candidates = (
            bundle_root / relative,
            bundle_root / "evealert" / relative,
            exe_dir / relative,
        )
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())

        return str((bundle_root / relative).resolve())

    # Development mode: strip 'evealert/' prefix and use PACKAGE_ROOT.
    relative_stripped = relative
    if relative.parts and relative.parts[0].lower() == "evealert":
        relative_stripped = Path(*relative.parts[1:])

    resource_path = (PACKAGE_ROOT / relative_stripped).resolve()

    # Fallback to EXEC_ROOT if not found in PACKAGE_ROOT.
    if not resource_path.exists():
        resource_path = (EXEC_ROOT / relative_stripped).resolve()

    return str(resource_path)
