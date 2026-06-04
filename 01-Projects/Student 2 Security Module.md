For future Claude. Student 2's security module implements sandboxing, authentication, process monitoring, audit logging, and emergency lockdown for SFFS. Six functions (F07-F12).

## Summary
Creates isolated sandbox directories with OS-level access control (Windows Job Objects / Linux AppArmor), securely wipes memory per DoD 5220.22-M, authenticates users with Argon2id + exponential backoff, monitors processes, writes tamper-proof audit logs to SQLite, and performs emergency security lockdown.

## Functions
| Function | File | Purpose |
|----------|------|---------|
| F07 `createIsolatedSandbox()` | `code2/f07_create_isolated_sandbox.py` | Sandbox dir with OS isolation |
| F08 `secureMemoryWipe()` | `code2/f08_secure_memory_wipe.py` | DoD 5220.22-M 3-pass overwrite |
| F09 `authenticateUser()` | `code2/f09_authenticate_user.py` | Argon2id password auth |
| F10 `ProcessMonitor` | `code2/f10_process_monitor.py` | Background security threat monitor |
| F11 `writeAuditLog()` | `code2/f11_write_audit_log.py` | SQLite audit log with hash chain |
| F12 `emergencyLock()` | `code2/f12_emergency_lock.py` | Immediate security lockdown |

## Key Design Decisions
- **Windows**: `icacls` for ACL control + Job Objects for process isolation
- **Linux**: `os.chmod(0o700)` + AppArmor profiles
- **Memory wipe**: DoD 5220.22-M standard (3-pass: zeros, ones, random)
- **Auth**: Argon2id (memory-hard), exponential backoff lockout, constant-time comparison
- **Audit**: SQLite with hash-linked entries for tamper evidence

## Related
- [[SFFS Project Overview]]
- [[SFFS Core Architecture]]
- [[Sandbox Isolation Design]]
- [[Threat Model]]
