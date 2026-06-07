# Graph Report - C:\Users\iblfe\Documents\collage\gp2\test  (2026-05-30)

## Corpus Check
- Large corpus: 292 files · ~295,285 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 1175 nodes · 1920 edges · 62 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `SFFSCore` - 75 edges
2. `AuditLogger` - 52 edges
3. `WorkerThread` - 43 edges
4. `FileManagerExplorer` - 41 edges
5. `LauncherPolicyError` - 38 edges
6. `SFFS (Smart File Fortify System)` - 37 edges
7. `SecurityError` - 35 edges
8. `ProvenanceTable` - 25 edges
9. `WrapStore` - 22 edges
10. `ProcessMonitor` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Verify signed IPC envelope and return trusted payload.` --uses--> `SecurityError`  [INFERRED]
  main-code\isolated_worker.py → code1\f03_decrypt_file.py
- `Background thread: purge expired nonces every 10 s.      WHY a background thre` --uses--> `SecurityError`  [INFERRED]
  main-code\isolated_worker.py → code1\f03_decrypt_file.py
- `Student 1 — crypto module tests.` --uses--> `SecurityError`  [INFERRED]
  tests\test_student1.py → code1\f03_decrypt_file.py
- `f12_emergency_lock.py — Student 2: System-Security Module  The threat model: w` --uses--> `AuditLogger`  [INFERRED]
  code2\f12_emergency_lock.py → code2\f11_write_audit_log.py
- `Emergency lock — immediate security lockdown.      This function performs a se` --uses--> `AuditLogger`  [INFERRED]
  code2\f12_emergency_lock.py → code2\f11_write_audit_log.py

## Hyperedges (group relationships)
- **SFFS Encrypt-Decrypt Pipeline** — code1_f01_generate_key_pairs, code1_f06_secure_key_storage, code1_f02_encrypt_file, code1_f03_decrypt_file, code1_f04_generate_hash, code1_f05_verify_hash, sffs_file_format, aes_256_gcm, rsa_2048 [EXTRACTED 0.95]
- **Emergency Lockdown Flow** — code2_f12_emergency_lock, code2_f07_create_isolated_sandbox, code2_f08_secure_memory_wipe, code2_f09_authenticate_user, code2_f11_write_audit_log, dod_5220_22_m [EXTRACTED 0.95]
- **Authentication and Access Control** — code2_f09_authenticate_user, code2_f08_secure_memory_wipe, argon2id, exponential_backoff_lockout, constant_time_comparison, code1_f06_secure_key_storage [EXTRACTED 0.85]
- **SFFS Modern UI Subsystem** — code3_sffs_ui, code3_mouse_entropy, code3_sandbox_viewer, code3_f16_cloud_sync, code3_f18_thread_controller, code3_f15_file_explorer, code3_f17_config_loader [EXTRACTED 1.00]
- **main-code Integration Layer** — main_code_core, main_code_isolated_worker, main_code_provenance_table, main_code_wrap_store, main_code_entry_point [EXTRACTED 1.00]
- **USB Deployment Toolchain** — scripts_usb_installer, scripts_usb_setup, scripts_reset_data, scripts_install_deps, scripts_fetch_viewers [EXTRACTED 1.00]
- **USB Deployment Pipeline** — setup_usb_standalone_one_click_installer, sffs_usb_pack_full_usb_deployment, launcher_main_usb_launcher_entry, hidden_volume_partition_discovery, hidden_volume_volume_mount_api, generate_icon_shield_lock_icon [EXTRACTED 1.00]
- **SFFS Multi-Layer Test Hierarchy** — test_student1_crypto_module_tests, test_student2_security_module_tests, test_student3_system_architect_tests, test_integration_encrypt_decrypt_roundtrip, test_integration_ipc_replay_protection, test_integration_security_fix_regression, test_sandbox_security_sandbox_structure_tests, test_sandbox_security_launcher_policy_tests, test_sandbox_security_worker_path_policy_tests, test_worker_hardening_ipc_hardening_tests, test_mouse_entropy_entropy_pool_tests, test_cloud_backup_mock_mock_test_suite [EXTRACTED 1.00]
- **Cryptographic Trust Chain Rationale** — code1_readme_sffs_binary_format, code1_readme_aes256gcm_rationale, code1_readme_iv_security_principle, code1_readme_hash_pre_integrity [INFERRED 0.85]
- **Three-Student Modular Architecture** — code2_readme_student2_module, code3_readme_student3_module, maincode_readme_sffscore, docs_architecture_module_map [EXTRACTED 1.00]
- **Student 1 Crypto Functions (F01-F06)** — docs_apireference_f01_keygen, docs_apireference_f02_encrypt, docs_apireference_f03_decrypt, docs_apireference_f04_hash, docs_apireference_f05_verify, docs_apireference_f06_keystore [EXTRACTED 1.00]
- **Student 2 Security Functions (F07-F12)** — docs_apireference_f07_sandbox, docs_apireference_f08_memory_wipe, docs_apireference_f09_auth, docs_apireference_f10_monitor, docs_apireference_f11_audit, docs_apireference_f12_emergency_lock [EXTRACTED 1.00]
- **SFFS Cryptographic Foundation** — converted_aes_256, converted_aes_256_gcm, converted_rsa, converted_sha_256, converted_argon2id, converted_pbkdf2, converted_gcm_tag, converted_constant_time_comparison [EXTRACTED 1.00]
- **SFFS Security Layer** — converted_isolated_execution, converted_isolated_worker, converted_emergency_lock, converted_secure_memory_wipe, converted_process_monitor, converted_audit_logging, converted_sandbox_directory, converted_wrap_store_enc [EXTRACTED 1.00]
- **SFFS Project Team** — converted_ibraheem_abusnineh, converted_karim_taha, converted_mazin_alsarahin, converted_ismat_aldmour, converted_applied_science_university [EXTRACTED 1.00]

## Communities

### Community 0 - "File Manager Explorer"
Cohesion: 0.03
Nodes (53): FileManagerExplorer, f15_file_manager_explorer.py — SFFS Student 3: Scoped file browser  A host ``Q, Two-pane explorer: directory tree + shallow file list for the selected dir., Factory returning a configured ``FileManagerExplorer`` widget.      Args:, Runs ``task(*args, **kwargs)`` and emits signals., WorkerThread, QDialog, QFrame (+45 more)

### Community 1 - "File Decryption & Security Errors"
Cohesion: 0.03
Nodes (83): Exception, decryptFile(), SFFS — Student 1: File Decryption Module  This module decrypts SFFS (.sffs) en, Raised when a security violation is detected during decryption., Decrypt an SFFS file and verify integrity.      The function reads the SFFS he, SecurityError, ProcessMonitor, Background daemon thread that monitors for security threats.      Args: (+75 more)

### Community 2 - "Sandbox & Policy Enforcement"
Cohesion: 0.03
Nodes (36): PermissionError, LauncherPolicyError, Raised when a launch request violates sandbox/app policy., _make_manifest(), Sandbox security audit — functional correctness + leak/escape checks.  Goal:, File content is overwritten; original bytes should not remain., ensure_secure_mode must raise RuntimeError when isolation is inactive., SECURITY: files outside sandbox open root must be rejected. (+28 more)

### Community 3 - "Isolated Sandbox Module"
Cohesion: 0.03
Nodes (76): createIsolatedSandbox(), destroySandbox(), isSandboxIntact(), f07_create_isolated_sandbox.py — Student 2: System-Security Module  An isolate, # WHY: On Linux, os.chmod works with POSIX permission bits (0o700 = owner rwx on, # WHY: On Windows, we need icacls for true ACL control — stat module alone is in, # WHY: This command removes inherited permissions and grants access only to curr, Securely destroy a sandbox by wiping its contents and removing the directory. (+68 more)

### Community 4 - "Crypto Key Gen & AES Encrypt"
Cohesion: 0.04
Nodes (49): generateKeyPairs(), SFFS — Student 1: RSA Key Pair Generation Module  This module generates RSA-20, Generate an RSA-2048 key pair for SFFS encryption/decryption.      RSA asymmet, encryptFile(), SFFS — Student 1: File Encryption Module  This module encrypts files using AES, Encrypt a file using AES-256-GCM and write to SFFS binary format.      The fun, generateFileHash(), generateHash() (+41 more)

### Community 5 - "Mouse Entropy Pool"
Cohesion: 0.04
Nodes (17): feed_mouse_entropy(), Mouse movement entropy — mixed with OS CSPRNG for per-session file keys.  WHY:, Call from GUI mouse-move handler; updates an internal pool (bounded)., Cryptographically strong random bytes, XOR-mixed with mouse pool if any., session_random_bytes(), Tests for code3/mouse_entropy.py — mouse-movement entropy pool.  Covers:   -, Two consecutive calls must produce different results., 50 threads each feed 20 times — pool must stay bounded and valid. (+9 more)

### Community 6 - "API Reference Docs"
Cohesion: 0.06
Nodes (48): F-09 Argon2id Authentication, Student 2 System-Security Module, F-13 USB Drive Detection, Google Drive Backup Setup, Student 3 System Architect Module, F-01 to F-18 API Reference, F-01 generateKeyPairs, F-02 encryptFile (+40 more)

### Community 7 - "USB Installer Setup"
Cohesion: 0.07
Nodes (16): elevate_admin(), _find_source_root(), headless_install(), Installer, InstallerApp, is_admin(), list_removable_drives(), main() (+8 more)

### Community 8 - "Security Concepts & Crypto Primitives"
Cohesion: 0.05
Nodes (43): AES-256, AES-256-GCM, Applied Science Private University, Argon2id, Audit Logging, AxCrypt, BitLocker, Constant-Time Comparison (+35 more)

### Community 9 - "USB Packaging Scripts"
Cohesion: 0.1
Nodes (41): build_executables(), copy_source_code(), copy_to_visible_partition(), create_marker(), _create_placeholder_icon(), download_python_embeddable(), _find_hidden_volume_guid(), generate_icon() (+33 more)

### Community 10 - "Entry Point & Test Suite"
Cohesion: 0.07
Nodes (34): SFFS test suite.  Run all: pytest tests/ -v One file: pytest tests/test_stude, main(), parse_args(), Launch SFFS with the modern UI (sffs_ui.py)., run_full_app(), run_headless_demo(), run_student_demo(), run_tests() (+26 more)

### Community 11 - "USB Drive Detection"
Cohesion: 0.06
Nodes (27): getAvailableSpace(), initDriveDetection(), _linux_mount_root(), monitorUSBPresence(), _partition_for_path(), f13_init_drive_detection.py — SFFS Student 3: USB / portable path layout  Port, Background thread: invoke ``callback`` when ``usb_root`` stops existing., Return (device, is_removable_guess, opts) for path's volume. (+19 more)

### Community 12 - "Hidden Volume Management"
Cohesion: 0.08
Nodes (32): enumerate_volumes(), find_hidden_partition(), find_sffs_partition(), _get_drive_type(), get_mounted_path(), _is_removable(), mount_hidden_volume(), hidden_volume.py — Windows API for hidden partition discovery and mount.  Enum (+24 more)

### Community 13 - "Cloud Backup Mocks"
Cohesion: 0.18
Nodes (24): check(), DummyCreds, _ensure_sffs_paths(), FakeFilesApi, FakeService, _patch(), Standalone mock-based cloud backup test. No Google credentials required. Run:, Apply patches stored as {attr: value} on cloud_mod. (+16 more)

### Community 14 - "UI Dashboard Theme"
Cohesion: 0.1
Nodes (11): apply_sffs_theme(), DragDropZone, f14_ui_dashboard.py — SFFS Student 3: Main PyQt6 shell  PyQt6 provides native, Accepts file drops and emits the first local file path., Primary window after authentication., Trigger cloud backup of keys via sffs_core.backupKeys()., Dark, high-contrast stylesheet for the whole application., Start (or reuse) ``QApplication`` and show the main dashboard.      Args: (+3 more)

### Community 15 - "Crypto Algorithm Design"
Cohesion: 0.11
Nodes (28): AES-256-GCM Authenticated Encryption, Argon2id Memory-Hard Password Hashing, RSA-2048 Key Pair Generation, AES-256-GCM File Encryption, SFFS File Decryption with Integrity Check, Cryptographic Hash Generation, Constant-Time Hash Verification, Secure RSA Private Key Storage with PBKDF2/Argon2id + AES-GCM (+20 more)

### Community 16 - "USB Standalone Setup"
Cohesion: 0.17
Nodes (26): build_executables(), copy_source_code(), download_python_embeddable(), generate_icon(), get_current_drive(), get_disk_number(), get_usb_size(), install_dependencies() (+18 more)

### Community 17 - "Google Drive Cloud Sync"
Cohesion: 0.16
Nodes (14): _assert_keystore_encrypted(), authenticateGoogleDrive(), cloudSync(), _ensure_backup_folder(), loadCredentials(), f16_cloud_sync.py — SFFS Student 3: Google Drive backup (optional)  OAuth 2.0, Return folder ID for SFFS_Backup, creating if needed., Upload, download, list, or delete backups on Google Drive.      Args: (+6 more)

### Community 18 - "Student 3 Module Overviews"
Cohesion: 0.19
Nodes (14): File Manager Explorer, Google Drive Cloud Sync, Encrypted Config Loader, Qt Worker Thread Controller, Mouse Movement Entropy Pool, Student 3 Demo Runner, Sandbox File Viewer, SFFS Modern UI (+6 more)

### Community 19 - "SFFS Icon Generator"
Cohesion: 0.23
Nodes (11): draw_icon(), generate_ico(), _hexagon(), _lock_body(), generate_icon.py — Creates a multi-resolution SFFS shield+lock icon.  Design:, Manually construct a multi-resolution .ico file., Generate a multi-resolution .ico file., Generate hexagon vertices centered at (cx, cy). (+3 more)

### Community 20 - "Community 20"
Cohesion: 0.36
Nodes (9): _assign_process_to_job(), _check_bool(), _create_job_object(), IO_COUNTERS, JOBOBJECT_BASIC_LIMIT_INFORMATION, JOBOBJECT_EXTENDED_LIMIT_INFORMATION, main(), If this process is not already marked as job-isolated, create a Windows Job Obje (+1 more)

### Community 21 - "Community 21"
Cohesion: 0.36
Nodes (9): main(), _opt1(), _opt2(), _opt3(), _opt4(), _opt5(), _opt6(), _opt7() (+1 more)

### Community 22 - "Community 22"
Cohesion: 0.29
Nodes (9): _audit(), _decode_text_preview(), _launch_with_policy(), Read-only viewer for files decrypted into the sandbox.  Text-like files are pr, Show text preview inline, or launch secure external viewer for non-text., Try decoding as common text encodings with a simple readability gate., Best-effort audit log hook through active core logger., Launch non-text files via secure app policy in code2. (+1 more)

### Community 23 - "Community 23"
Cohesion: 0.38
Nodes (7): SFFS Shield+Lock Icon, Hidden Partition Discovery API, Volume Mount/Unmount API, Four-Strategy Partition Discovery, USB Launcher Entry Point, USB One-Click Standalone Installer, Full USB Deployment Automation

### Community 24 - "Community 24"
Cohesion: 0.33
Nodes (6): Audit Log SQLite Retry Test, Security Fix Regression Tests, Five Security Fix Verification Tests, Sandbox Structure Tests, Auth Timing Constant-Time Test, Student 2 Security Module Tests

### Community 25 - "Community 25"
Cohesion: 0.7
Nodes (4): install_deps(), list_removable(), main(), verify()

### Community 26 - "Community 26"
Cohesion: 0.4
Nodes (5): AES-256-GCM Rationale, Hash-Before-Encryption Integrity Proof, IV Uniqueness Principle, SFFS Binary Format Specification, Unified Dependency Entrypoint

### Community 27 - "Community 27"
Cohesion: 0.67
Nodes (2): featureCard(), mkShadow()

### Community 28 - "Community 28"
Cohesion: 0.5
Nodes (1): Windows Job Object lazy activation when not started via sffs.bat.

### Community 29 - "Community 29"
Cohesion: 0.83
Nodes (4): OS-Level Isolation Detection (AppArmor/Windows Job), Secure External Viewer Launcher with Manifest Policy, Windows Job Object Isolation Wrapper, Windows Job Object Process Confinement

### Community 30 - "Community 30"
Cohesion: 0.67
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 0.67
Nodes (1): Resolve-only integration check for portable viewers (no GUI spawn).

### Community 32 - "Community 32"
Cohesion: 0.67
Nodes (3): Portable Viewer Downloader, USB Installer GUI, USB Setup and Verify

### Community 33 - "Community 33"
Cohesion: 0.67
Nodes (3): Cloud Backup E2E Test, Cloud Backup Mock Test Suite, Student 3 System Architect Tests

### Community 34 - "Community 34"
Cohesion: 0.67
Nodes (3): Encrypt-Decrypt Roundtrip Integration Test, HMAC File Binding Check Test, Student 1 Crypto Module Tests

### Community 35 - "Community 35"
Cohesion: 0.67
Nodes (3): IPC Replay Protection Tests, Worker Path Policy Tests, Worker IPC Hardening Tests

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (3): P1 Demo-Killing Bug Fixes, P4 Security Fixes, Demo Day Implementation Plan

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): SFFS setup.py — allows pip install -e . for development mode

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Pytest configuration — ensures SFFS package roots are on sys.path.

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (2): Zip Path Traversal Rejection, Unencrypted Keystore Upload Block

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (2): Manifest Route Validation Test, USB Launcher Manifest Resolution Probe

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (2): OS Isolation Detection Tests, Windows Job Object Lazy Activation Tests

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (2): Launcher Policy Enforcement Tests, External Viewer PID Termination Test

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (2): Pytest sys.path configuration, SFFS Test Suite Init

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Compute canonical hash for an audit entry.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Read hash_pre from .sffs header without decrypting.          Layout: Magic(4)

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Dependency Installer

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Mouse Entropy Pool Tests

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Entropy Pool Thread Safety Tests

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Smart File Fortify System

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): SFFS Critical Development Rules

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): CI Pipeline Configuration

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Project Team & Supervisor

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Requirements Dependencies

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Locked Dependencies (pip-compile)

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Sample Test Output

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Full Cloud Sync (Auto-sync)

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): C++ or Java Backend Modules

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): HSM/YubiKey Support

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Linux Sandbox Hardening (bubblewrap/Firejail)

## Knowledge Gaps
- **312 isolated node(s):** `SFFS — Student 1: RSA Key Pair Generation Module  This module generates RSA-20`, `Generate an RSA-2048 key pair for SFFS encryption/decryption.      RSA asymmet`, `SFFS — Student 1: File Encryption Module  This module encrypts files using AES`, `Encrypt a file using AES-256-GCM and write to SFFS binary format.      The fun`, `SFFS — Student 1: File Decryption Module  This module decrypts SFFS (.sffs) en` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 37`** (2 nodes): `setup.py`, `SFFS setup.py — allows pip install -e . for development mode`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `sffs_install_deps.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `conftest.py`, `Pytest configuration — ensures SFFS package roots are on sys.path.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `Zip Path Traversal Rejection`, `Unencrypted Keystore Upload Block`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `Manifest Route Validation Test`, `USB Launcher Manifest Resolution Probe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `OS Isolation Detection Tests`, `Windows Job Object Lazy Activation Tests`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (2 nodes): `Launcher Policy Enforcement Tests`, `External Viewer PID Termination Test`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (2 nodes): `Pytest sys.path configuration`, `SFFS Test Suite Init`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Compute canonical hash for an audit entry.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Read hash_pre from .sffs header without decrypting.          Layout: Magic(4)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `fetch_missing_viewers.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Dependency Installer`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Mouse Entropy Pool Tests`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Entropy Pool Thread Safety Tests`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Smart File Fortify System`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `SFFS Critical Development Rules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `CI Pipeline Configuration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Project Team & Supervisor`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Requirements Dependencies`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Locked Dependencies (pip-compile)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Sample Test Output`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Full Cloud Sync (Auto-sync)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `C++ or Java Backend Modules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `HSM/YubiKey Support`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Linux Sandbox Hardening (bubblewrap/Firejail)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SFFSCore` connect `File Manager Explorer` to `File Decryption & Security Errors`, `Entry Point & Test Suite`, `Isolated Sandbox Module`, `Cloud Backup Mocks`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `LauncherPolicyError` connect `Sandbox & Policy Enforcement` to `Entry Point & Test Suite`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `Policy tests for secure external viewer launcher.` connect `Entry Point & Test Suite` to `File Manager Explorer`, `Sandbox & Policy Enforcement`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `SFFSCore` (e.g. with `Card` and `Badge`) actually correct?**
  _`SFFSCore` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `AuditLogger` (e.g. with `f12_emergency_lock.py — Student 2: System-Security Module  The threat model: w` and `Emergency lock — immediate security lockdown.      This function performs a se`) actually correct?**
  _`AuditLogger` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `WorkerThread` (e.g. with `Interactive demo runner for Student 3 (System Architect) modules.` and `Card`) actually correct?**
  _`WorkerThread` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `FileManagerExplorer` (e.g. with `Card` and `Badge`) actually correct?**
  _`FileManagerExplorer` has 33 INFERRED edges - model-reasoned connections that need verification._