# GP2 Exam Answers — Student 2 (Security, code2, f07–f12)

---

**Q101. In `f07_create_isolated_sandbox.py`, the `_wipe_stale_sandboxes()` function is called at the start of every `createIsolatedSandbox()` call. What security threat does wiping stale sandboxes prevent, and what is the "stale" detection criterion (how is a sandbox determined to be from a crashed session)?**

**Answer:** Stale sandboxes from crashed or unclean sessions may still contain decrypted plaintext files on disk, which an attacker or forensic tool could read. By wiping them at the start of every new session, SFFS ensures no leftover plaintext persists across session boundaries. A sandbox is considered stale if its `sandbox.lock` file is absent or if its `st_mtime` age exceeds 24 hours (`cutoff = 24 * 3600` seconds).

**Reasoning:** The lock file's modification time acts as a heartbeat; a missing or old lock means the session that created the sandbox is gone and the plaintext it left behind is now orphaned and dangerous.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `_wipe_stale_sandboxes()` ~line 37

---

**Q102. In `f07_create_isolated_sandbox.py`, the sandbox directory is created with `exist_ok=False` (line 99). What happens if a `sandbox_<session_id>` directory already exists, and why is it safer to fail with an error rather than silently reusing the existing directory?**

**Answer:** If the directory already exists, `mkdir(exist_ok=False)` raises `FileExistsError`, aborting sandbox creation. Silently reusing an existing directory is dangerous because it might contain files from a prior session (including decrypted secrets) or might have been placed there by an attacker to pre-stage malicious content.

**Reasoning:** Fail-closed is always safer: an unexpected pre-existing directory is a red flag, not a convenience.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 99

---

**Q103. In `f07_create_isolated_sandbox.py`, on Linux the sandbox is created with `os.chmod(sandbox_path, 0o700)`. What does the octal permission `0o700` mean in terms of read/write/execute for owner, group, and others? Why is execute permission included for a directory that contains files?**

**Answer:** `0o700` gives the owner read (4), write (2), and execute (1) permission; group and others get no permissions at all. For directories, the execute bit is the "search" bit — without it, a user cannot `cd` into the directory or access files inside it, even if they know the filename.

**Reasoning:** On Linux, directory execute permission is required to traverse into a directory, so `0o700` gives the owner full access while completely blocking everyone else.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 110

---

**Q104. In `f07_create_isolated_sandbox.py`, the Windows path uses `icacls` with `/inheritance:r` and `/grant:r`. What does `/inheritance:r` do to the inherited ACL entries, and what security risk exists on Windows if this flag is omitted?**

**Answer:** `/inheritance:r` removes all inherited ACL entries from the directory, leaving only explicitly granted entries. Without this flag, the sandbox directory inherits permissions from its parent (e.g., a temp folder accessible by all users), making it world-readable and breaking isolation entirely.

**Reasoning:** Windows ACL inheritance is enabled by default; omitting `/inheritance:r` means broad parent permissions silently propagate to the sandbox.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 119

---

**Q105. In `f07_create_isolated_sandbox.py`, after `icacls` runs on Windows, the code calls `isSandboxIntact(sandbox_path)` to verify the ACLs were actually applied. Why is this post-creation verification necessary — what attack or system misconfiguration could cause `icacls` to succeed (return code 0) but leave broad permissions?**

**Answer:** `icacls` can return exit code 0 even if the ACL change was only partially applied (e.g., on network drives or redirected folders where ACL inheritance is re-applied by group policy). A misconfigured Group Policy Object can silently re-add broad entries after `icacls` completes, so verifying the output is the only reliable confirmation.

**Reasoning:** Trusting the exit code alone is insufficient; an explicit check of the resulting ACL output closes the verification gap.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 164

---

**Q106. In `f07_create_isolated_sandbox.py`, the `sandbox.lock` file on Linux is created using `os.open()` with `os.O_WRONLY | os.O_CREAT | os.O_TRUNC` and mode `0o600`, while on Windows it is created with `Path.write_text()`. Why does the Linux path use the low-level `os.open()` with an explicit mode, and what security issue would arise from using `Path.write_text()` on Linux?**

**Answer:** `Path.write_text()` opens the file after creation and does not accept a mode argument, so the file is created with the process's umask-modified default (often `0o644`), which allows group/other read access. Using `os.open()` with mode `0o600` atomically creates the file with owner-only permissions, preventing other local users from reading the session ID stored in the lock file.

**Reasoning:** The session ID is sensitive metadata; the atomic `os.open()` with explicit mode is the only safe way to guarantee the file is never briefly readable by others.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 154

---

**Q107. In `f07_create_isolated_sandbox.py`, the `createIsolatedSandbox()` creates three subdirectories: `decrypted/`, `temp/`, and `keys_runtime/`. What is the security purpose of having separate subdirectories rather than placing all files in the sandbox root?**

**Answer:** Separation provides principle of least privilege at the filesystem level: decrypted plaintext goes in `decrypted/`, ephemeral scratch data in `temp/`, and runtime key material in `keys_runtime/`. This allows different cleanup policies per subdirectory and limits the blast radius if one subdirectory is inadvertently exposed — a leaked temp file does not sit next to a decrypted secret file.

**Reasoning:** Compartmentalization limits what an attacker learns if they gain partial access to the sandbox.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 136

---

**Q108. In `f07_create_isolated_sandbox.py`, the `destroySandbox()` function calls `secureWipeDirectory()` before `shutil.rmtree()`. The docstring explicitly states that `shutil.rmtree()` alone is "NOT sufficient for secure deletion." Explain technically why deleting a file without overwriting it first still leaves the data recoverable on many filesystems.**

**Answer:** On most filesystems (ext4, NTFS, FAT32), deleting a file only removes the directory entry and marks the data blocks as free; the actual bytes remain in the unallocated region until overwritten by new data. Forensic tools such as PhotoRec or Autopsy can scan unallocated space and reassemble files from these intact blocks.

**Reasoning:** True secure deletion requires overwriting the data blocks before releasing them; `secureWipeDirectory()` does exactly this with three passes before `rmtree` removes the now-zeroed entries.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `destroySandbox()` ~line 211

---

**Q109. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` function implements a 3-pass DOD 5220.22-M overwrite (zeros, ones, random). For modern SSDs with wear-leveling firmware, why might even 3-pass overwrite fail to guarantee erasure of sensitive data?**

**Answer:** SSD wear-leveling firmware transparently remaps logical block addresses to different physical NAND cells, so an OS write to logical block X may go to a new physical location while the original physical cell (containing the old data) is moved to a spare pool and not immediately overwritten. The multi-pass overwrite only reaches the current logical mapping, leaving old copies in the SSD's internal spare area that are only erased at the firmware's discretion.

**Reasoning:** The only reliable method on SSDs is ATA Secure Erase or full-disk encryption where the key is thrown away, because both operate at the firmware level below wear-leveling.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `secureWipeDirectory()` ~line 243

---

**Q110. In `f07_create_isolated_sandbox.py`, the `_write_and_sync()` helper calls `fh.flush()` followed by `os.fsync(fh.fileno())` after each overwrite pass. What is the difference between `flush()` and `fsync()`, and why are both needed when writing security-critical overwrites?**

**Answer:** `flush()` moves data from Python's user-space buffer to the OS kernel page cache, while `os.fsync()` instructs the kernel to flush its page cache to the physical storage device. Without `flush()`, data may not reach the kernel; without `fsync()`, data sits in the kernel cache and a power failure (or OS crash) would mean the overwrite never reached the disk — leaving the previous pass recoverable.

**Reasoning:** Both calls together create a chain: Python buffer → kernel cache → storage device, ensuring each overwrite pass is durably committed before the next begins.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `_write_and_sync()` ~line 239

---

**Q111. In `f07_create_isolated_sandbox.py`, the `isSandboxIntact()` function on Linux checks if the permission mode is in `("700", "400", "500")`. Why are `400` and `500` considered acceptable alternatives to `700`, and under what administrative scenario would these stricter modes appear?**

**Answer:** `0o400` (owner read-only) and `0o500` (owner read+execute) are stricter than `0o700` — they remove write permission, making the sandbox contents immutable to even the owner. An administrator might set these modes to lock down a sandbox for forensic preservation or audit, or a security policy script might automatically tighten permissions after creation.

**Reasoning:** Accepting these modes avoids false-positive integrity failures while still rejecting any mode that grants group or other access.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `isSandboxIntact()` ~line 386

---

**Q112. In `f07_create_isolated_sandbox.py`, the `isSandboxIntact()` function on Windows checks for "broad access entries" including `"Everyone"`, `"BUILTIN\\Users"`, and `"NT AUTHORITY\\Authenticated Users"`. Why are these three specific principal names considered threats to sandbox isolation?**

**Answer:** "Everyone" includes all users including unauthenticated guests; "BUILTIN\\Users" includes all local user accounts on the machine; "NT AUTHORITY\\Authenticated Users" includes any user who has logged in, including remote network users. Any of these principals having access to the sandbox directory would allow other processes or users on the same machine to read the decrypted files it contains.

**Reasoning:** These three are the most commonly inherited broad groups on Windows and represent the main vectors through which sandbox isolation breaks.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `isSandboxIntact()` ~line 405

---

**Q113. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function raises `TypeError` if `target` is not a `bytearray`. The docstring explains that Python strings are "immutable and interned by the interpreter." What does interning mean in CPython, and give a concrete example of how interning prevents secure erasure of a string containing a password.**

**Answer:** String interning means CPython caches certain string objects and reuses the same object when the same string literal appears again; for example, `a = "password123"; b = "password123"` may give `a is b == True` because both refer to the same interned object. Even if you nullify `a = ""`, the interned object still lives in CPython's string cache, so the original `"password123"` bytes remain accessible in memory until the interpreter decides to evict it.

**Reasoning:** Immutability + interning means you cannot overwrite the bytes of the original string object regardless of what you do to the Python variable referencing it.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` ~line 75

---

**Q114. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function performs a final `target[:] = b'\x00' * len(target)` zero-out after all passes complete (line 107). Why is this final zeroing pass performed even though pass 3 already overwrites with random bytes?**

**Answer:** The final zero-out ensures that if the caller's code later inspects the bytearray (e.g., for debugging, logging, or comparison), it sees a clearly wiped all-zero buffer rather than ambiguous random data that could be mistaken for still-sensitive content. It also removes the random bytes from memory, which themselves could theoretically be misused if they were cryptographically related to key material.

**Reasoning:** Ending in a predictable all-zero state makes the "wiped" status unambiguous and removes any residual entropy that the random pass introduced.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` ~line 107

---

**Q115. In `f08_secure_memory_wipe.py`, the `wipeString()` function encodes the string to UTF-8, creates a `bytearray`, and calls `secureMemoryWipe()` on the bytearray. The docstring warns this is "best-effort only." What fundamental limitation prevents true erasure of the original Python string object, even after this function completes?**

**Answer:** The `s.encode('utf-8')` call creates a new `bytes` object (a copy of the string's data), and `secureMemoryWipe()` wipes only that copy — the original Python `str` object's internal buffer is never touched. Because Python strings are immutable, there is no supported API to overwrite the actual memory of the `str` object in place; it persists until CPython's garbage collector reclaims it.

**Reasoning:** The function wipes a UTF-8 copy, not the string itself; the original `str` object's memory cannot be modified through Python's object model.

**Reference:** `code2/f08_secure_memory_wipe.py` → `wipeString()` ~line 126

---

**Q116. In `f08_secure_memory_wipe.py`, the docstring explains: "A cold boot attack occurs when an attacker freezes RAM." What is the physical basis for cold boot attacks — why does cooling RAM preserve its contents after power loss — and what does this imply about the minimum viable duration for secure memory wipe operations?**

**Answer:** DRAM cells store bits as charge on capacitors; at room temperature the charge leaks within milliseconds, but cooling to -50°C or below dramatically slows leakage (minutes to hours), preserving the bit pattern after power is removed. An attacker can remove and quickly freeze the DIMM, then transfer it to a reader to dump its contents. This means secure memory wipes must complete within the time the RAM remains powered — effectively before the attacker can physically extract and cool it — so wipe operations should complete in well under one second.

**Reasoning:** The physical retention time at low temperature is the adversarial budget; wipes must beat it.

**Reference:** `code2/f08_secure_memory_wipe.py` → module docstring ~line 8

---

**Q117. In `f08_secure_memory_wipe.py`, `os.urandom(len(target))` is used for the random-bytes pass. Why is `os.urandom()` preferred over Python's `random.getrandbytes()` for the security-critical final pass of the DOD wipe standard?**

**Answer:** `os.urandom()` pulls from the operating system's cryptographically secure random number generator (e.g., `/dev/urandom` on Linux, `BCryptGenRandom` on Windows), which is seeded with hardware entropy and is unpredictable to an attacker. Python's `random` module uses a Mersenne Twister PRNG that is not cryptographically secure — given a few hundred bytes of its output, an attacker can reconstruct its internal state and predict all past and future bytes, making the overwrite pattern recoverable.

**Reasoning:** The random pass must be unpredictable; only a CSPRNG like `os.urandom()` guarantees that.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` ~line 102

---

**Q118. In `f08_secure_memory_wipe.py`, the `createSecureBuffer(size)` function simply returns `bytearray(size)`. Why is creating a zeroed `bytearray` specifically through this function (rather than just calling `bytearray(size)` inline) considered a best practice from a code-review and security standpoint?**

**Answer:** Wrapping the allocation in a named function makes the security intent explicit and searchable: any code that creates a buffer for sensitive data should be auditable by searching for `createSecureBuffer`. It also provides a single place to add future enhancements (e.g., locking the memory page with `mlock` to prevent swapping) without changing every call site.

**Reasoning:** Named allocation functions turn a bare `bytearray()` call into a documented security contract, improving both auditability and future extensibility.

**Reference:** `code2/f08_secure_memory_wipe.py` → `createSecureBuffer()` ~line 169

---

**Q119. In `f09_authenticate_user.py`, a `_DUMMY_HASH` is pre-computed at module load time (lines 57–59). Explain the timing-based username enumeration attack this prevents, and calculate approximately how long an attacker could enumerate usernames without this defense if Argon2id takes 100 ms per verification.**

**Answer:** Without the dummy hash, an unknown username returns immediately (0 ms) because the code skips password verification; a known username takes ~100 ms for Argon2 verification. An attacker can test usernames by measuring response time: instant ≈ invalid, slow ≈ valid. With the dummy hash, both paths take ~100 ms, eliminating the timing signal. Without this defense, an attacker could enumerate roughly 10 usernames per second (1000 ms / 100 ms) — 600 per minute — trivially fast for a small user database.

**Reasoning:** Constant-time rejection removes the timing oracle that separates valid from invalid usernames.

**Reference:** `code2/f09_authenticate_user.py` → `_DUMMY_HASH` ~line 57

---

**Q120. In `f09_authenticate_user.py`, the `_compute_lock_until()` function uses `min(30 * (2 ** (failed_attempts - 1)), 3600)`. Calculate the lockout duration after the 5th, 6th, and 7th consecutive failed attempts, and explain why the lockout is capped at 3600 seconds.**

**Answer:** 5th attempt: `30 * 2^4 = 480` seconds (8 min); 6th attempt: `30 * 2^5 = 960` seconds (16 min); 7th attempt: `30 * 2^6 = 1920` seconds, but capped at 3600 seconds (1 hour). The cap prevents the lockout from growing so large that a legitimate user is permanently denied access due to a runaway exponential — 1 hour is severe enough to deter brute force while still being recoverable.

**Reasoning:** Unbounded exponential lockout would eventually lock an account for days or years from a modest number of failures, constituting a self-inflicted denial-of-service.

**Reference:** `code2/f09_authenticate_user.py` → `_compute_lock_until()` ~line 67

---

**Q121. In `f09_authenticate_user.py`, the `authenticateUser()` function calls `secureMemoryWipe(password)` inside a `finally` block (line 239). Why is `finally` critical here — what specific scenario would cause the password to NOT be wiped if `finally` were replaced with a plain call after `pw.verify()`?**

**Answer:** If `pw.verify()` raises an unexpected exception (e.g., `VerificationError`, `MemoryError`, or a library-internal error that is not `VerifyMismatchError`), execution would skip the wipe call placed after it and propagate the exception up the call stack — leaving the password bytearray intact in memory. The `finally` block runs unconditionally regardless of whether an exception is raised, ensuring the wipe always happens.

**Reasoning:** Any exception in `pw.verify()` that is not caught before the wipe line would leave the password in memory; `finally` is the only Python construct that provides this unconditional guarantee.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 235

---

**Q122. In `f09_authenticate_user.py`, `registerUser()` accepts `password: bytearray` rather than `password: str`. The caller must pass a mutable bytearray. From the perspective of the function's security contract, what obligation does this API design place on the caller after `registerUser()` returns?**

**Answer:** The function wipes the bytearray in place before returning, so after `registerUser()` returns, the caller's bytearray reference now contains zeros — the password is gone. The caller must not attempt to read or re-use the bytearray after the call, and must not pass the same bytearray to another function expecting the original password. The design places the entire password lifecycle responsibility on the call boundary.

**Reasoning:** By wiping inside `registerUser()`, the API enforces that the password is single-use; the caller is obligated to treat the bytearray as consumed and invalid after the call returns.

**Reference:** `code2/f09_authenticate_user.py` → `registerUser()` ~line 143

---

**Q123. In `f09_authenticate_user.py`, the `sessions` table stores `expires_at` as an ISO timestamp string. In `validateSession()`, the check `expires_at > now` is a lexicographic string comparison. Under what conditions could lexicographic ISO string comparison fail, and is it reliable for this purpose?**

**Answer:** ISO 8601 timestamps in the format `YYYY-MM-DDTHH:MM:SS.ffffff` (produced by `datetime.now().isoformat()`) are lexicographically sortable because the most significant components come first. The comparison is reliable as long as both timestamps are produced by the same format call (same locale, same Python version) with no timezone suffix. It would fail if one timestamp had a `+HH:MM` timezone suffix and the other did not, or if a legacy entry used a different format like `DD/MM/YYYY`.

**Reasoning:** Consistent use of `datetime.now().isoformat()` throughout the module makes this reliable in practice, but it is fragile to format variation.

**Reference:** `code2/f09_authenticate_user.py` → `validateSession()` ~line 306

---

**Q124. In `f09_authenticate_user.py`, the `registerUser()` function enforces a password policy: minimum 12 characters, with uppercase, lowercase, digit, and special character. Why is minimum length (12 chars) considered more important than complexity requirements by modern security standards (NIST SP 800-63B)?**

**Answer:** Password entropy grows exponentially with length but only linearly with character-set size. A 12-character password from a 95-character ASCII set has ~78 bits of entropy; adding one more character contributes ~6.5 more bits, while requiring one uppercase letter adds at most a few bits. NIST SP 800-63B emphasizes length because it provides greater resistance to brute-force attacks than complexity rules, which often lead users to predictable patterns like `Password1!` that satisfy complexity but have low effective entropy.

**Reasoning:** Length dominates entropy; complexity rules have diminishing returns and promote bad user behavior.

**Reference:** `code2/f09_authenticate_user.py` → `registerUser()` ~line 125

---

**Q125. In `f09_authenticate_user.py`, SQLite is chosen for the authentication database over other options. The comment says it is "USB-portable" and "no server needed." What are the security tradeoffs of using a local SQLite file for authentication compared to a remote authentication server?**

**Answer:** SQLite on a USB is offline-capable and self-contained, but the database file is physically accessible to anyone with the USB — it can be copied and brute-forced offline at full GPU speed (though Argon2id mitigates this). A remote authentication server keeps credentials off the client device entirely and can enforce rate-limiting server-side; however, it requires network connectivity and introduces a server compromise risk. For SFFS's threat model (portable, air-gapped use), local SQLite with strong KDF is the appropriate tradeoff.

**Reasoning:** The offline portability requirement forces local storage; Argon2id compensates for the physical access risk.

**Reference:** `code2/f09_authenticate_user.py` → `initAuthDatabase()` ~line 71

---

**Q126. In `f09_authenticate_user.py`, on successful authentication, `failed_attempts` is reset to 0 and `locked_until` is set to `NULL`. What security implication does resetting the counter on success have — could an attacker exploit this to brute-force a password without triggering permanent lockout?**

**Answer:** Yes — an attacker who knows the correct password prefix could attempt N-1 guesses (stopping before lockout), then use any side channel to confirm a partial match, and repeat. More practically, an attacker with one correct credential can log in between bursts to reset the counter, effectively making the lockout per-burst rather than cumulative. Persistent lockout counters (reset only by admin action) would be more secure, though at the cost of increased legitimate lockout.

**Reasoning:** The reset-on-success policy is a usability tradeoff; cumulative counters would be more secure but would frequently lock out legitimate users who occasionally mistype.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 259

---

**Q127. In `f09_authenticate_user.py`, the session token is generated with `secrets.token_urlsafe(32)`. Why is `token_urlsafe` used rather than `token_hex`, and what is the effective entropy in bits of a 32-byte URL-safe token?**

**Answer:** `token_urlsafe(32)` produces 32 random bytes encoded in base64url (A-Z, a-z, 0-9, `-`, `_`), yielding a 43-character string safe for use in HTTP headers and URLs without escaping. `token_hex(32)` produces 64 hex characters using only 16 symbols, making the string longer for the same entropy. Both have 256 bits of entropy (32 bytes × 8 bits), but `token_urlsafe` is more compact and URL-friendly.

**Reasoning:** URL-safe encoding is practical for session tokens sent in cookies or headers; the underlying entropy is identical to `token_hex(32)` at 256 bits.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 263

---

**Q128. In `f09_authenticate_user.py`, the `authenticateUser()` function uses `conn.execute("BEGIN EXCLUSIVE")` is NOT explicitly used — the session insertion is done after the `UPDATE` with standard `conn.commit()`. What race condition could occur in a multi-process environment where two processes try to authenticate the same user simultaneously?**

**Answer:** Two processes could both read `failed_attempts = 0` and both compute the new failed count independently, then both write back — one write would overwrite the other, potentially under-counting failures. Similarly, both could pass the lockout check simultaneously and both create separate session rows for the same user, resulting in duplicate active sessions. Without an exclusive transaction spanning the read-update-insert sequence, these TOCTOU races are possible.

**Reasoning:** Non-atomic read-modify-write on `failed_attempts` and session creation allows concurrent processes to produce inconsistent state.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 186

---

**Q129. In `f10_monitor_process.py`, the `isDebuggerPresent()` function on Linux reads `/proc/self/status` and checks the `TracerPid:` field. What is TracerPid, and under what Linux privilege model can a process trace (ptrace) another process?**

**Answer:** `TracerPid` in `/proc/self/status` shows the PID of the process that is currently `ptrace`-attached to the current process; a value of 0 means no tracer. On modern Linux (with Yama security module), by default only a parent process or a process with `CAP_SYS_PTRACE` capability can attach to another process (`ptrace_scope=1`). At `ptrace_scope=0` (permissive), any process of the same user can attach.

**Reasoning:** The `ptrace_scope` kernel parameter governs who can trace whom; without elevated privilege, most debuggers require parent-child relationship or `CAP_SYS_PTRACE`.

**Reference:** `code2/f10_monitor_process.py` → `isDebuggerPresent()` ~line 67

---

**Q130. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` caps the process iteration at `MAX_PROCS = 1000` using `itertools.islice()`. The comment says "Legitimate debuggers typically appear early in the list." Is this assumption reliable, and how could an attacker exploit the 1000-process cap to evade detection?**

**Answer:** The assumption is not reliable — on Linux, `psutil.process_iter()` returns processes roughly in PID order (low PIDs first), and an attacker could deliberately launch their debugger with a high PID (e.g., by spawning 1000 sacrificial processes first to push the debugger beyond PID 1000). On Windows, process order is not guaranteed and a sophisticated attacker could ensure their tool's PID appears above the cap.

**Reasoning:** Caps introduce a predictable blind spot; an attacker with process-creation ability can trivially push their tool beyond the inspection window.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 97

---

**Q131. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` on Windows checks for `["x64dbg.exe", "ollydbg.exe", "windbg.exe", "ida64.exe", "processhacker.exe", "wireshark.exe"]`. What is the limitation of signature-based detection of "suspicious" processes by name, and what simple evasion technique would defeat this list entirely?**

**Answer:** The blocklist only matches exact process names; any attacker can rename `x64dbg.exe` to `notepad2.exe` or any other innocent-sounding name and the check will not flag it. More broadly, signature-based detection cannot discover unknown or custom tools. It provides a low-friction deterrent against script kiddies but offers zero protection against a prepared adversary.

**Reasoning:** Name-based detection is the weakest form of anti-debugging; a single rename completely defeats it.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 103

---

**Q132. In `f10_monitor_process.py`, the `ProcessMonitor` class inherits from `threading.Thread` and is created with `daemon=True`. What does daemon mode mean for a thread, and what would happen to the monitoring thread if the main SFFS process terminates unexpectedly?**

**Answer:** A daemon thread is automatically killed by the Python interpreter when the last non-daemon thread exits, without waiting for the daemon thread to finish its current iteration. If the main SFFS process terminates unexpectedly (e.g., due to `sys.exit()` from `emergencyLock()`), the OS will kill all daemon threads immediately — the monitoring loop stops without needing explicit cleanup code.

**Reasoning:** Daemon mode ensures the monitoring thread never prevents a clean process exit; it lives only as long as the process needs it.

**Reference:** `code2/f10_monitor_process.py` → `ProcessMonitor.__init__()` ~line 141

---

**Q133. In `f10_monitor_process.py`, the `ProcessMonitor.run()` loop uses `self._stop_event.wait(self.check_interval)` instead of `time.sleep(self.check_interval)`. What is the advantage of using `threading.Event.wait()` for the sleep in a monitoring thread?**

**Answer:** `threading.Event.wait(timeout)` blocks for at most `timeout` seconds but returns immediately if the event is set before the timeout expires. When `stop()` is called and sets `_stop_event`, the thread wakes up at once rather than waiting for the full sleep interval to elapse. With `time.sleep()`, the thread would remain blocked for up to `check_interval` (500 ms) after `stop()` is called before noticing the stop signal.

**Reasoning:** `Event.wait()` combines sleeping with interruptibility, enabling near-instant thread termination on demand.

**Reference:** `code2/f10_monitor_process.py` → `ProcessMonitor.run()` ~line 169

---

**Q134. In `f10_monitor_process.py`, when a threat is detected, `_handleThreat()` calls `self.threat_detected.set()` and `self._stop_event.set()` before invoking the callback. Why is the stop event set before the callback runs, and what could go wrong if the callback raised an unhandled exception?**

**Answer:** Setting `_stop_event` before the callback ensures the monitoring loop is marked as done even if the callback raises an exception or blocks indefinitely — the thread will not restart the detection loop. The callback is wrapped in a `try/except Exception: pass` block, so an unhandled exception in the callback is silently swallowed, preventing it from crashing the monitor thread while still guaranteeing the threat flag remains set.

**Reasoning:** Pre-setting the stop event is a defensive pattern: the detection result is recorded before any potentially unreliable callback code runs.

**Reference:** `code2/f10_monitor_process.py` → `_handleThreat()` ~line 180

---

**Q135. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` catches `psutil.NoSuchProcess`, `psutil.AccessDenied`, and `psutil.ZombieProcess` exceptions when iterating. Why is `psutil.AccessDenied` especially common on Windows, and does silently continuing on `AccessDenied` represent a security gap?**

**Answer:** On Windows, reading process attributes (especially `exe()`) for processes owned by other users (SYSTEM, services) requires `SeDebugPrivilege`, which normal user processes do not have. `psutil.AccessDenied` is raised for these privileged processes. Silently continuing creates a security gap: an attacker running a debugger as SYSTEM or as a different user would be invisible to this check — exactly the scenario where detection is most needed.

**Reasoning:** The most privileged processes (which are the most dangerous attackers' tools) are the most likely to trigger `AccessDenied`, creating a blind spot in the highest-risk category.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 125

---

**Q136. In `f11_write_audit_log.py`, the `AuditLogger` class uses `threading.Lock()` to serialize writes. The lock is acquired in the `log()` method via `with self.lock:`. What specific data corruption scenario would occur without this lock in a multi-threaded application where Student 1, Student 2, and Student 3 modules all call `writeAuditLog()` concurrently?**

**Answer:** Without the lock, two threads could both read the same `prev_hash` (the last entry's hash) at the same time, then both insert new entries referencing the same predecessor — breaking the hash chain by creating a forked chain rather than a linear one. Additionally, SQLite without serialization can produce `database is locked` errors or partial writes that corrupt the WAL file when multiple threads write simultaneously.

**Reasoning:** The hash chain integrity depends on reading the last hash and inserting the new entry as an atomic unit; concurrent threads interleaving these operations would fork the chain.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.log()` ~line 169

---

**Q137. In `f11_write_audit_log.py`, the `log()` method uses `BEGIN EXCLUSIVE` transaction for each write. The comment explains this "prevents race condition between concurrent processes reading prev_hash and inserting." Explain the specific TOCTOU (Time-of-Check-Time-of-Use) vulnerability that a non-exclusive transaction would introduce for the hash chain.**

**Answer:** Without `BEGIN EXCLUSIVE`, Process A reads `prev_hash = H_N` (check), then Process B also reads `prev_hash = H_N` before A commits, and both insert entries claiming `prev_hash = H_N` (use). The chain now has two entries both linking to H_N, creating a branch. `verifyLogIntegrity()` expects a linear chain and will report both entries as tampered. `BEGIN EXCLUSIVE` locks the database file at the start of A's read, forcing B to wait until A's full read-compute-insert-commit sequence finishes.

**Reasoning:** The TOCTOU window is between the SELECT of `prev_hash` and the INSERT; `BEGIN EXCLUSIVE` collapses this window to zero.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.log()` ~line 182

---

**Q138. In `f11_write_audit_log.py`, the `_compute_entry_hash()` method computes `SHA-256(timestamp|level|event|module|user_id|metadata_json|prev_hash)` using `|` as a delimiter. What subtle collision attack could be mounted if the hash were computed over concatenated fields WITHOUT delimiters?**

**Answer:** Without delimiters, `hash("INFO" + "login")` and `hash("INF" + "Ologin")` produce identical input strings despite different field splits, allowing an attacker to craft a log entry whose concatenated fields match an unrelated legitimate entry's concatenation — producing the same hash and bypassing tamper detection. Delimiters prevent this by making field boundaries unambiguous.

**Reasoning:** Delimiter-free concatenation makes different (field-set, values) pairs potentially hash-identical; delimiters uniquely encode the field structure.

**Reference:** `code2/f11_write_audit_log.py` → `_compute_entry_hash()` ~line 106

---

**Q139. In `f11_write_audit_log.py`, the hash chain starts with `prev_hash = "GENESIS"` for the first entry. How does this GENESIS sentinel enable tamper detection for the very first log entry, and what would happen if an attacker deleted all log entries and started a fresh chain?**

**Answer:** The first entry's hash is computed over `prev_hash = "GENESIS"`, binding it to this known starting value. `verifyLogIntegrity()` begins its chain walk with `expected_prev_hash = "GENESIS"` and checks that the first entry's `prev_hash` matches — so any entry inserted at position 1 with a different predecessor is detected. If an attacker deletes all entries and inserts a new chain, the new first entry also starts with "GENESIS" and would pass chain verification — there is no external timestamp anchor to detect the reset, which is a limitation.

**Reasoning:** GENESIS provides a known chain anchor but cannot detect complete chain replacement; off-device log archiving would be needed for that guarantee.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.verifyLogIntegrity()` ~line 352

---

**Q140. In `f11_write_audit_log.py`, the `_encrypt_field()` method encrypts individual fields with AES-GCM, but the `entry_hash` and `prev_hash` fields are stored in PLAINTEXT (not encrypted). Why must these integrity fields remain in plaintext even though they contain metadata about log entries?**

**Answer:** `entry_hash` and `prev_hash` are computed over plaintext field values and must be verifiable without the encryption key (e.g., by an auditor or forensic investigator who doesn't have the log encryption key). If these fields were encrypted, `verifyLogIntegrity()` would require the decryption key to check chain integrity — defeating the purpose of having tamper detection that is independent of key availability.

**Reasoning:** Integrity metadata must be readable by anyone conducting a tamper check; encrypting it would tie integrity verification to key possession.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.log()` ~line 213

---

**Q141. In `f11_write_audit_log.py`, the `verifyLogIntegrity()` method decrypts fields before recomputing hashes. The comment explains "entry_hash was computed over plaintext, so we must decrypt first." If an attacker has the encryption key, could they forge a log entry that passes integrity verification? Explain your reasoning.**

**Answer:** Yes — an attacker with the encryption key can decrypt all fields, modify them, recompute valid SHA-256 hashes and a correct chain linkage, re-encrypt the modified fields with the same key, and write everything back. The hash chain provides tamper evidence only against attackers who lack the encryption key; key compromise breaks both confidentiality and integrity.

**Reasoning:** The chain is a cryptographic commitment to plaintext values, not a MAC; without key separation between the log encryption key and an auditor's signing key, the chain offers no protection to a keyholder.

**Reference:** `code2/f11_write_audit_log.py` → `verifyLogIntegrity()` ~line 335

---

**Q142. In `f11_write_audit_log.py`, the `_checkRotation()` method deletes the oldest log entries when count exceeds 10,000. What forensic problem does log rotation create, and what would be a more security-conscious approach to log management?**

**Answer:** Deleting the oldest entries destroys the forensic record of events that may pre-date a discovered security incident — exactly the events an investigator needs to reconstruct an attack timeline. A more security-conscious approach is to export (archive) old entries to a write-once off-device store (e.g., a WORM drive, remote syslog server, or signed archive file) before deleting them locally, preserving the chain hash of the last archived entry as an anchor.

**Reasoning:** Rotation without archiving creates a sliding window that destroys evidence; the security community calls this "log washing."

**Reference:** `code2/f11_write_audit_log.py` → `_checkRotation()` ~line 238

---

**Q143. In `f11_write_audit_log.py`, the `viewLogs()` method decrypts fields using `_decrypt_field()` but catches `json.JSONDecodeError` and `KeyError` for backward compatibility with "legacy plaintext fields." What security risk is introduced by treating decryption failures as "legacy plaintext" rather than as errors?**

**Answer:** An attacker who corrupts or replaces an encrypted field with plaintext text can cause `_decrypt_field()` to silently return the attacker-controlled plaintext as if it were the legitimate decrypted value. This masks tampering: what should be a detectable integrity failure is instead treated as a valid legacy entry, allowing the attacker to inject false log events that pass the integrity check.

**Reasoning:** Falling back to plaintext on parse failure conflates "old format" with "attacker-modified content," hiding tampering behind a compatibility shim.

**Reference:** `code2/f11_write_audit_log.py` → `_decrypt_field()` ~line 146

---

**Q144. In `f11_write_audit_log.py`, the `AuditLogger.__init__()` calls `_initialize()` which runs `ALTER TABLE audit_log ADD COLUMN prev_hash TEXT` if the column is missing. This is a backward-compatible schema migration. What happens to the `prev_hash` values for all existing rows after this migration, and does this break the hash chain verification?**

**Answer:** SQLite's `ALTER TABLE ADD COLUMN` sets the new column to `NULL` for all existing rows. In `verifyLogIntegrity()`, the code uses `prev_hash or "GENESIS"` when computing expected_prev_hash, so a `NULL` prev_hash is treated as "GENESIS". This means all pre-migration entries will have their chain linkage recomputed against "GENESIS" rather than the actual predecessor hash, causing every entry after the first to appear tampered — the migration does break chain verification for legacy entries.

**Reasoning:** The NULL default for new columns is unavoidable in SQLite; the chain is irrecoverably broken for pre-migration data unless the hash computation treats NULL as the previous entry's hash, not GENESIS.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger._initialize()` ~line 89

---

**Q145. In `f11_write_audit_log.py`, the global singleton `_logger_instance` is created lazily by `_getLogger()` with a hardcoded path `"./code2/test_output/audit.db"`. What is the risk of this hardcoded path in production, and how does the production code in `sffs_core.py` avoid this problem?**

**Answer:** The hardcoded path writes the audit database to a relative path from the working directory, which in production is likely the application's source directory rather than the USB's `sffs_data/logs/` directory — so audit logs would appear on the host's hard drive rather than the USB, violating portability and potentially leaving forensic evidence on the host. The production code in `sffs_core.py` initializes `AuditLogger` directly with an absolute path derived from `initDriveDetection()` results, bypassing the default singleton.

**Reasoning:** Hardcoded relative paths are a deployment hazard; the production code explicitly passes the USB-relative path to avoid this.

**Reference:** `code2/f11_write_audit_log.py` → `_getLogger()` ~line 406

---

**Q146. In `f12_emergency_lock.py`, the `emergencyLock()` function wraps each step in an independent `try/except` block. Why is it critical that a failure in step 3 (memory wipe) does not prevent execution of step 4 (sandbox destroy) and step 5 (session termination)?**

**Answer:** Each step defends against a different attack vector: memory wipe removes keys from RAM, sandbox destroy removes decrypted files from disk, session termination prevents reuse of the session token. A crash in step 3 (e.g., a null wipe target) must not stop step 4 from deleting plaintext files — the goal is to complete as much of the lockdown as possible in the face of partial failures. Chaining steps without isolation would cause a single failure to leave subsequent protections unapplied.

**Reasoning:** Independent try/except blocks implement a "best-effort lockdown" pattern — partial lockdown is better than no lockdown.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` ~line 100

---

**Q147. In `f12_emergency_lock.py`, step 7 calls `sys.exit(1)` with exit code 1 rather than 0. The comment explains "a non-zero code lets callers and monitoring tools distinguish a successful clean exit from an emergency lock trigger." What monitoring infrastructure would use this exit code, and how does using `sys.exit()` rather than `raise SystemExit()` help testing?**

**Answer:** Process supervisors (systemd, Windows Task Scheduler, Docker), shell scripts checking `$?`, and monitoring agents (Nagios, Prometheus process exporters) all use exit codes to determine why a process stopped — code 1 signals abnormal termination and can trigger alerts or automatic restart policies. `sys.exit()` can be monkey-patched in tests by replacing `sys.exit` with a mock, whereas `raise SystemExit()` directly throws an exception that bypasses the monkey-patch and terminates the test process.

**Reasoning:** `sys.exit()` as a function call is interceptable in test environments; the exit code carries semantic meaning to any process monitoring infrastructure.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` ~line 148

---

**Q148. In `f12_emergency_lock.py`, the `EMERGENCY_ACTIVE = False` flag is a module-level global variable. What threading issue exists with reading and setting this flag without a lock, and why might this not matter in the emergency lock context?**

**Answer:** Without a lock, a thread reading `EMERGENCY_ACTIVE` concurrently with another thread setting it could see a stale value due to CPU cache coherency or Python's GIL release timing — in theory, two threads could both pass the flag check and both execute emergency procedures. In practice, the GIL serializes Python bytecode operations, and CPython's global assignment to a module variable is effectively atomic at the bytecode level. More importantly, duplicate execution of `emergencyLock()` (which calls `sys.exit(1)`) is idempotent — the second call never completes.

**Reasoning:** The race is benign because the worst outcome (double invocation of emergency lock) terminates the process anyway, and `sys.exit(1)` in the first call stops the second.

**Reference:** `code2/f12_emergency_lock.py` → `EMERGENCY_ACTIVE` ~line 63

---

**Q149. In `f12_emergency_lock.py`, the audit log write (step 6) happens AFTER the sandbox destruction (step 4) and session termination (step 5). Why is this ordering important, and what information does the audit log record that could not be recorded if logging happened first?**

**Answer:** Writing the log last ensures the entry records whether the sandbox was destroyed and the session was terminated — information only known after those steps complete. If logging happened first, the log entry would be speculative about steps that had not yet run and might not run (e.g., if sandbox destruction failed). Logging last also means the log entry is the final confirmation that the lock sequence was attempted, even partially, which is the most useful forensic signal.

**Reasoning:** The log entry's value is as a completion receipt; writing it last maximizes its informational content about what actually happened.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` ~line 135

---

**Q150. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` function uses polling with `check_interval = 0.5` seconds rather than kernel filesystem events (inotify on Linux). What is the maximum theoretical latency between USB removal and lock trigger with this approach, and when would this latency be unacceptable?**

**Answer:** The maximum theoretical latency is just under 1 polling interval = 500 ms (the check runs, USB is present; user pulls USB; next check runs up to 500 ms later and detects absence). This latency would be unacceptable in a scenario where the attacker pulls the USB and immediately attempts to read decrypted files still in RAM or in a memory-mapped region — 500 ms is sufficient for a local attacker to read many megabytes of decrypted data before the lock fires.

**Reasoning:** For RAM-based attacks, the 500 ms window is dangerous; for persistent disk-based attacks it is less critical since sandbox wipe takes longer anyway.

**Reference:** `code2/f12_emergency_lock.py` → `setupUSBRemovalDetection()` ~line 168

---

**Q151. In `f12_emergency_lock.py`, the `setupIdleTimeout()` function uses a `global last_activity` variable updated by `resetIdleTimer()`. What is the threading safety of this approach — could a race condition cause the idle timer to fire even though the user was recently active?**

**Answer:** `last_activity = time.time()` is a single attribute assignment, which is atomic at CPython's bytecode level due to the GIL. However, the idle monitor reads `last_activity`, computes `idle_time`, and then makes the lockout decision — if a user activity calls `resetIdleTimer()` between the read and the comparison, the monitor sees the old value and may fire spuriously if the timing is extremely tight (within one bytecode instruction boundary). In practice this is rare but theoretically possible on heavily loaded multi-core systems where the GIL is released frequently.

**Reasoning:** The GIL makes the assignment atomic but not the read-compare-decide sequence, leaving a narrow race window.

**Reference:** `code2/f12_emergency_lock.py` → `setupIdleTimeout()` / `resetIdleTimer()` ~line 228

---

**Q152. In `f12_emergency_lock.py`, the `usbMonitor()` inner function in `setupUSBRemovalDetection()` checks `if not usb_root.exists()`. What false-positive scenario could trigger this condition on a network drive or a slow filesystem, causing an erroneous emergency lock?**

**Answer:** On a network-mounted drive (SMB/NFS) or a slow USB hub, a transient network hiccup, device sleep mode, or filesystem stall can cause `path.exists()` to return `False` (or raise an `OSError`) even though the device is still physically connected. The current code does not distinguish between a temporary mount failure and true removal, so a brief network blip would trigger an irreversible emergency lock — locking the user out unnecessarily.

**Reasoning:** A single failed `exists()` poll is too coarse a signal for removal detection on unreliable transports; a confirmation count (N consecutive failures) would reduce false positives.

**Reference:** `code2/f12_emergency_lock.py` → `usbMonitor()` inner function ~line 171

---

**Q153. In `f07_create_isolated_sandbox.py`, the `secureWipeFile()` function does nothing if the file does not exist (`if not file_path.exists()`). What TOCTOU (time-of-check time-of-use) race condition exists between the existence check and the subsequent `stat()` call, and why is this acceptable in this context?**

**Answer:** Between the `exists()` check (time-of-check) and the `stat()` call (time-of-use), another process or thread could delete the file, causing `stat()` to raise `OSError`. However, the code already handles `OSError` from `stat()` with a `try/except` that returns early, so the race resolves gracefully. The context is a secure wipe operation, not a security enforcement point — a file that disappears before wiping is no longer present to leak, so the race outcome is benign.

**Reasoning:** The TOCTOU gap here leads to a gracefully handled no-op, not to a security bypass; the worst case is an already-deleted file, which is the desired end state anyway.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `secureWipeFile()` ~line 330

---

**Q154. In `f09_authenticate_user.py`, the `initAuthDatabase()` function uses `CREATE TABLE IF NOT EXISTS`. What happens if the database file already exists with an incompatible schema (e.g., missing columns), and how would this affect the authentication system at runtime?**

**Answer:** `CREATE TABLE IF NOT EXISTS` silently succeeds without modifying the existing table, so missing columns from an old schema remain absent. At runtime, any SQL query referencing a missing column (e.g., `locked_until`) would raise `sqlite3.OperationalError: table users has no column named locked_until`, crashing the authentication function. There is no schema migration beyond `_initialize()`'s `ALTER TABLE ADD COLUMN prev_hash` in the audit logger — the auth database has no equivalent migration.

**Reasoning:** Schema version enforcement or migration logic is absent from the auth module; incompatible schemas produce runtime errors rather than graceful upgrades.

**Reference:** `code2/f09_authenticate_user.py` → `initAuthDatabase()` ~line 71

---

**Q155. In `f10_monitor_process.py`, on Windows, `kernel32 = ctypes.windll.kernel32` is executed at import time (line 35). What happens when this module is imported on Linux, and why is the conditional `if platform.system() == "Windows":` guard around the `kernel32` assignment important?**

**Answer:** The guard at line 34 (`if platform.system() == "Windows":`) assigns `kernel32 = ctypes.windll.kernel32` only on Windows; on Linux, `kernel32 = None` is assigned instead. Without this guard, importing the module on Linux would raise `AttributeError: module 'ctypes' has no attribute 'windll'` because `ctypes.windll` is a Windows-only attribute, making the entire `f10_monitor_process` module unusable on Linux — including for CI and testing.

**Reasoning:** The guard is essential for cross-platform portability; `ctypes.windll` does not exist on Linux or macOS.

**Reference:** `code2/f10_monitor_process.py` → module level ~line 34

---

**Q156. In `f11_write_audit_log.py`, the `log()` method has a retry loop that retries `BEGIN EXCLUSIVE` up to 3 times with linear back-off (0.1s, 0.2s). What scenario causes `sqlite3.OperationalError` during `BEGIN EXCLUSIVE`, and why is 3 retries sufficient for a USB-portable single-user application?**

**Answer:** `BEGIN EXCLUSIVE` raises `OperationalError: database is locked` when another connection (from a different thread or process) already holds a write lock on the SQLite file. In a single-user USB application with the `threading.Lock` serializing same-process writes, this error only occurs when a second OS process (e.g., a backup script or a briefly overlapping SFFS instance) has the database open. Three retries over 0–200 ms is sufficient because such contention is transient and brief; sustained contention would indicate a misconfiguration rather than a normal operating condition.

**Reasoning:** Single-user portable apps rarely have genuine concurrent writers; short linear back-off resolves transient lock conflicts without the complexity of full exponential back-off.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.log()` ~line 180

---

**Q157. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` function calls itself recursively for subdirectories (`secureWipeDirectory(dir_path)`). What risk of unbounded recursion exists, and how deep could the sandbox directory tree legitimately grow?**

**Answer:** A symlink loop or an adversarially crafted deep directory tree inside the sandbox could cause unbounded recursion and a Python `RecursionError`. Legitimately, the sandbox has three fixed subdirectories (`decrypted/`, `temp/`, `keys_runtime/`) with no enforced depth limit for files placed inside them by the user — so a deeply nested decrypted archive could create many subdirectory levels. In practice the default Python recursion limit (~1000) would be exhausted by a directory tree deeper than ~500 levels.

**Reasoning:** The code has no depth guard or cycle detection; a symlink loop or adversarial tree would exhaust the call stack.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `secureWipeDirectory()` ~line 314

---

**Q158. In `f12_emergency_lock.py`, the five trigger types are: `USB_REMOVED`, `DEBUGGER_DETECTED`, `TIMEOUT`, `MANUAL`, `MAX_FAILURES`. For which of these triggers should the audit log entry be written before `sys.exit(1)` is called, and for which might a post-exit log write be too late?**

**Answer:** For all five triggers, logging happens in step 6 immediately before `sys.exit(1)` in step 7, which is correct — the log write occurs while the process is still running. `USB_REMOVED` is the most time-critical: if the USB is removed, the audit database on the USB may be unmounted before step 6 completes, making the log write silently fail. `DEBUGGER_DETECTED` and `MAX_FAILURES` should always succeed in logging. `TIMEOUT` and `MANUAL` are the least urgent and are most likely to log successfully.

**Reasoning:** The risk is specifically for USB_REMOVED, where the log storage medium may be gone before the write completes; all other triggers have stable storage available.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` ~line 135

---

**Q159. In `f09_authenticate_user.py`, the `PasswordHasher` is instantiated with `time_cost=3, memory_cost=65536, parallelism=4` but without specifying `hash_len`. What is the default `hash_len` for the argon2-cffi `PasswordHasher`, and does omitting it affect security compared to explicitly specifying 32 bytes?**

**Answer:** The argon2-cffi `PasswordHasher` defaults to `hash_len=16` (16 bytes = 128 bits). For password verification purposes, 128 bits provides negligible practical difference from 256 bits — with Argon2id's memory-hardness, the cost of cracking is dominated by the Argon2 computation cost, not the hash output length. However, if the hash output were used as a key (not the case here), 16 bytes would be weaker than 32 bytes. Explicitly specifying `hash_len=32` would be marginally more defensive but is not functionally important for password storage.

**Reasoning:** Hash length matters for key derivation but is largely irrelevant for password verification; the Argon2 parameters dominate security.

**Reference:** `code2/f09_authenticate_user.py` → `PasswordHasher` instantiation ~line 185

---

**Q160. In `f10_monitor_process.py`, the `ProcessMonitor.stop()` method only sets `_stop_event` without waiting for the thread to terminate (`join()`). What happens if code calls `stop()` and then immediately checks `threat_detected` — could a race condition produce a false negative?**

**Answer:** Yes — after `stop()` returns, the monitoring thread may still be in the middle of its final loop iteration, executing `isDebuggerPresent()` or `checkSuspiciousProcesses()`. If a threat is detected in that final iteration, `_handleThreat()` sets `threat_detected` after `stop()` has already returned, so code that checks `threat_detected` immediately after `stop()` might see `False` even though a threat was detected moments later. Adding `thread.join()` after `stop()` would eliminate this race.

**Reasoning:** Without `join()`, there is a window between `stop()` returning and the thread actually completing its last check where a threat flag could be set but not yet visible.

**Reference:** `code2/f10_monitor_process.py` → `ProcessMonitor.stop()` ~line 189

---

**Q161. In `f07_create_isolated_sandbox.py`, the function `_wipe_stale_sandboxes()` silently ignores all exceptions with `except Exception: pass` in the per-sandbox cleanup. What forensic information is lost by swallowing these exceptions, and how should this be improved in production code?**

**Answer:** Swallowing exceptions loses information about which stale sandboxes failed to wipe and why (e.g., permission denied, locked file, I/O error on failing USB), preventing post-incident analysis of whether sensitive plaintext was successfully removed. In production, exceptions should be logged to the audit log at WARN level with the sandbox path and error message, allowing operators to identify persistent stale sandboxes that may still contain sensitive data.

**Reasoning:** Best-effort cleanup is acceptable, but silent failure of a security-critical operation (stale plaintext removal) should always be recorded.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `_wipe_stale_sandboxes()` ~line 66

---

**Q162. In `f09_authenticate_user.py`, the `terminateSession()` function deletes the session row from the database. What happens if `terminateSession()` is called with a `session_token` that does not exist (e.g., already expired), and is this behavior safe?**

**Answer:** `DELETE FROM sessions WHERE session_token = ?` is idempotent on SQLite — if no row matches, zero rows are deleted and no error is raised. The function completes successfully with no exception. This is safe: double-terminating or terminating an already-expired session has no effect on the database state, and there is no path by which a missing token causes unauthorized access.

**Reasoning:** SQL DELETE on a non-existent row is a safe no-op; the function's safety comes from the fact that "session doesn't exist" is equivalent to "session already invalidated."

**Reference:** `code2/f09_authenticate_user.py` → `terminateSession()` ~line 320

---

**Q163. In `f11_write_audit_log.py`, the `AuditLogger` constructor accepts an optional `encryption_key: bytes = None`. When `None` is passed, log fields are stored in plaintext. What is the minimum viable key management scheme for production to ensure the audit log encryption key is not the same as the AES key used for file encryption?**

**Answer:** The production scheme should derive the audit log key separately from the master password using a different KDF purpose label (e.g., `HKDF(master_key, info="sffs-audit-log-v1")`) rather than reusing the file AES key. Using the same key for both audit log encryption and file encryption violates key separation — a compromise of one key immediately compromises both, and the keys have different rotation lifecycles.

**Reasoning:** Key separation via purpose-specific HKDF derivation is the standard pattern; reuse eliminates the defense-in-depth benefit of separate keys.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.__init__()` ~line 61

---

**Q164. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function operates on a `bytearray` in-place but does not return a new object — the caller's reference is modified. What Python memory model property makes this in-place modification work correctly when the `bytearray` is passed by reference?**

**Answer:** Python passes object references by value — the function receives a reference to the same `bytearray` object as the caller holds. Because `bytearray` is mutable, slice assignment `target[:] = ...` modifies the object's underlying buffer in place, and since the caller's variable also references the same object, the caller sees the modifications without any return value. This is different from immutable types where in-place modification is impossible.

**Reasoning:** Python's pass-by-object-reference model means in-place mutation of a mutable object is visible to all holders of a reference to that object.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` ~line 91

---

**Q165. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` returns a daemon thread. After `emergencyLock()` calls `sys.exit(1)`, what happens to the monitoring daemon thread, and why is it safe to exit without explicitly stopping the thread first?**

**Answer:** When `sys.exit(1)` is called, Python's interpreter shutdown begins; all daemon threads are killed without executing their remaining code or cleanup. The USB monitor daemon thread is terminated forcibly, which is safe because it holds no locks, has no open file handles of its own, and performs no cleanup that would leave data in an inconsistent state — its only action is to call the lock callback, which is irrelevant after `sys.exit(1)` has already been called.

**Reasoning:** Daemon threads are designed to be killed at process exit; the monitor thread has no resources that need explicit cleanup.

**Reference:** `code2/f12_emergency_lock.py` → `setupUSBRemovalDetection()` ~line 178

---

**Q166. In `f09_authenticate_user.py`, the `registerUser()` function returns `{"user_id": None, "status": "error", "message": "Username already exists"}` on duplicate username. Should the error message reveal whether the username exists? What user enumeration attack does this enable, and how would you redesign this response?**

**Answer:** Revealing "Username already exists" allows an attacker to enumerate valid usernames: they register with a target username and the distinct error message confirms the username is in use. A safer design returns a generic `"Registration failed — check your input"` message for all registration errors, preventing enumeration. The distinction between "username taken" and "invalid input" can be preserved in internal logs but should not be exposed to the caller.

**Reasoning:** Distinct error messages for different failure modes are a classic information leakage pattern in registration flows.

**Reference:** `code2/f09_authenticate_user.py` → `registerUser()` ~line 161

---

**Q167. In `f07_create_isolated_sandbox.py`, `uuid.uuid4()` is used to generate the `session_id` when none is provided. UUID4 is randomly generated. How many bits of entropy does UUID4 provide, and is this sufficient to prevent session ID collisions between simultaneous sessions?**

**Answer:** UUID4 has 122 bits of random entropy (128 bits minus 6 fixed version/variant bits). By the birthday paradox, collision probability among N UUIDs is approximately `N²/2^123`; for 1 million simultaneous sessions the probability is `10^12 / 10^37 ≈ 10^-25` — negligible. For a USB-portable single-user application with at most a few concurrent sessions, 122 bits of entropy is overwhelmingly sufficient.

**Reasoning:** 122-bit entropy provides collision resistance far beyond any realistic number of sessions in this application's threat model.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 95

---

**Q168. In `f10_monitor_process.py`, the Linux `checkSuspiciousProcesses()` list includes `"gdb"`, `"strace"`, `"ltrace"`, `"radare2"`, `"frida"`, `"valgrind"`. Which of these tools would appear as a child process of SFFS (and thus be most reliably detected), versus appearing as a separate process that attaches to SFFS?**

**Answer:** Tools launched to wrap SFFS from birth (parent-child relationship) would appear as a parent, not a child: `strace python main.py` makes `strace` the parent of SFFS. Tools that attach to an already-running process appear as separate processes: `gdb --pid <sffs_pid>`, `frida -p <sffs_pid>`, and `ltrace` in attach mode. Only `valgrind` always starts as the parent (it cannot attach). The process list scan detects all of them if they are visible in the process table, regardless of parent-child relationship.

**Reasoning:** Attachment tools run as separate processes; the name scan detects them either way, though a parent-process `strace` would have SFFS as a child rather than the reverse.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 108

---

**Q169. In `f11_write_audit_log.py`, the `viewLogs()` method queries with `ORDER BY log_id DESC` to return newest-first. What happens to the hash chain verification if `log_id` values are not monotonically increasing (e.g., due to log rotation deleting middle entries followed by new insertions)?**

**Answer:** `verifyLogIntegrity()` queries `ORDER BY log_id ASC` and walks the chain assuming each row's `prev_hash` points to the immediately preceding `log_id`. If rotation deletes middle entries, gaps appear and the `prev_hash` of an entry after the gap points to a hash that no longer exists in the database — `expected_prev_hash` will not match, causing all post-gap entries to be flagged as tampered even if untouched. This is a direct consequence of FIFO rotation breaking chain continuity.

**Reasoning:** The hash chain is designed for an append-only log; FIFO deletion severs the chain and makes integrity verification unreliable after rotation.

**Reference:** `code2/f11_write_audit_log.py` → `verifyLogIntegrity()` ~line 335

---

**Q170. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` uses `os.walk(directory)` with default `topdown=True` for the first pass (files) and `topdown=False` for the second pass (directories). Why must the directory removal pass use `topdown=False`?**

**Answer:** `dir_path.rmdir()` requires the directory to be empty before it can be removed. With `topdown=True`, parent directories are visited before their children; attempting to `rmdir` a parent before its subdirectories are removed would fail with "Directory not empty." `topdown=False` (bottom-up) visits leaf directories first, removes them, then moves up to their parents — each directory is already empty by the time `rmdir` is called on it.

**Reasoning:** Bottom-up traversal ensures the removal precondition (empty directory) is met at each step.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `secureWipeDirectory()` ~line 309

---

**Q171. In `f12_emergency_lock.py`, step 2 in the `emergencyLock()` function is documented as "Close all open file handles (best-effort)" but the comment says "Python does not offer a safe 'close all process handles' primitive." What operating system facilities could be used instead, and does the lack of handle closure create a specific data leak risk?**

**Answer:** On Linux, `os.closerange(3, resource.getrlimit(resource.RLIMIT_NOFILE)[0])` closes all file descriptors above stderr. On Windows, `NtQuerySystemInformation` or iterating process handles via the Win32 API can enumerate and close them. Without explicit handle closure, any open writable file descriptors (e.g., to the decrypted sandbox) remain open briefly, and the OS will flush their buffers to disk on close — potentially writing partially decrypted data to disk after the sandbox wipe has already run (a race between the wipe and any pending buffered writes).

**Reasoning:** Unflushed write buffers for open handles could land on disk after the wipe, creating a narrow window where data is recoverable.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` step 2 ~line 110

---

**Q172. In `f09_authenticate_user.py`, the `PasswordHasher` object `pw` is created fresh for each `authenticateUser()` call (line 185). What is the performance impact of re-instantiating `PasswordHasher` per call versus creating it once at module load time?**

**Answer:** Creating `PasswordHasher()` is lightweight — it just stores configuration parameters and allocates no significant resources. The actual cost is in `pw.hash()` and `pw.verify()` which run the Argon2id algorithm (the 100 ms operation). Re-instantiating per call adds microseconds of Python object creation overhead, which is negligible compared to the 100 ms Argon2 computation. There is no meaningful performance difference between per-call and module-level instantiation.

**Reasoning:** `PasswordHasher` is a stateless configuration object; the expensive work is in the KDF itself, not the object creation.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 185

---

**Q173. In `f07_create_isolated_sandbox.py`, `subprocess.run(['icacls', ...], check=True, capture_output=True, stdin=subprocess.DEVNULL)` is used with `stdin=subprocess.DEVNULL`. Why is it important to redirect stdin to DEVNULL when running a security-critical subprocess?**

**Answer:** Without `stdin=DEVNULL`, the subprocess inherits the parent process's stdin, which could be an interactive terminal or a pipe. A malicious or interactive `icacls` version could prompt for confirmation or read credentials from stdin — allowing an attacker to inject input or for the process to hang waiting for input that never comes (DoS). Redirecting to DEVNULL ensures the subprocess has no input channel and cannot be interactively manipulated.

**Reasoning:** Closing stdin prevents the subprocess from reading attacker-controlled or unexpected input and prevents hangs on interactive prompts.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 122

---

**Q174. In `f11_write_audit_log.py`, the `_encrypt_field()` method generates a fresh 12-byte IV for every field encrypted in every log entry. In a system writing 10,000 log entries with 4 encrypted fields each, what is the total number of GCM IV values used, and how does this compare to the GCM IV birthday bound?**

**Answer:** Total IVs used: 10,000 × 4 = 40,000 IVs. The GCM birthday bound for a 96-bit nonce is 2^32 invocations (~4.3 billion) before nonce collision probability exceeds 1/(2^32). The probability of any collision among 40,000 IVs is approximately `40,000² / 2 / 2^96 ≈ 8×10^8 / 7.9×10^28 ≈ 10^-20` — astronomically small. The system is nowhere near the GCM nonce birthday bound.

**Reasoning:** 40,000 IVs from a 2^96 space faces negligible collision probability; the GCM birthday bound is not a concern at this scale.

**Reference:** `code2/f11_write_audit_log.py` → `_encrypt_field()` ~line 123

---

**Q175. In `f08_secure_memory_wipe.py`, after `secureMemoryWipe()` returns, the bytearray still exists in memory (filled with zeros). What additional step must the caller take to fully remove the reference from scope, and does CPython's reference counting guarantee immediate deallocation?**

**Answer:** The caller should delete all references to the bytearray: `del password_buf` (and any other variable referencing it). In CPython, reference counting does guarantee immediate deallocation when the reference count reaches zero — unlike Java's GC, CPython frees the object and its buffer immediately when `del` drops the last reference. However, if the bytearray was passed to other functions, copied, or stored in a container, those references must also be cleared before the memory is freed.

**Reasoning:** CPython's reference counting provides deterministic deallocation; the caller must ensure all references are dropped for immediate memory release.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` return ~line 109

---

**Q176. In `f09_authenticate_user.py`, the `sessions` table has no index on `session_token`. In `validateSession()`, the query `SELECT user_id, expires_at FROM sessions WHERE session_token = ?` performs a full table scan. At what session table size would this become a performance problem, and should `session_token` be indexed?**

**Answer:** SQLite full table scans on a local USB SSD are typically fast up to tens of thousands of rows. Performance would noticeably degrade above ~100,000 session rows (taking tens of milliseconds per validation). However, in a single-user system with 24-hour session expiry, the table should never accumulate more than a handful of rows; `terminateSession()` deletes rows on logout. An index on `session_token` would be a best practice defensive measure but is not practically necessary at this scale.

**Reasoning:** The session table stays tiny in a single-user system; an index is good practice but not a functional requirement here.

**Reference:** `code2/f09_authenticate_user.py` → `validateSession()` ~line 295

---

**Q177. In `f12_emergency_lock.py`, `last_activity = time.time()` is a module-level global. If `f12_emergency_lock` is imported by multiple modules (e.g., by `sffs_core.py`), do they share the same `last_activity` value, or does each import get its own copy? How does Python's import system handle this?**

**Answer:** Python's import system caches modules in `sys.modules` after the first import — every subsequent `import f12_emergency_lock` returns the same module object. All importers share the same module namespace, so `last_activity` is a single variable shared across all of `sffs_core.py`, `f09_authenticate_user.py`, and any other module that imports `f12_emergency_lock`. `resetIdleTimer()` updates the single shared `last_activity`, and the idle monitor reads the same shared value.

**Reasoning:** Module-level globals are singletons per process; Python's module cache ensures all importers reference the same object.

**Reference:** `code2/f12_emergency_lock.py` → `last_activity` ~line 64

---

**Q178. In `f10_monitor_process.py`, on Windows, `kernel32.IsDebuggerPresent()` is a well-known anti-debugging technique that advanced debuggers can bypass by patching the PEB (Process Environment Block) flag. What does this imply about the reliability of `isDebuggerPresent()` as a security control?**

**Answer:** `IsDebuggerPresent()` reads the `BeingDebugged` flag in the Process Environment Block (PEB); a debugger like x64dbg can simply patch this byte to 0 before the check runs, making it return `False` even while actively debugging. This means `isDebuggerPresent()` is easily bypassed by any competent attacker and should be treated as a deterrent against casual reverse engineering, not a reliable security barrier. The module docstring acknowledges this: "This is a defense-in-depth measure, not a guarantee."

**Reasoning:** PEB patching is a well-documented anti-anti-debugging technique; the control provides friction, not protection.

**Reference:** `code2/f10_monitor_process.py` → `isDebuggerPresent()` ~line 62

---

**Q179. In `f07_create_isolated_sandbox.py`, `shutil.rmtree(sandbox_path, ignore_errors=True)` is called after `secureWipeDirectory()`. Why might `shutil.rmtree()` fail even after the secure wipe, and what cleanup state remains if it does fail?**

**Answer:** `shutil.rmtree()` can fail if a file or directory is locked by another process (e.g., a virus scanner or indexer that opened a file during the wipe), if the directory contains reparse points or junctions on Windows, or if permissions prevent deletion. With `ignore_errors=True` the failure is silently swallowed. The remaining state is an empty (all-zeros) directory tree — the sensitive data has been overwritten, but the directory skeleton and empty files remain on disk, potentially revealing the sandbox's existence and structure to a forensic investigator.

**Reasoning:** After wiping, residual directory structure is a metadata leak but not a data leak; the actual sensitive content has been overwritten.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `destroySandbox()` ~line 214

---

**Q180. In `f11_write_audit_log.py`, the module level has a `_logger_instance = None` singleton. If `writeAuditLog()` is called from a `multiprocessing` worker process (not a thread), each worker process gets its own copy of `_logger_instance`. What database corruption could result from multiple processes writing to the same SQLite file without coordination?**

**Answer:** Each worker process creates its own `AuditLogger` with its own `threading.Lock` — but these locks are process-local and do not coordinate between processes. Two processes could simultaneously execute `BEGIN EXCLUSIVE` on the same SQLite file; while SQLite's own file-level locking serializes commits, the hash chain logic (read last hash, compute new hash, insert) is not atomic across processes — two processes could both read the same `prev_hash` and create a forked chain. Additionally, WAL-mode corruption can occur with multiple uncoordinated writers.

**Reasoning:** Process-local locks do not coordinate inter-process SQLite access; the hash chain's read-modify-insert must be atomic across all writers.

**Reference:** `code2/f11_write_audit_log.py` → `_getLogger()` ~line 401

---

**Q181. In `f09_authenticate_user.py`, `password_str = password.decode('utf-8')` is called in `registerUser()` before hashing. What error occurs if the bytearray contains non-UTF-8 bytes (e.g., from a binary paste), and how should the function handle this gracefully?**

**Answer:** `bytearray.decode('utf-8')` raises `UnicodeDecodeError` if the bytearray contains invalid UTF-8 byte sequences (e.g., a standalone `\xff` byte). The current code does not catch this, so the exception propagates to the caller as an unhandled error rather than a clean validation failure. The function should catch `UnicodeDecodeError` and re-raise it as a `ValueError("Password must be valid UTF-8 text")`, ensuring the password bytearray is still wiped in a `finally` block even on this error path.

**Reasoning:** Non-UTF-8 input is a user error that should produce a clean validation message, not an internal exception; and the bytearray must still be wiped even on the error path.

**Reference:** `code2/f09_authenticate_user.py` → `registerUser()` ~line 124

---

**Q182. In `f07_create_isolated_sandbox.py`, the `createIsolatedSandbox()` returns a dict containing the full `sandbox_path`, `decrypted_dir`, `temp_dir`, and `keys_runtime_dir`. If this dict is logged to the audit log, what information leakage risk arises?**

**Answer:** The full absolute paths reveal the session ID (embedded in `sandbox_{session_id}`), the USB mount point or temporary directory root (leaking where SFFS stores data), and the internal directory structure. An attacker who reads the audit log (or its plaintextversion if unencrypted) now knows exactly where to look on disk for decrypted files — the paths are a roadmap to the sandbox contents.

**Reasoning:** Logging full sandbox paths couples forensic records to operational secrets; only the session ID should be logged, not the full path.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` return ~line 175

---

**Q183. In `f10_monitor_process.py`, the `ProcessMonitor` thread runs as a daemon but `_handleThreat()` invokes `self.on_threat_detected` callback. If the callback blocks indefinitely (e.g., waiting for a GUI event), what happens to the threat response system?**

**Answer:** The monitoring loop breaks after `_handleThreat()` returns (or fails), but if the callback blocks indefinitely, `_handleThreat()` never returns — the monitor thread is stuck in the callback, `threat_detected` is set (correct), `_stop_event` is set (correct), but the monitoring loop never reaches its final `break`. The practical consequence is that the monitor daemon thread leaks until the process exits. Since `emergencyLock()` calls `sys.exit(1)`, the stuck thread is eventually killed by interpreter shutdown.

**Reasoning:** A blocking callback freezes the monitor thread but the threat is still flagged via the Event; process exit eventually resolves the stuck thread.

**Reference:** `code2/f10_monitor_process.py` → `_handleThreat()` ~line 183

---

**Q184. In `f09_authenticate_user.py`, the `initAuthDatabase()` function connects to the database and calls `conn.commit()` but does not verify that the WAL (Write-Ahead Logging) mode is appropriate for concurrent access. What SQLite journal mode would be better for a multi-reader scenario, and how would you enable it?**

**Answer:** WAL (Write-Ahead Logging) mode allows concurrent readers and one writer simultaneously, which is better than the default DELETE journal mode that blocks all readers during writes. To enable it: `conn.execute("PRAGMA journal_mode=WAL")` immediately after opening the connection. WAL mode also improves crash recovery and reduces write amplification. For a USB-portable single-user application, WAL mode is worthwhile for SFFS because audit logging and authentication can run concurrently from separate threads.

**Reasoning:** WAL mode's reader-writer concurrency model fits SFFS's multi-threaded access pattern better than the default exclusive-lock journaling mode.

**Reference:** `code2/f09_authenticate_user.py` → `initAuthDatabase()` ~line 78

---

**Q185. In `f12_emergency_lock.py`, `destroySandbox(sandbox_path)` is called in step 4. If the sandbox path no longer exists (e.g., it was already cleaned up by a previous emergency lock call), what happens in `destroySandbox()`, and is the error handled gracefully?**

**Answer:** In `destroySandbox()`, the first check is `if sandbox_path.exists()` — if the path does not exist, `secureWipeDirectory()` is skipped. Then `shutil.rmtree(sandbox_path)` is called, which raises `FileNotFoundError`; this is explicitly caught and returns `True` (the sandbox is treated as successfully gone). In `emergencyLock()`, step 4 also guards with `if sandbox_path and sandbox_path.exists()`, so the entire step is skipped if the path is already gone. Both layers handle this gracefully.

**Reasoning:** Both `destroySandbox()` and `emergencyLock()` guard against non-existent paths, making double-invocation safe.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` step 4 ~line 122; `code2/f07_create_isolated_sandbox.py` → `destroySandbox()` ~line 210

---

**Q186. In `f11_write_audit_log.py`, each encrypted field produces a JSON blob with `iv`, `ct`, and `tag`. The entire JSON blob is stored as a single SQLite TEXT column. What is the storage overhead per log entry when all four encrypted fields (`event`, `module`, `user_id`, `metadata`) are encrypted compared to plaintext storage?**

**Answer:** Each encrypted field JSON blob contains: 12-byte IV (base64 = 16 chars) + variable ciphertext (base64 ≈ 1.33× plaintext length) + 16-byte GCM tag (base64 = 24 chars) + JSON keys and braces (~30 chars overhead) ≈ 70 chars fixed overhead per field plus 1.33× the plaintext size. For four typical short fields (each ~20 plaintext chars → ~27 base64 chars), the overhead is approximately 4 × (70 + 27 - 20) = ~308 additional characters per entry versus plaintext. Total per-entry encrypted storage is roughly 400–500 bytes vs 100–150 bytes plaintext.

**Reasoning:** Each AES-GCM encryption adds a fixed ~70-char JSON envelope overhead plus base64 expansion, multiplied by four fields per entry.

**Reference:** `code2/f11_write_audit_log.py` → `_encrypt_field()` ~line 126

---

**Q187. In `f09_authenticate_user.py`, the password policy check (`len(password_str) < 12`, uppercase/lowercase/digit/special checks) is performed BEFORE hashing. What is the security implication of a policy check that leaks length information through timing (e.g., the check for a 1-character password is faster than for an 11-character password)?**

**Answer:** Policy checks like `len(password_str) < 12` return immediately for short passwords without running Argon2id, so an attacker submitting 1-character passwords sees a fast response (~1ms) while 12+ character passwords take ~100ms for hashing. This timing oracle reveals whether the password passed the length check, providing information about whether the attempted password had sufficient length — leaking policy structure to an attacker conducting online probing.

**Reasoning:** Pre-hash policy checks create a timing side-channel that reveals which policy constraint was violated before the expensive KDF runs.

**Reference:** `code2/f09_authenticate_user.py` → `registerUser()` ~line 125

---

**Q188. In `f07_create_isolated_sandbox.py`, `_wipe_stale_sandboxes()` uses `cutoff = 24 * 3600` seconds (24 hours) as the staleness threshold. Is 24 hours an appropriate threshold for a USB-portable security application? What threat arises from stale sandboxes that are only 1 hour old?**

**Answer:** 24 hours is too generous for a USB security application: a sandbox left from a crash 2 hours ago already contains stale decrypted plaintext that should have been wiped the moment the session ended. A 1-hour-old stale sandbox represents plaintext files that have been sitting unprotected for an hour — if the USB was briefly accessed by an unauthorized person, they had a 1-hour window to copy those files. A more appropriate threshold would be 15–30 minutes, or ideally, any sandbox whose process is not currently running.

**Reasoning:** The threat is not the age per se but the existence of unwiped decrypted files; a shorter threshold limits the exposure window after a crash.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `_wipe_stale_sandboxes()` ~line 47

---

**Q189. In `f10_monitor_process.py`, the `checkSuspiciousProcesses()` function checks processes by name and also checks the full executable path (`proc.exe()`) on Windows. What privilege is required to call `proc.exe()` on another user's process, and what exception is caught when this fails?**

**Answer:** On Windows, reading the executable path of a process owned by a different user typically requires `PROCESS_QUERY_INFORMATION` access right, which non-elevated (non-administrator) processes often lack for system or other-user processes. When access is denied, `psutil` raises `psutil.AccessDenied`, which is caught in the `except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess)` clause and silently skips that process.

**Reasoning:** `proc.exe()` requires cross-process read access; standard user processes lack this for privileged processes, making `AccessDenied` the expected failure mode.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 121

---

**Q190. In `f11_write_audit_log.py`, the `AuditLogger.log()` method returns `{"log_id": None, "timestamp": ..., "status": "error", "error": str(e)}` on failure rather than raising an exception. What is the security implication of silently swallowing logging errors — which categories of security events could go unrecorded?**

**Answer:** If the audit log write fails silently, security-critical events may go completely unrecorded: failed authentication attempts (masking brute-force attacks), emergency lock triggers (hiding attacker activity), file encrypt/decrypt operations (masking data exfiltration), and debugger detection events. The caller receives an error dict but if it doesn't check `result["status"]`, the failure is invisible. An attacker who can cause SQLite errors (e.g., by filling the USB drive) could suppress all audit evidence of their activity.

**Reasoning:** Silent logging failures let adversaries erase their tracks by disrupting the logging subsystem; callers must check the return status.

**Reference:** `code2/f11_write_audit_log.py` → `AuditLogger.log()` ~line 225

---

**Q191. In `f09_authenticate_user.py`, `cursor.execute("SELECT user_id, password_hash, failed_attempts, locked_until FROM users WHERE username = ?", (username,))` uses parameterized queries. Why are parameterized queries important here, and what SQL injection payload would succeed against a naive string-formatted query?**

**Answer:** Parameterized queries pass the username as a data value rather than interpolating it into the SQL string; the database driver handles escaping and type binding, making SQL injection structurally impossible. Against a naive `f"...WHERE username = '{username}'"`, the payload `admin' OR '1'='1` would produce `WHERE username = 'admin' OR '1'='1'`, returning all users and bypassing authentication. A more destructive payload like `'; DROP TABLE users; --` would delete the user database.

**Reasoning:** Parameterized queries eliminate SQL injection by construction; string formatting creates the classic injection vulnerability.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 191

---

**Q192. In `f12_emergency_lock.py`, when the `TIMEOUT` trigger fires, the module docstring says it is "graceful, can be resumed with re-authentication." But `emergencyLock()` calls `sys.exit(1)` for all trigger types. Is the "resumable" claim accurate, and what would need to change to make TIMEOUT truly resumable?**

**Answer:** The "resumable" claim is inaccurate as implemented — `sys.exit(1)` terminates the process for all triggers including TIMEOUT, requiring a full application restart and re-login. To make TIMEOUT truly resumable, the function would need to skip `sys.exit(1)` for TIMEOUT triggers, instead triggering a re-authentication dialog (lock screen), wiping only the in-memory session token and keys (not the sandbox), and resuming the session upon successful re-auth without destroying all work in progress.

**Reasoning:** A resumable lock preserves application state and the sandbox while re-validating identity; the current hard-exit implementation makes the docstring claim incorrect.

**Reference:** `code2/f12_emergency_lock.py` → `emergencyLock()` ~line 148

---

**Q193. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function returns a dict with `passes_completed` and `bytes_wiped`. What information should the caller use this return value for, and what is the risk of ignoring the return value?**

**Answer:** The caller should check `result["status"] == "wiped"` and `result["passes_completed"] == 3` to confirm all wipe passes completed successfully. The function can return `status: "error"` with `passes_completed < 3` if an exception occurred mid-wipe (e.g., a MemoryError during the random-bytes generation). Ignoring the return value means the caller proceeds as if the memory is wiped when it may only be partially zeroed — a critical gap if the error path left partially sensitive data in the buffer.

**Reasoning:** A partial wipe (1 or 2 passes) still leaves residual patterns from uncompleted passes; the caller must verify completion.

**Reference:** `code2/f08_secure_memory_wipe.py` → `secureMemoryWipe()` ~line 109

---

**Q194. In `f10_monitor_process.py`, `psutil.process_iter(["name", "exe"])` is called with attribute filters. Why is filtering attributes important for performance, and what would happen if `process_iter()` were called without any filters on a Windows system with thousands of processes?**

**Answer:** When attribute names are passed to `process_iter()`, psutil fetches only those attributes for each process in a single system call batch (via `psutil.Process.as_dict()`), minimizing per-process overhead. Without filters, `process_iter()` creates bare `Process` objects and defers attribute fetching to individual `proc.name()`, `proc.exe()` calls — each requiring a separate system call (e.g., `NtQuerySystemInformation`, `OpenProcess`, `QueryFullProcessImageName`). On Windows with 3,000+ processes, unfiltered iteration can take 2–5 seconds, making the 500 ms check interval meaningless.

**Reasoning:** Attribute pre-fetching batches system calls; per-attribute lazy fetching multiplies them, creating severe latency on process-heavy systems.

**Reference:** `code2/f10_monitor_process.py` → `checkSuspiciousProcesses()` ~line 98

---

**Q195. In `f07_create_isolated_sandbox.py`, `secureWipeDirectory()` recursively calls itself for subdirectories. Given the sandbox structure (`decrypted/`, `temp/`, `keys_runtime/`), trace through the full recursion order that occurs when `destroySandbox()` is called on a sandbox containing files in each subdirectory.**

**Answer:** `destroySandbox()` calls `secureWipeDirectory(sandbox_root)`. Pass 1 (topdown=True, files): walks `decrypted/`, `temp/`, `keys_runtime/` and wipes all files in each (3-pass overwrite + unlink). Pass 2 (topdown=False, directories): visits subdirs bottom-up; for each subdir `secureWipeDirectory(subdir)` is called recursively (which finds no files remaining), then `dir_path.rmdir()` removes the now-empty subdir. Order: recursion on `decrypted/` → rmdir `decrypted/`; recursion on `temp/` → rmdir `temp/`; recursion on `keys_runtime/` → rmdir `keys_runtime/`. Then `destroySandbox()` calls `shutil.rmtree(sandbox_root)` to remove the root.

**Reasoning:** The two-pass walk separates file wiping (topdown) from directory removal (bottom-up), ensuring correct ordering.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `secureWipeDirectory()` ~line 275

---

**Q196. In `f09_authenticate_user.py`, the `_DUMMY_HASH` is computed once at import time. If the module is imported in a subprocess worker (e.g., `isolated_worker.py`), the Argon2 hash is recomputed on every worker spawn. What is the performance impact of this, and how could it be optimized?**

**Answer:** Each worker spawn that imports `f09_authenticate_user` triggers a fresh Argon2id hash computation (~100 ms with `time_cost=3, memory_cost=65536`). If `isolated_worker.py` spawns frequently, this adds 100 ms to every worker startup. The optimization is to pre-compute `_DUMMY_HASH` once in the main process and pass it as an environment variable or initializer argument to worker processes, or to use Python's `multiprocessing` initializer hook to share it without recomputation.

**Reasoning:** Module-level Argon2 computation at import time scales linearly with worker spawn frequency; a shared pre-computed value eliminates this cost.

**Reference:** `code2/f09_authenticate_user.py` → `_DUMMY_HASH` ~line 57

---

**Q197. In `f11_write_audit_log.py`, the `verifyLogIntegrity()` function checks both hash correctness AND chain linkage (`chain_ok = (prev_hash or "GENESIS") == expected_prev_hash`). Why is checking both conditions necessary — what specific tampering would pass the hash check but fail the chain check?**

**Answer:** An attacker could insert a new fabricated log entry with a correctly computed `entry_hash` over its own fields and a `prev_hash` pointing to some earlier entry (not the immediately preceding one), creating a "shortcut" in the chain that skips entries they deleted. The hash check (`computed_hash == stored_hash`) would pass for the fabricated entry because its own hash is internally consistent. The chain check (`prev_hash == expected_prev_hash`) would fail because the expected predecessor (the entry that was deleted) is missing — revealing the gap.

**Reasoning:** Hash-only verification catches field modification; chain linkage verification catches insertion/deletion attacks that preserve per-entry hash consistency.

**Reference:** `code2/f11_write_audit_log.py` → `verifyLogIntegrity()` ~line 377

---

**Q198. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` creates a daemon thread with `thread = threading.Thread(target=usbMonitor, daemon=True)`. If the main process calls `emergencyLock()` due to `TIMEOUT` and then `sys.exit(1)`, does the USB monitor thread cleanly stop? What race condition exists between the thread's final check and the process exit?**

**Answer:** The USB monitor daemon thread does not stop "cleanly" — `sys.exit(1)` begins interpreter shutdown which kills all daemon threads immediately without running their remaining code. A race exists: if the USB monitor is in the middle of `usb_root.exists()` when `sys.exit(1)` fires, the OS call may be interrupted mid-execution. On Linux this is safe (the OS cleans up the interrupted syscall); on Windows, an interrupted `PathFileExists` call may leave a brief file handle open. Neither causes lasting harm since the process is exiting.

**Reasoning:** Daemon thread death by interpreter shutdown is abrupt but safe; the OS cleans up any kernel resources the interrupted thread held.

**Reference:** `code2/f12_emergency_lock.py` → `setupUSBRemovalDetection()` ~line 167

---

**Q199. In `f07_create_isolated_sandbox.py`, the Windows `icacls` command grants permissions with `(OI)(CI)F` (Object Inherit, Container Inherit, Full Control). What do OI and CI mean in terms of how permissions are inherited by files and subdirectories created inside the sandbox after it is set up?**

**Answer:** `(OI)` (Object Inherit) means the ACE is inherited by files created inside the directory — new files automatically get the same grant. `(CI)` (Container Inherit) means the ACE is inherited by subdirectories created inside the directory — new subdirectories also inherit the grant. Together, `(OI)(CI)F` grants the owner full control on the sandbox root and automatically propagates that grant to all files and subdirectories subsequently created inside it, ensuring new content is also owner-only without requiring additional `icacls` calls.

**Reasoning:** OI + CI together implement transitive permission inheritance, covering both files (OI) and directories (CI) created after the initial ACL setup.

**Reference:** `code2/f07_create_isolated_sandbox.py` → `createIsolatedSandbox()` ~line 121

---

**Q200. In `f09_authenticate_user.py`, the `authenticateUser()` function checks `if locked_until and locked_until > now` using ISO string comparison. What happens if `locked_until` is stored in a format that is NOT ISO 8601 (e.g., due to locale settings affecting `datetime.now().isoformat()`), and how would you make this comparison timezone-aware and format-agnostic?**

**Answer:** If `locked_until` were stored in a locale-specific format (e.g., `"07/06/2026 14:30:00"`) while `now` is ISO (`"2026-06-07T14:30:00"`), lexicographic comparison would produce incorrect results — `"07/..."` sorts before `"2026..."` alphabetically, making all lockouts appear expired. The fix is to store and compare as `datetime` objects: `datetime.fromisoformat(locked_until) > datetime.now()`, optionally with timezone awareness by using `datetime.now(tz=timezone.utc)` and storing UTC ISO timestamps consistently.

**Reasoning:** String comparison only works for ISO 8601; parsing to `datetime` objects makes the comparison format-agnostic and enables timezone awareness.

**Reference:** `code2/f09_authenticate_user.py` → `authenticateUser()` ~line 219
