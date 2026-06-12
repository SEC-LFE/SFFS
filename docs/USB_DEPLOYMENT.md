# SFFS USB Deployment — Split-Partition Vault Build

How the demo USB (Kingston DataTraveler 3.0) was built, what each build artifact
did, and how to reproduce it. This is the **no-admin-at-runtime, split-partition**
layout: a tiny visible launcher partition + a hidden vault partition holding the
code, bundled Python, and SFFS internal data.

## Final layout

```
Disk 2 (USB, GPT)
├── Partition 1  label SFFS        E:  25.9 GB   ← visible, launcher only
│   ├── SFFS.exe        (logo, windowed launcher — double-click to run)
│   ├── _internal/      (PyInstaller onedir support folder — keep beside SFFS.exe)
│   ├── sffs.bat        (fallback launcher, vault-aware)
│   └── sffs.sh         (Linux launcher, vault-aware)
│
└── Partition 2  label SFFS_VAULT  X:  3 GB      ← hidden vault
    ├── .sffs_vault     (discovery marker)
    ├── python/         (Python 3.13.5 embeddable + pip + all deps)
    ├── code1/ code2/ code3/ main-code/   (app source)
    ├── sffs_data/      (keys, logs, config, sandbox, auth.db — internal state)
    ├── requirements.txt
    └── .deps_installed (first-run marker)
```

User-facing encrypted `.sffs` files are saved by the user to **P1 (E:)** at runtime;
keys/logs/sandbox/auth stay on the **vault (X:)**.

## Runtime model (no admin)

- Admin is needed **once at install** (diskpart/repartition only).
- At runtime a standard user just plugs in the USB: Windows 10 v1703+/11 auto-mounts
  the second partition with a drive letter, no admin required.
- **The drive letter is assigned by the host machine, not stored on the partition.**
  It will differ between machines (X: here, F: elsewhere, etc.). Nothing depends on
  a specific letter: `code3/f13_init_drive_detection.py` calls
  `code2/vault_drive.detect_vault_root()`, which finds the vault by label
  `SFFS_VAULT` or `.sffs_vault` marker, and `SFFS.exe`/`sffs.bat` scan A–Z for the
  marker. All SFFS internal data is routed to whatever letter the vault mounted on.
- On GUI launch `main.py` hides the vault data folder via Hidden+System file
  attributes (no admin) and restores visibility on exit.

### Drive-letter visibility (NoDrives) — host-dependent, not portable
The vault contents are hidden on the **USB filesystem** (Hidden+System attributes on
`code1-3/`, `main-code/`, `python/`, `sffs_data/`, markers, `requirements.txt`), so
opening the vault drive shows an **empty** drive on any machine — portable, no admin.

Hiding the **drive letter itself** from This PC is a different thing and is *not*
portable: it requires writing the host's per-user `NoDrives` policy value
(`HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`) at runtime —
the setting lives on the host registry, never on the USB. `vault_drive.hide_drive()`
attempts this on launch:

- **Unmanaged host** → write succeeds, letter disappears from Explorer automatically.
- **GPO-managed host** (e.g. the `kyomu` lab machine) → the `Policies\Explorer`
  subtree is locked to **ReadKey** for standard users (`New-Item` → *Access denied*).
  The write fails (a safe no-op) and the **letter stays visible**. Hiding it there
  would need runtime admin, which the no-admin design rules out.

Decision: **accept the letter visible, contents hidden.** Confidentiality does not
come from hiding (that is cosmetic) — it comes from SFFS's AES encryption of
everything stored on the vault. Check a target machine with:
```powershell
try { New-Item 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer' -Force -EA Stop; 'WRITABLE -> letter hides' }
catch { 'LOCKED -> letter stays visible' }
```

## Launcher chain

`SFFS.exe` (or `sffs.bat`) → finds vault → runs
`X:\python\pythonw.exe X:\code2\windows_job_wrapper.py` → Windows Job Object
isolation → `X:\main-code\main.py` (GUI via the windowless interpreter, no console).

`windows_job_wrapper.py` self-locates the repo root from its own path, so moving
the code onto the vault required no code change.

---

## Build procedure (reproducible)

### 1. Source + portable Python onto the drive
```powershell
# copy app source
robocopy <repo>\code1 X:\code1 /E ; (code2, code3, main-code likewise)

# Python 3.13.5 embeddable -> X:\python  (3.13 chosen for PyQt6 wheel availability)
Invoke-WebRequest https://www.python.org/ftp/python/3.13.5/python-3.13.5-embed-amd64.zip -OutFile py.zip
Expand-Archive py.zip X:\python
# enable site-packages: uncomment "import site" in X:\python\python313._pth
Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
X:\python\python.exe get-pip.py
X:\python\python.exe -m pip install -r X:\main-code\requirements.txt
```

### 2. Repartition (ELEVATED, install-time only) — `sffs_vault_install.ps1`
diskpart `convert gpt` fails on an already-GPT disk; the working method uses
PowerShell Storage cmdlets:
```powershell
# SAFETY: verify disk 2 is the expected USB before clearing
Clear-Disk -Number 2 -RemoveData -RemoveOEM -Confirm:$false
# (Initialize-Disk GPT if RAW)
$p1 = New-Partition -DiskNumber 2 -Size 26500MB -DriveLetter E
Format-Volume -Partition $p1 -FileSystem NTFS -NewFileSystemLabel SFFS
$p2 = New-Partition -DiskNumber 2 -UseMaximumSize -DriveLetter X
Format-Volume -Partition $p2 -FileSystem NTFS -NewFileSystemLabel SFFS_VAULT
# restore app to E:, then move code+python to X:, drop X:\.sffs_vault marker
```
Run elevated with a UAC prompt:
```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList '-File','sffs_vault_install.ps1'
```

### 3. Split: launcher on P1, everything else on the vault
```powershell
# move code + python from E: to X: (no admin; both partitions are lettered)
robocopy E:\code1 X:\code1 /E /MOVE   # code2, code3, main-code, python likewise
# E: keeps only SFFS.exe + _internal\ + sffs.bat + sffs.sh
```

### 4. Branded launcher exe — `sffs_vault_launcher.py` → `SFFS.exe`
Source: `scripts/usb-pack/sffs_vault_launcher.py` (vault detection + spawn wrapper).
Built with real CPython 3.14 (`pythoncore-3.14-64`), not the embeddable:
```powershell
pip install pyinstaller
# Build ONEDIR (not onefile) to avoid the Defender false positive — see below.
pyinstaller --onedir --windowed --name SFFS --icon sffs_logo.ico sffs_vault_launcher.py
# deploy dist\SFFS\SFFS.exe + dist\SFFS\_internal\ to E:\
```

### Antivirus note (false positive)
PyInstaller **`--onefile`** exes are routinely flagged by Defender
(`Trojan:Win32/Wacatac.B!ml` etc.) — the self-extract-to-temp behavior, the shared
PyInstaller bootloader, and being unsigned/zero-reputation all trigger ML
heuristics. Switching to **`--onedir`** removes the self-extraction step and clears
the detection (verified clean via `Start-MpScan` on the onedir build). For a final
hand-in, also submit the exe to Microsoft as a false positive
(microsoft.com/wdsi/filesubmission). `sffs.bat` is never flagged (plain script).

---

## Build artifacts used (this session)

| Artifact | Role | Keep? |
|---|---|---|
| `sffs_build/` | PyInstaller work dir; produced `SFFS.exe` (onefile then onedir) | Regenerable from `sffs_vault_launcher.py` |
| `sffs_usb_backup/` | Snapshot of app+python; used to restore E: after the repartition wipe | Off-USB safety copy |
| `sffs_vault_install.ps1` + `.log` | Elevated repartition/restore script + run log | Record of how E:/X: were created |
| PyInstaller 6.20.0 (in pythoncore-3.14) | Build-time only dependency | Uninstallable after build |

Repo-tracked source (not disposable): `scripts/usb-pack/sffs_vault_launcher.py`,
`sffs.bat`, `sffs.sh`, `code2/vault_drive.py`.

## Verification performed
- Headless pipeline (`main.py --headless`) ran from the vault as a standard user:
  register → encrypt → decrypt → verify, exit 0; all internal data on `X:\sffs_data`,
  no `E:\sffs_data`.
- `SFFS.exe` launched the PyQt6 GUI via the vault with no console window.
- `Start-MpScan` on the onedir `SFFS.exe`: clean.
