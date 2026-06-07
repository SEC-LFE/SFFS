For future Claude. SFFS sandbox isolation design using OS-level primitives for secure file execution environment.

## Summary
SFFS uses a dual-OS isolation strategy: Windows Job Objects + ACLs on Windows, AppArmor profiles on Linux. The sandbox creates an isolated directory where decrypted files are opened/viewed, preventing escape to the host filesystem.

## Windows Implementation
- **Job Objects**: Process group confinement via Win32 API (`CreateJobObject`, `AssignProcessToJobObject`)
  - Limits: process count, memory, CPU affinity
  - Termination: all children killed when job closes
  - Lazy activation: only if not already running inside a job (checked via `IsProcessInJob`)
- **ACLs**: `icacls` command to:
  - Remove inherited permissions
  - Grant access only to current user
  - Deny access to all others
- **Path**: `C:\Users\<user>\AppData\Local\Temp\sffs_sandbox_<random>\`

## Linux Implementation
- **AppArmor**: Security profile for the sandbox process
  - Filesystem restrictions (read-only outside sandbox)
  - Network access disabled
  - Executable whitelist
- **Permissions**: `os.chmod(0o700)` — owner rwx only
- **Path**: `/tmp/sffs_sandbox_<random>/`

## DoD 5220.22-M Memory Wipe
3-pass overwrite standard:
1. Pass 1: Write zeros (0x00)
2. Pass 2: Write ones (0xFF)
3. Pass 3: Write random bytes
- Applied to: bytearray buffers, key material, decrypted file content
- `ctypes` used to zero memory in C extensions

## Policy Enforcement
- `LauncherPolicyError`: raised when file launch violates sandbox/app policy
- External viewer whitelist via manifest (`apps/` directory with portable viewers: 7zip, ImageGlass)
- Only signed IPC envelopes accepted from `isolated_worker.py`
- Nonce-based replay protection with 10-second expiry

## Related
- [[SFFS Core Architecture]]
- [[01-Projects/Student 2 Security Module]]
- [[Threat Model]]
