For future Claude. SFFS (Smart File Fortify System) is a university group project (3 students) implementing a file encryption and security system with sandbox isolation, GUI dashboard, USB deployment, and cloud sync. This note is the master project overview.

## Summary
SFFS encrypts/decrypts files using RSA-2048 + AES-256-GCM, runs files in an isolated sandbox (Windows Job Objects / Linux AppArmor), provides a PyQt6 GUI dashboard, and optionally syncs to Google Drive. It is deployed via USB with hidden volume support. The codebase spans 292 files with 3 student modules + integration layer + tests + scripts.

## God Nodes (Most Connected Abstractions)
- `SFFSCore` (75 edges) — central integration hub
- `AuditLogger` (52 edges) — cross-cutting audit concern
- `WorkerThread` (43 edges) — threading bridge between UI and crypto
- `FileManagerExplorer` (41 edges) — main UI component
- `LauncherPolicyError` (38 edges) — sandbox policy enforcement
- `SecurityError` (35 edges) — security exception handling

## Architecture (Three-Student Modular)
```
Student 1 (code1/) — Crypto: key gen, encrypt, decrypt, hash, secure key storage
Student 2 (code2/) — Security: sandbox, memory wipe, auth, process monitor, audit, emergency lock
Student 3 (code3/) — UI/Cloud: drive detection, PyQt6 dashboard, file explorer, cloud sync, config, threads
main-code/ — Integration: main.py, sffs_core.py, isolated_worker.py, provenance_table, wrap_store
tests/ — pytest suite: per-student + integration + policy + hardening
scripts/ — USB setup/verify/reset/install
```

## Key Hyperedges (Group Relationships)
- **Encrypt-Decrypt Pipeline**: f01_keygen → f06_keystore → f02_encrypt → f04_hash → f03_decrypt → f05_verify
- **Emergency Lockdown Flow**: f12_emergency_lock → f07_sandbox → f08_memory_wipe → f09_auth → f11_audit
- **Modern UI Subsystem**: sffs_ui + mouse_entropy + sandbox_viewer + cloud_sync + thread_controller + file_explorer + config_loader
- **Integration Layer**: SFFSCore + isolated_worker + provenance_table + wrap_store + entry_point

## Surprising Connections
- `isolated_worker.py` (integration layer) `--uses-->` `SecurityError` from Student 1's decryption module — IPC verification crosses module boundaries
- `f12_emergency_lock.py` `--uses-->` `AuditLogger` — emergency lockdown requires audit trail

## Communities (Top 20)
| # | Label | Nodes | Cohesion |
|---|-------|-------|----------|
| 0 | File Manager Explorer | 53 | 0.03 |
| 1 | File Decryption & Security Errors | 83 | 0.03 |
| 2 | Sandbox & Policy Enforcement | 36 | 0.03 |
| 3 | Isolated Sandbox Module | 76 | 0.03 |
| 4 | Crypto Key Gen & AES Encrypt | 49 | 0.04 |
| 5 | Mouse Entropy Pool | 17 | 0.04 |
| 6 | API Reference Docs | 48 | 0.06 |
| 7-19 | USB Installer, Security Concepts, Cloud Sync, etc. | 11-41 | 0.05-0.23 |

## Knowledge Graph Stats
- 1175 nodes, 1920 edges, 62 communities
- 84% EXTRACTED, 16% INFERRED
- Token reduction: **90x fewer tokens per query** (avg 4,369 vs 393,664 naive)

## Open Questions from Graph Analysis
- Why does `SFFSCore` bridge File Manager Explorer ↔ Decryption ↔ Sandbox ↔ Cloud Backup? (betweenness 0.171)
- Are the 46 INFERRED edges on `SFFSCore` actually correct?
- Are the 40 INFERRED edges on `AuditLogger` actually correct?

## Project Specs
- **Stack**: Python 3.11, PyQt6, pycryptodome, argon2-cffi, psutil, google-api-python-client
- **Crypto**: RSA-2048, AES-256-GCM, SHA-256, Argon2id, PBKDF2, constant-time comparison
- **OS**: Windows primary, Linux CI (xvfb for GUI tests)
- **Security**: Windows Job Objects, Linux AppArmor, DoD 5220.22-M memory wipe, exponential backoff lockout

## Project Team
- Ibraheem Abusnineh, Karim Taha, Mazin Alsarahin, Ismat Aldmour
- Applied Science University

## Key Decisions
- AES-256-GCM chosen for authenticated encryption (integrity + confidentiality)
- RSA-2048 for key wrapping (asymmetric encrypt the symmetric key)
- Argon2id for password-based key derivation (memory-hard, resistant to GPU/ASIC)
- Mouse movement entropy mixed with OS CSPRNG for session keys
- SFFS binary format: Magic(4) + version + IV + AES-GCM-tag + encrypted payload + hash_pre
- Windows: icacls for ACL control (not just stat); Linux: os.chmod 0o700
- DoD 5220.22-M (3-pass overwrite) for secure memory wipe
