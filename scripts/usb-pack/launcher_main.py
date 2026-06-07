r"""
launcher_main.py — SFFS Launcher Entry Point

Finds the hidden partition with .sffs_marker, mounts it to S:\,
then spawns the SFFS application from the hidden partition.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

# Add sibling directory to path for hidden_volume import
_script_dir = Path(__file__).resolve().parent
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from hidden_volume import (
    mount_hidden_volume,
    unmount_hidden_volume,
)

DRIVE_LETTER = "S"
CREATE_NO_WINDOW = 0x08000000


def _find_sffs_volume_guid() -> "str | None":
    """Find SFFS hidden partition GUID. Tries four strategies in order."""
    exe_path = Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0])

    # Strategy 0: GUID file next to the exe — fastest, set by rebuild bat
    try:
        guid_file = exe_path.parent / "sffs_volume.guid"
        if guid_file.exists():
            saved = guid_file.read_text(encoding="utf-8").strip()
            if saved and "Volume{" in saved:
                return saved if saved.endswith("\\") else saved + "\\"
    except Exception:
        pass

    # Strategy 1: PowerShell — same-disk sibling partition (no drive letter, NTFS)
    try:
        drive = exe_path.drive[0] if exe_path.drive else None
        if drive:
            cmd = (
                "$d=(Get-Partition -DriveLetter '" + drive + "').DiskNumber; "
                "Get-Partition -DiskNumber $d "
                "| Where-Object {$_.DriveLetter -eq $null} "
                "| Get-Volume "
                "| Where-Object {$_.FileSystem -eq 'NTFS'} "
                "| Select-Object -ExpandProperty UniqueId"
            )
            r = subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
                capture_output=True, text=True, timeout=15,
                creationflags=CREATE_NO_WINDOW,
            )
            uid = r.stdout.strip()
            if uid and "Volume{" in uid:
                return uid if uid.endswith("\\") else uid + "\\"
    except Exception:
        pass

    # Strategy 2: PowerShell — label scan for SFFS_DATA across all volumes
    try:
        cmd = (
            "(Get-Volume "
            "| Where-Object {$_.FileSystemLabel -eq 'SFFS_DATA'} "
            "| Select-Object -First 1 -ExpandProperty UniqueId)"
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
            capture_output=True, text=True, timeout=15,
            creationflags=CREATE_NO_WINDOW,
        )
        uid = r.stdout.strip()
        if uid and "Volume{" in uid:
            return uid if uid.endswith("\\") else uid + "\\"
    except Exception:
        pass

    # Strategy 3: ctypes fallback via hidden_volume
    try:
        from hidden_volume import find_sffs_partition
        return find_sffs_partition()
    except Exception:
        pass

    return None


def _is_admin() -> bool:
    """Check if running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _run_as_admin() -> None:
    """Relaunch this script with admin privileges."""
    exe = sys.executable
    script = sys.argv[0]
    args = sys.argv[1:]
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe, f'"{script}" {" ".join(args)}', None, 1
    )
    sys.exit(0)


def _show_error(title: str, message: str) -> None:
    """Show a Windows message box."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
    except Exception:
        print(f"[{title}] {message}", file=sys.stderr)


def _spawn_sffs(root: Path) -> int:
    """Run main.py from an SFFS install rooted at *root*. Returns child rc."""
    main_py = root / "main-code" / "main.py"
    # Prefer the windowless interpreter so no console flashes for the GUI.
    pyw = root / "python" / "pythonw.exe"
    py = root / "python" / "python.exe"
    interp = pyw if pyw.exists() else (py if py.exists() else Path(sys.executable))

    env = os.environ.copy()
    env["SFFS_ROOT"] = str(root)
    env["PYTHONPATH"] = (
        str(root / "code1") + os.pathsep
        + str(root / "code2") + os.pathsep
        + str(root / "code3") + os.pathsep
        + str(root / "main-code") + os.pathsep
        + env.get("PYTHONPATH", "")
    )
    cmd = [str(interp), str(main_py)] + sys.argv[1:]
    return subprocess.run(cmd, env=env).returncode


def _run_local(root: Path) -> "int | None":
    """Plain-copy fallback: launch SFFS straight from the exe's own drive.

    The USB installer (sffs_usb_installer.py) copies the project flat onto the
    drive — no hidden partition. In that layout the exe sits next to main-code/
    and python/, so just run it in place. Returns None if this isn't a valid
    SFFS root (so the caller can show an error)."""
    if not (root / "main-code" / "main.py").exists():
        return None
    return _spawn_sffs(root)


def main() -> int:
    exe_path = Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0])
    local_root = exe_path.parent

    # Step 1: Look for a hidden SFFS partition (sffs_usb_pack.py scheme).
    volume_guid = _find_sffs_volume_guid()
    if volume_guid and mount_hidden_volume(volume_guid, DRIVE_LETTER):
        try:
            root = Path(f"{DRIVE_LETTER}:\\")
            main_py = root / "main-code" / "main.py"
            if root.exists() and main_py.exists():
                return _spawn_sffs(root)
            _show_error("SFFS Launcher", f"Mount verification failed: {root}")
            return 1
        finally:
            unmount_hidden_volume(DRIVE_LETTER)

    # Step 2: Plain-copy fallback — run from the exe's own drive.
    rc = _run_local(local_root)
    if rc is not None:
        return rc

    # Neither scheme found a valid install.
    _show_error(
        "SFFS Launcher",
        "No SFFS installation found.\n\n"
        f"Looked for main-code\\main.py on the hidden partition and next to "
        f"this launcher ({local_root}).\n\n"
        "Re-run the SFFS USB installer.",
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
