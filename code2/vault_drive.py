"""
vault_drive.py — No-admin "hidden vault drive" support (Student 2: runtime/system).

Model (all without administrator privileges):
  * A second USB partition (or any volume) auto-mounts with a drive letter, e.g. X:.
  * SFFS hides that letter from Explorer/This-PC via the per-user ``NoDrives``
    policy (HKCU) — the icon disappears, but the drive stays reachable by full
    path (X:\\...), so SFFS reads/writes it normally.
  * Confidentiality is NOT provided by the hiding (that is cosmetic) — it comes
    from SFFS's existing AES encryption of everything stored on the volume.

Admin-mode upgrade (out of scope here): a file-system minifilter driver that
permits access only to the Authenticode-signed SFFS binary. That requires admin
to load a kernel driver; this module is the no-admin equivalent.

Public API:
  detect_vault_root()           -> Path | None     # for f13 drive detection
  find_vault_letter()           -> str | None       # single letter, e.g. "X"
  hide_drive(letter)            -> bool
  show_drive(letter)            -> bool
  is_drive_hidden(letter)       -> bool
  refresh_explorer()            -> None              # make the change show live
  restore(letter)               -> bool             # alias of show_drive
"""

from __future__ import annotations

import os
import string
import sys
from pathlib import Path

# Volume label / marker that identifies the SFFS vault partition.
VAULT_LABEL = "SFFS_VAULT"
VAULT_MARKER = ".sffs_vault"

# Per-user policy key — writable by a standard user, no admin needed.
_NODRIVES_KEY = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
_NODRIVES_VAL = "NoDrives"

_IS_WINDOWS = os.name == "nt"


# ── Drive-letter bit math ────────────────────────────────────────────────────

def _letter(letter: str) -> str:
    letter = letter.strip().rstrip(":\\/").upper()
    if len(letter) != 1 or letter not in string.ascii_uppercase:
        raise ValueError(f"Not a drive letter: {letter!r}")
    return letter


def nodrives_mask(letter: str) -> int:
    """Bit for a drive letter in the NoDrives bitmask (A=bit0 … Z=bit25)."""
    return 1 << (ord(_letter(letter)) - ord("A"))


# ── NoDrives registry (HKCU — no admin) ──────────────────────────────────────

def _read_nodrives() -> int:
    if not _IS_WINDOWS:
        return 0
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _NODRIVES_KEY) as k:
            val, _ = winreg.QueryValueEx(k, _NODRIVES_VAL)
            return int(val)
    except FileNotFoundError:
        return 0
    except OSError:
        return 0


def _write_nodrives(mask: int) -> None:
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _NODRIVES_KEY) as k:
        if mask == 0:
            try:
                winreg.DeleteValue(k, _NODRIVES_VAL)
            except FileNotFoundError:
                pass
        else:
            winreg.SetValueEx(k, _NODRIVES_VAL, 0, winreg.REG_DWORD, mask & 0x03FFFFFF)


def is_drive_hidden(letter: str) -> bool:
    return bool(_read_nodrives() & nodrives_mask(letter))


def hide_drive(letter: str) -> bool:
    """Hide a drive letter from Explorer for the current user. No admin needed."""
    if not _IS_WINDOWS:
        return False
    try:
        _write_nodrives(_read_nodrives() | nodrives_mask(letter))
        refresh_explorer()
        return True
    except OSError:
        return False


def show_drive(letter: str) -> bool:
    """Un-hide a drive letter (clear its NoDrives bit). No admin needed."""
    if not _IS_WINDOWS:
        return False
    try:
        _write_nodrives(_read_nodrives() & ~nodrives_mask(letter))
        refresh_explorer()
        return True
    except OSError:
        return False


restore = show_drive


# ── Folder hiding via +h +s attributes (reliable, no admin, no policy key) ───
# NoDrives (above) needs the HKCU Policies subtree, which is ACL-locked on many
# managed/lab machines. Marking the vault FOLDER Hidden+System always works for
# the file owner with no admin, hides it from Explorer's default view, and keeps
# it fully reachable by full path. This is the primary hide mechanism.

_FILE_ATTRIBUTE_HIDDEN = 0x02
_FILE_ATTRIBUTE_SYSTEM = 0x04
_FILE_ATTRIBUTE_NORMAL = 0x80


def _get_attrs(path: Path) -> int:
    import ctypes
    a = ctypes.windll.kernel32.GetFileAttributesW(str(path))
    return int(a) if a != 0xFFFFFFFF else 0


def is_path_hidden(path: Path) -> bool:
    if not _IS_WINDOWS:
        return False
    return bool(_get_attrs(path) & _FILE_ATTRIBUTE_HIDDEN)


def hide_path(path: Path) -> bool:
    """Mark a folder/file Hidden+System (invisible in Explorer). No admin."""
    if not _IS_WINDOWS or not Path(path).exists():
        return False
    try:
        import ctypes
        cur = _get_attrs(path)
        ok = ctypes.windll.kernel32.SetFileAttributesW(
            str(path), cur | _FILE_ATTRIBUTE_HIDDEN | _FILE_ATTRIBUTE_SYSTEM
        )
        return bool(ok)
    except Exception:
        return False


def show_path(path: Path) -> bool:
    """Clear Hidden+System so the folder/file is visible again. No admin."""
    if not _IS_WINDOWS or not Path(path).exists():
        return False
    try:
        import ctypes
        cur = _get_attrs(path)
        cur &= ~_FILE_ATTRIBUTE_HIDDEN
        cur &= ~_FILE_ATTRIBUTE_SYSTEM
        if cur == 0:
            cur = _FILE_ATTRIBUTE_NORMAL
        ok = ctypes.windll.kernel32.SetFileAttributesW(str(path), cur)
        return bool(ok)
    except Exception:
        return False


# ── High-level vault hide/show ───────────────────────────────────────────────

def hide_vault(data_dir: Path, drive_letter: "str | None" = None) -> dict:
    """Hide the vault for this session.

    Always marks the data folder Hidden+System (reliable, no admin). If the
    vault is its own drive letter, also best-effort hides that letter from
    Explorer via NoDrives (works only where the Policies key is writable).

    Returns a summary of what was applied.
    """
    folder_hidden = hide_path(Path(data_dir))
    letter_hidden = hide_drive(drive_letter) if drive_letter else False
    return {"folder_hidden": folder_hidden, "letter_hidden": letter_hidden}


def show_vault(data_dir: Path, drive_letter: "str | None" = None) -> dict:
    """Reverse hide_vault — make the folder and (if any) drive letter visible."""
    folder_shown = show_path(Path(data_dir))
    letter_shown = show_drive(drive_letter) if drive_letter else False
    return {"folder_shown": folder_shown, "letter_shown": letter_shown}


def refresh_explorer() -> None:
    """Broadcast WM_SETTINGCHANGE so open Explorer windows pick up NoDrives.

    Non-destructive (does not restart Explorer). A newly opened Explorer window
    always reflects the change; existing windows update on this broadcast or on
    next navigation.
    """
    if not _IS_WINDOWS:
        return
    try:
        import ctypes
        from ctypes import wintypes

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        res = ctypes.c_ulong()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0,
            ctypes.c_wchar_p("Policy"), SMTO_ABORTIFHUNG, 1000, ctypes.byref(res),
        )
        # Also nudge the shell to refresh its drive view.
        SHCNE_UPDATEDIR = 0x00001000
        SHCNF_FLUSH = 0x1000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_UPDATEDIR, SHCNF_FLUSH, None, None)
    except Exception:
        pass


# ── Vault discovery ──────────────────────────────────────────────────────────

def _volume_label(root: str) -> str:
    """Return the volume label for a mounted drive root like 'X:\\'. '' on error."""
    if not _IS_WINDOWS:
        return ""
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(261)
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(root), buf, 261, None, None, None, None, 0
        )
        return buf.value if ok else ""
    except Exception:
        return ""


def find_vault_letter() -> str | None:
    """Find the SFFS vault drive letter.

    Order:
      1. Env override  SFFS_VAULT_DRIVE=X   (forces a letter — used for testing)
      2. Volume label == SFFS_VAULT
      3. Marker file   <X>:\\.sffs_vault
    Returns a single uppercase letter, or None.
    """
    env = os.environ.get("SFFS_VAULT_DRIVE", "").strip()
    if env:
        try:
            lt = _letter(env)
            if Path(f"{lt}:\\").exists():
                return lt
        except ValueError:
            pass

    if not _IS_WINDOWS:
        return None

    for lt in string.ascii_uppercase:
        root = f"{lt}:\\"
        if not Path(root).exists():
            continue
        if _volume_label(root).upper() == VAULT_LABEL:
            return lt
        if (Path(root) / VAULT_MARKER).exists():
            return lt
    return None


def detect_vault_root() -> Path | None:
    """Return the vault drive root (Path like X:\\) if present, else None.

    Consumed by f13_init_drive_detection.initDriveDetection() so all SFFS data
    lands on the hidden vault volume when one is plugged in.
    """
    lt = find_vault_letter()
    return Path(f"{lt}:\\") if lt else None


if __name__ == "__main__":
    print("=== SFFS vault drive ===")
    lt = find_vault_letter()
    if not lt:
        print("No vault drive found (label SFFS_VAULT or .sffs_vault marker).")
        sys.exit(0)
    print(f"Vault drive: {lt}:  hidden={is_drive_hidden(lt)}  mask=0x{nodrives_mask(lt):08X}")
    print(f"Vault root : {detect_vault_root()}")
