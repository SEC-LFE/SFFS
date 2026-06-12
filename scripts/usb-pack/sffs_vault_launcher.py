r"""
sffs_vault_launcher.py — Windowed entry point for the split-partition SFFS USB.

Layout it targets:
  P1 (visible)  : this SFFS.exe only.
  P2 (SFFS_VAULT, hidden): python\ + code1..3\ + main-code\ + sffs_data\ + .sffs_vault

Behaviour:
  * Find the vault drive (env SFFS_VAULT_DRIVE, or any drive with a .sffs_vault
    marker + python\pythonw.exe).
  * Launch the app from the vault via the windowless interpreter through
    code2\windows_job_wrapper.py (Windows Job Object isolation), so there is no
    console window and no flash.
  * Fall back to running next to the exe (single-folder portable layout).
  * Show a message box if no install is found.

Build (onefile, windowed, with logo):
    pyinstaller --onefile --windowed --icon sffs_logo.ico --name SFFS sffs_vault_launcher.py
"""

from __future__ import annotations

import ctypes
import os
import string
import subprocess
import sys
from pathlib import Path

VAULT_MARKER = ".sffs_vault"


def _exe_dir() -> Path:
    base = sys.executable if getattr(sys, "frozen", False) else __file__
    return Path(base).resolve().parent


def _is_sffs_root(root: Path) -> bool:
    return (root / "python" / "pythonw.exe").exists() and (
        root / "code2" / "windows_job_wrapper.py"
    ).exists()


def _find_vault() -> "Path | None":
    # 1. Explicit override.
    env = os.environ.get("SFFS_VAULT_DRIVE", "").strip().rstrip(":\\/").upper()
    order = [env] if (len(env) == 1 and env.isalpha()) else []
    order += [c for c in string.ascii_uppercase if c != env]

    for lt in order:
        root = Path(f"{lt}:\\")
        try:
            if (root / VAULT_MARKER).exists() and _is_sffs_root(root):
                return root
        except OSError:
            continue
    return None


def _msgbox(text: str, title: str = "SFFS") -> None:
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
    except Exception:
        sys.stderr.write(f"[{title}] {text}\n")


def main() -> int:
    if os.name != "nt":
        _msgbox("This launcher is for Windows. On Linux run sffs.sh.")
        return 1

    root = _find_vault()
    if root is None:
        local = _exe_dir()
        if _is_sffs_root(local):
            root = local
    if root is None:
        _msgbox(
            "SFFS installation not found.\n\n"
            "Looked for a drive with a .sffs_vault marker (the SFFS_VAULT "
            "partition) and for python\\ + code2\\ next to this program.\n\n"
            "Re-run the SFFS USB installer."
        )
        return 1

    pyw = root / "python" / "pythonw.exe"
    wrapper = root / "code2" / "windows_job_wrapper.py"

    env = os.environ.copy()
    env["SFFS_ROOT"] = str(root)
    env["PYTHONPATH"] = os.pathsep.join(
        str(root / d) for d in ("code1", "code2", "code3", "main-code")
    ) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        return subprocess.run(
            [str(pyw), str(wrapper), *sys.argv[1:]],
            cwd=str(root),
            env=env,
        ).returncode
    except Exception as e:  # noqa: BLE001
        _msgbox(f"Failed to launch SFFS:\n{e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
