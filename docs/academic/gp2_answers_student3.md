# GP2 Answers — Student 3 (UI / Cloud, Q201–Q300)

---

**Q201. In `f13_init_drive_detection.py`, the `initDriveDetection()` function uses `sys.argv[0]` to resolve the application directory. Why is `sys.argv[0]` preferred over `__file__` for determining the USB root, and what edge case arises when the application is run as a frozen executable (e.g., PyInstaller)?**

**Answer:** `sys.argv[0]` reflects the entry-point script (e.g., `main-code/main.py`) so all modules agree on one application root regardless of which `.py` file is executing. `__file__` would resolve to the individual module file (`code3/f13_...py`), giving a different parent. In a PyInstaller frozen executable, `__file__` may not exist or may point inside the bundle's temp directory, whereas `sys.argv[0]` still points to the real executable path on the USB.

**Reasoning:** A single, consistent application root prevents "split-brain" paths where keys end up on a different drive than logs.

**Reference:** `code3/f13_init_drive_detection.py` → `_resolved_script_parent()` ~line 33

---

**Q202. In `f13_init_drive_detection.py`, the `_linux_mount_root()` function iterates over `psutil.disk_partitions(all=False)` and returns the mount point with the longest prefix match for the given path. Why is the "longest prefix match" strategy needed rather than just finding any partition that matches?**

**Answer:** On Linux, multiple partitions can be mounted under each other (e.g., `/` and `/media/user/USB`). A file on `/media/user/USB/sffs` matches both `/` and `/media/user/USB`; the longest match (`/media/user/USB`) is the actual filesystem the file lives on. Returning any matching partition would risk treating a USB file as being on the root filesystem.

**Reasoning:** The longest-prefix rule mimics the kernel's own mount resolution, guaranteeing the correct volume is identified.

**Reference:** `code3/f13_init_drive_detection.py` → `_linux_mount_root()` ~line 42

---

**Q203. In `f13_init_drive_detection.py`, when `is_removable` is `False`, the function issues a `UserWarning` and falls back to the repository root rather than the OS volume root. What production misconfiguration could silently cause `sffs_data/` to be created on the host hard drive instead of the USB stick?**

**Answer:** If the partition opts reported by `psutil` do not include `"removable"` — which happens when some USB controllers or Linux kernel versions omit that flag — `is_removable` is `False` even for a real USB drive. The fallback then places `sffs_data/` under the app directory on the local disk, potentially leaving sensitive key material on the host machine.

**Reasoning:** The `UserWarning` is swallowed silently in production GUI contexts where `stderr` is not visible, making this failure mode hard to detect.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 114

---

**Q204. In `f13_init_drive_detection.py`, the `getAvailableSpace()` function uses `psutil.disk_usage(str(path))`. Why must the path be converted to a string (`str(path)`) rather than passed as a `Path` object, and what does `psutil.disk_usage()` return that cannot be inferred from the `Path.stat()` method alone?**

**Answer:** Older `psutil` versions (pre-5.x) do not accept `pathlib.Path` objects and raise `TypeError`; `str(path)` ensures compatibility. `psutil.disk_usage()` returns filesystem-level total, used, and free bytes for the entire volume; `Path.stat()` only returns metadata (size, timestamps) for a single file or directory, not the underlying partition's free space.

**Reasoning:** Free space is needed to warn the user before encryption fails mid-operation due to a full USB drive.

**Reference:** `code3/f13_init_drive_detection.py` → `getAvailableSpace()` ~line 89

---

**Q205. In `f13_init_drive_detection.py`, the `initDriveDetection()` function creates six subdirectories (`data_dir`, `keys_dir`, `sandbox_dir`, `logs_dir`, `config_dir`, `backups_dir`) using `mkdir(parents=True, exist_ok=True)`. Why does creating these directories at startup prevent race conditions in subsequent modules that assume their existence?**

**Answer:** If each module created its own directory on first use, two modules starting concurrently could both execute the `mkdir` check at the "directory does not exist" state and then race to create it. By having a single initializer run before any worker threads or subprocesses start, all directories are guaranteed to exist before any module tries to write to them.

**Reasoning:** Centralised directory creation also enforces a single canonical path map, preventing one module from creating `sffs_data/keys` while another uses `sffs_data/Keys` on a case-insensitive filesystem.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 146

---

**Q206. In `f13_init_drive_detection.py`, the `monitorUSBPresence()` function polls `usb_root.exists()` every 0.5 seconds. How does this polling-based approach compare to kernel event–based monitoring (e.g., using `pyudev` on Linux or `ReadDirectoryChangesW` on Windows) in terms of latency, reliability, and CPU usage?**

**Answer:** Polling has up to 0.5 s latency per removal event, uses a small but constant CPU slice every half-second, and works identically on all platforms without extra dependencies. Kernel event–based monitoring (`pyudev`/`ReadDirectoryChangesW`) delivers near-zero latency and near-zero CPU while idle, but requires platform-specific code and additional dependencies; `pyudev` also needs `udev` running, which may not be available in all Linux environments.

**Reasoning:** For SFFS's USB-portable use case, 0.5 s latency is acceptable; polling's simplicity and cross-platform nature outweigh the small CPU cost.

**Reference:** `code3/f13_init_drive_detection.py` → `monitorUSBPresence()` ~line 158

---

**Q207. In `f13_init_drive_detection.py`, the daemon thread in `monitorUSBPresence()` is named `"SFFS-USBWatch"`. Why is naming threads in Python important for debugging, and what tools would you use to inspect running thread names in a crashed Python application?**

**Answer:** Named threads appear in stack traces, debugger listings, and log entries, making it immediately clear which thread triggered a problem rather than seeing generic `Thread-3`. For a crashed Python application, `faulthandler` dumps all thread stacks with their names; `gdb` with the Python extension (`py-bt` per thread), `py-spy`, and `pyrasite` can also enumerate live or post-crash thread names.

**Reasoning:** In security-critical code, knowing that "SFFS-USBWatch" fired the emergency callback is essential for post-incident forensics.

**Reference:** `code3/f13_init_drive_detection.py` → `monitorUSBPresence()` ~line 181

---

**Q208. In `f13_init_drive_detection.py`, the `_partition_for_path()` function returns `(device, is_removable, opts)`. On Linux, `is_removable` is determined by whether `"removable"` appears in partition opts. How reliable is this approach on Linux where the `opts` field may not consistently report removability across different kernel versions and USB controllers?**

**Answer:** Reliability is inconsistent: many Linux kernels and USB Mass Storage drivers do not set the `removable` bit in the mount options exposed by `psutil`. A more reliable method would be to read `/sys/block/<dev>/removable` directly. The current approach may silently fall back to development mode on a legitimate USB stick if the driver omits the flag.

**Reasoning:** This is documented as a known limitation; the fallback path emits a `UserWarning` so operators can detect it during testing.

**Reference:** `code3/f13_init_drive_detection.py` → `_partition_for_path()` ~line 55

---

**Q209. In `f14_ui_dashboard.py`, the `apply_sffs_theme()` function applies a dark stylesheet globally to the `QApplication`. Why is a dark theme specifically named in the docstring as "high-contrast," and what accessibility concern does this raise for users with certain visual impairments?**

**Answer:** Dark-background / light-text themes have high luminance contrast between foreground text and background, which benefits users with low contrast sensitivity. However, for users with certain forms of color blindness (e.g., achromatopsia) or photosensitivity, dark themes with vivid accent colors (like the red `#f28b82` and yellow `#fdd663` used for security alerts) may not be distinguishable. The theme also uses color as the sole indicator for security severity, violating WCAG 1.4.1 (use of color).

**Reasoning:** Screen readers and system high-contrast mode override application stylesheets, so the security color labels may not convey their meaning to all users.

**Reference:** `code3/f14_ui_dashboard.py` → `apply_sffs_theme()` ~line 40

---

**Q210. In `f14_ui_dashboard.py`, the `DragDropZone` class emits `file_dropped = pyqtSignal(str)` when a file is dropped. The signal payload is a `str` path. What security check is missing before emitting the signal — what malicious input could an attacker provide by constructing a specially crafted file URL?**

**Answer:** No path validation is performed before emitting. A file URL could resolve to a path outside the USB root (e.g., `file:///etc/shadow` on Linux), a network UNC path (`\\\\server\\share\\evil`), or a path containing null bytes or traversal sequences. The downstream handler in `sffs_core.py` should validate that the resolved path is within the USB root and is a regular file before proceeding.

**Reasoning:** Drop events accept any URL the operating system forwards, and the MIME data is not sanitized by Qt itself.

**Reference:** `code3/f14_ui_dashboard.py` → `DragDropZone.dropEvent()` ~line 161

---

**Q211. In `f14_ui_dashboard.py`, the `DragDropZone.dropEvent()` method calls `urls[0].toLocalFile()` and emits only the first URL. What happens if a user drags multiple files onto the drop zone, and is this single-file constraint clearly communicated to the user?**

**Answer:** Only the first file in the drop is processed; all other files are silently ignored. The user receives no feedback indicating that only one file was accepted — the label updates to show the first file's name, which could be confused with confirmation that all files were queued. This creates confusion if the user intended to batch-encrypt multiple files.

**Reasoning:** A well-designed UI would either accept multiple files via a queue, or display a message like "Only one file at a time supported."

**Reference:** `code3/f14_ui_dashboard.py` → `DragDropZone.dropEvent()` ~line 162

---

**Q212. In `f14_ui_dashboard.py`, the `SFSSDashboard.__init__()` includes a `hint` label that says "AES file keys mix OS randomness with your mouse movement." This label is only shown `if core is not None`. What is the meaning of `core` being `None` in the dashboard context, and when does this condition occur?**

**Answer:** `core` is an `SFFSCore` instance that provides access to the crypto pipeline. When `core is None`, the dashboard is running in demo/standalone mode — launched directly with `python f14_ui_dashboard.py` or in a test harness without a full SFFS session. In this mode, encrypt/decrypt operations and cloud backup are unavailable, so the entropy hint (which only applies to real key generation) is hidden.

**Reasoning:** The `if __name__ == "__main__"` block at the bottom of the file calls `SFSSDashboard("demo-session-token", {}, paths)` without a `core`, confirming the demo-mode use case.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 248

---

**Q213. In `f14_ui_dashboard.py`, `self._lock_btn.clicked.connect(on_logout)` and `self._out_btn.clicked.connect(on_logout)` both connect to the same callback. What is the difference between "End session" and "Logout" from a security standpoint, and should these buttons trigger different behaviors?**

**Answer:** Semantically, "End session" should lock the screen and wipe in-memory keys but keep the user account active (resumable with re-authentication), while "Logout" should terminate the session, revoke the session token, and wipe all sensitive material. In the current implementation both call the same `on_logout` callback, so the distinction is purely cosmetic. A more secure design would have "End session" call a `lockSession()` that preserves the account but clears secrets, while "Logout" calls `terminateSession()` with full cleanup.

**Reasoning:** Conflating the two actions means there is no low-disruption "screen lock" option, reducing usability without improving security.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 309

---

**Q214. In `f14_ui_dashboard.py`, the `_on_cloud_backup()` method calls `self._core.backupKeys()` and checks `result.get("status")`. If `status == "not_authenticated"`, a `QMessageBox.question()` dialog is shown. Why is it important that this dialog blocks the UI thread, and what could go wrong if the authentication flow ran in the background thread?**

**Answer:** `QMessageBox.question()` runs a modal event loop on the main thread, preventing the user from triggering other operations while the question is displayed. If the authentication flow ran in a background thread, the user could simultaneously click "Encrypt" or "Logout", causing race conditions on shared state such as the session token and the Google credentials file being written concurrently with a logout that wipes them.

**Reasoning:** Qt enforces that all widget operations occur on the main thread; running a dialog from a background thread would trigger undefined behavior or a Qt warning/crash.

**Reference:** `code3/f14_ui_dashboard.py` → `_on_cloud_backup()` ~line 365

---

**Q215. In `f14_ui_dashboard.py`, the `_run_google_auth()` method defines an inner `_AuthWorker(QThread)` class and stores it as `self._auth_worker`. Why must the worker be stored as an instance attribute rather than a local variable, and what would happen if it were a local variable?**

**Answer:** If `_auth_worker` were a local variable, Python's garbage collector could deallocate the `QThread` object as soon as `_run_google_auth()` returns, while the OS thread is still running. Qt does not hold a Python-level reference to the thread, so the Python object would be destroyed while the underlying C++ `QThread` continues executing, causing a crash or signal delivery to a dangling object. Storing it as `self._auth_worker` keeps a reference for the lifetime of the window.

**Reasoning:** This is a well-known PyQt/PySide pitfall; the Qt documentation explicitly recommends keeping a reference to worker threads.

**Reference:** `code3/f14_ui_dashboard.py` → `_run_google_auth()` ~line 407

---

**Q216. In `f14_ui_dashboard.py`, the Google auth worker calls `self._auth_worker.terminate()` when the progress dialog is cancelled. What does `QThread.terminate()` do, and why is using `terminate()` considered unsafe for threads that hold locks or open file handles?**

**Answer:** `QThread.terminate()` forcibly kills the OS thread without any cleanup — no `finally` blocks run, no destructors are called, and no mutexes or file handles are released. If the auth flow had opened a socket or was writing `google_token.json`, the file could be left partially written or corrupt. Locks held by the terminated thread remain locked forever, potentially causing deadlocks in other threads.

**Reasoning:** The safe alternative is to set a cancellation flag and let the thread exit cooperatively, but the OAuth flow from `google_auth_oauthlib` does not expose a cancellation mechanism.

**Reference:** `code3/f14_ui_dashboard.py` → `_run_google_auth()` ~line 415

---

**Q217. In `f14_ui_dashboard.py`, `uiDashboard()` uses `QApplication.instance() or QApplication(sys.argv)` to reuse an existing QApplication if one exists. Why can only one `QApplication` instance exist per process, and what would happen if a second `QApplication` were created?**

**Answer:** `QApplication` initializes the Qt platform plugin, event loop infrastructure, and global state (style, clipboard, font database). Qt internally stores a single application pointer; creating a second instance corrupts that pointer. In practice, creating a second `QApplication` either raises a warning and returns `None`, crashes with a segfault, or causes unpredictable behavior in the first instance's event loop.

**Reasoning:** The guard `QApplication.instance() or QApplication(sys.argv)` ensures tests and demo scripts can call `uiDashboard()` even if a `QApplication` already exists in the process.

**Reference:** `code3/f14_ui_dashboard.py` → `uiDashboard()` ~line 447

---

**Q218. In `f14_ui_dashboard.py`, the `showSecurityAlert()` method changes the color of `self._sec` label to red (`#f28b82`) for CRITICAL alerts and yellow (`#fdd663`) for others. How are these color alerts communicated to screen reader software for visually impaired users?**

**Answer:** They are not communicated at all in the current implementation. Changing the stylesheet color of a `QLabel` conveys no semantic information to screen readers (AT-SPI on Linux, UIA/MSAA on Windows); these technologies read the label's text, not its color. To make the severity accessible, the label text itself should include the severity word (e.g., "CRITICAL: Tamper detected") and `QAccessibleInterface::state` should be updated, or a `QAccessibleEvent` should be emitted to notify assistive technology of the change.

**Reasoning:** WCAG 1.4.1 requires that color is not the only visual means of conveying information.

**Reference:** `code3/f14_ui_dashboard.py` → `showSecurityAlert()` ~line 354

---

**Q219. In `f14_ui_dashboard.py`, the `refreshLogs()` method displays only the last 5 log entries: `log_entries[-5:]`. What information could be lost if a burst of security events exceeds 5 entries in one refresh cycle?**

**Answer:** If multiple security events fire within a single refresh interval (e.g., a rapid sequence of failed logins followed by a debugger detection and a USB-removal alert), only the 5 most recent events are displayed, and earlier events in the burst are not shown in the UI. A user reviewing the dashboard would not see the full attack sequence. The underlying audit database retains all entries, but the operator must query it directly to see the complete picture.

**Reasoning:** The 5-entry cap is a UI simplification choice; for security monitoring, a scrollable log view or "view all" button would be safer.

**Reference:** `code3/f14_ui_dashboard.py` → `refreshLogs()` ~line 434

---

**Q220. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` uses a `QFileSystemModel` with `setReadOnly(True)`. Despite this setting, the context menu created in `_ctx_menu()` includes "Encrypt", "Decrypt", and "Delete" actions. What is the discrepancy between the model's read-only setting and these context menu actions?**

**Answer:** `QFileSystemModel.setReadOnly(True)` prevents the model from allowing in-place rename or delete operations initiated through the model's Qt editing interface (e.g., pressing F2 to rename). It does not affect custom context menu actions that invoke external code. The "Encrypt", "Decrypt", and "Delete" menu items are unconnected labels (no slot is wired), so they do nothing, but if connected, they would bypass the model's read-only flag entirely.

**Reasoning:** The docstring notes these are "labels only in this demo — wiring to crypto belongs in main-code," so the discrepancy is intentional and harmless in the current codebase.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 42, `_ctx_menu()` ~line 90

---

**Q221. In `f15_file_manager_explorer.py`, the docstring states "A host `QFileDialog` leaks paths to OS MRU databases and thumbnail caches." Explain concretely what an OS MRU (Most Recently Used) database is and how an adversary with physical access to the host computer could exploit it after a user browsed files with the host file dialog.**

**Answer:** The OS MRU database (e.g., `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs` on Windows, `~/.local/share/recently-used.xbel` on Linux) stores the names and paths of recently accessed files. An adversary with physical or forensic access to the host machine could read these registries or files to learn which sensitive documents the user was working with — even if the files themselves have been deleted from the USB drive. This reveals file names, directory structures, and access times without the attacker ever having had access to the USB stick.

**Reasoning:** The scoped `FileManagerExplorer` avoids this because all browsing uses the `QFileSystemModel` without invoking native OS dialogs.

**Reference:** `code3/f15_file_manager_explorer.py` → module docstring ~line 3

---

**Q222. In `f15_file_manager_explorer.py`, the `FileManagerExplorer._on_double_click()` emits `sffs_file_selected` for `.sffs` files and `plain_file_selected` for others. The `_status` label updates with the file size. Why is displaying the file size of an `.sffs` file potentially useful to an attacker who cannot read its contents?**

**Answer:** The encrypted `.sffs` file size reveals the approximate size of the original plaintext (ciphertext is nearly the same size as plaintext in AES-GCM). An attacker observing the file sizes can infer whether a file is a small text document (~1 KB) or a large database (~50 MB), helping them prioritize targets. Combined with the file's name stem (visible in the explorer), this can leak significant metadata about the original document.

**Reasoning:** The SFFS threat model includes protecting metadata; the date-modified column is already hidden for this reason, but file size in the status bar was not suppressed.

**Reference:** `code3/f15_file_manager_explorer.py` → `_on_double_click()` ~line 88

---

**Q223. In `f15_file_manager_explorer.py`, the `QFileSystemModel` is set with `setNameFilters()` only when `allowed_extensions` does not contain `"*"`. What happens to the file listing if `allowed_extensions = ["*"]` is passed explicitly versus passing `None`?**

**Answer:** When `allowed_extensions = None`, the `if` block is skipped entirely and no filters are set, so all files are shown. When `allowed_extensions = ["*"]` is passed, the condition `"*" not in allowed_extensions` is `False`, so the filter block is also skipped — the behavior is identical to `None`. Both result in all files being visible. The `"*"` wildcard acts as an explicit "show everything" opt-out of filtering, which is consistent and intentional.

**Reasoning:** The design allows callers to explicitly declare "no filtering" with `["*"]` for code clarity, rather than relying on `None` alone.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 43

---

**Q224. In `f15_file_manager_explorer.py`, hiding columns 1–3 (size, type, date modified) with `self._tree.hideColumn(col)` reduces information leakage in the tree view. Why is the date-modified column specifically sensitive in a security-focused file browser?**

**Answer:** The date-modified timestamp reveals when a file was last accessed or changed, which an adversary can correlate with known events (e.g., "a file was modified at 14:32 on the day of the breach"). For `.sffs` files, modification time also reveals when encryption occurred, helping an attacker map the timeline of the victim's activity. Combined with filesystem forensics, these timestamps can undermine deniability claims.

**Reasoning:** Hiding metadata columns is a defence-in-depth measure; the file data itself is encrypted, but timestamp leakage could still assist an attacker during an investigation.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 51

---

**Q225. In `f15_file_manager_explorer.py`, the `_ctx_menu()` method creates a `QMenu` with "Encrypt", "Decrypt", "Delete" labels but does not connect any of these actions to callbacks (`menu.addAction("Encrypt")` without a slot). What is the design intent here, and what risk does a partially implemented context menu create in a security application?**

**Answer:** The design intent is that `FileManagerExplorer` is a pure display widget; actual crypto operations are wired at integration level in `main-code`. The risk is that a developer might connect the "Delete" action without implementing the USB-root boundary check, or connect "Decrypt" without sandbox isolation, accidentally exposing raw plaintext outside the vault. Partially-implemented security UI creates a false sense of completeness that can lead to rushed, insecure wiring during integration.

**Reasoning:** The module docstring explicitly states "wiring to crypto belongs in main-code," which mitigates this risk if followed.

**Reference:** `code3/f15_file_manager_explorer.py` → `_ctx_menu()` ~line 90

---

**Q226. In `f16_cloud_sync.py`, the OAuth scope is `"https://www.googleapis.com/auth/drive.file"`. What does the `drive.file` scope restrict Google Drive access to, and why is it chosen over the broader `drive` scope?**

**Answer:** The `drive.file` scope limits SFFS to only reading and writing files that it created or explicitly opened — it cannot list, modify, or delete any other files in the user's Drive. The broader `drive` scope grants full read/write access to all files. Using `drive.file` follows the principle of least privilege: a compromised OAuth token or a bug in `cloudSync()` can only damage SFFS backup files, not the user's entire Drive library.

**Reasoning:** Narrowing the scope also reduces the risk of accidental data loss if SFFS has a bug in its delete logic.

**Reference:** `code3/f16_cloud_sync.py` → `SCOPES` ~line 30

---

**Q227. In `f16_cloud_sync.py`, the `_BUNDLED_SECRET` path points to `code3/google_client_secret.json`. The docstring explains that a "Desktop-app client_secret is intentionally semi-public (Google's own guidance for installed-application OAuth)." Why does Google consider the client secret of an installed/desktop application to be semi-public, and what is the actual security boundary in OAuth 2.0 for installed apps?**

**Answer:** Google's installed-app OAuth model acknowledges that the client secret can be extracted from the distributed binary by any motivated user. The actual security boundary is the user's Google account: the OAuth flow requires the user to interactively sign in and grant consent; an attacker with the client secret alone cannot impersonate any user without their credentials. The authorization code and access/refresh tokens are what must be kept secret, not the client ID/secret pair.

**Reasoning:** This is why the `drive.file` scope is critical: even if the client secret is extracted, the attacker can only access files created by SFFS, and only after full Google account authentication by the real user.

**Reference:** `code3/f16_cloud_sync.py` → `_BUNDLED_SECRET` ~line 36

---

**Q228. In `f16_cloud_sync.py`, the `_assert_keystore_encrypted()` function checks for required fields `{"kdf", "encrypted_private_key", "auth_tag", "iv", "salt"}` before allowing upload. Why is this pre-upload check critical — what specific secret would be exposed if a raw (unencrypted) private key file were uploaded to Google Drive?**

**Answer:** An unencrypted keystore would contain the RSA private key in plaintext. Anyone with access to the SFFS_Backup folder in Google Drive (e.g., via a stolen OAuth token or a Google account compromise) could read the private key and use it to decrypt the `bound_file_mac` and unwrap all AES file-encryption keys, gaining access to every file ever encrypted by that SFFS instance. The check prevents this catastrophic exposure by failing fast before any upload occurs.

**Reasoning:** The docstring states "a catastrophic secret exposure" — this is the correct characterisation since the private key is the root of trust for the entire system.

**Reference:** `code3/f16_cloud_sync.py` → `_assert_keystore_encrypted()` ~line 91

---

**Q229. In `f16_cloud_sync.py`, the `cloudSync()` function attempts to refresh an expired OAuth token with `creds.refresh(Request())` and re-saves the updated token to `google_token.json`. What happens if the refresh token itself has expired (e.g., the user hasn't used SFFS for 6 months), and how does the code handle this case?**

**Answer:** Google refresh tokens for installed apps expire after approximately 6 months of inactivity (or immediately if the user revokes access). When `creds.refresh(Request())` is called with an expired refresh token, it raises a `google.auth.exceptions.RefreshError`. The `except Exception as e` block catches this and returns `{"status": "offline", "message": str(e)}`. The user must then call `authenticateGoogleDrive()` again to perform a new interactive OAuth flow.

**Reasoning:** The code correctly treats a dead refresh token as an "offline/unauthenticated" state rather than crashing, preserving the structured-error-return design contract.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 161

---

**Q230. In `f16_cloud_sync.py`, the `authenticateGoogleDrive()` function calls `flow.run_local_server(port=0)`. What does `port=0` specify, and what security benefit does using a random ephemeral port have compared to a fixed port for the OAuth redirect server?**

**Answer:** `port=0` tells the OS to assign any available ephemeral port. The security benefit is that no other process can pre-bind to that specific port to intercept the OAuth authorization code (a "localhost redirect hijacking" attack). With a fixed port like `8080`, a malicious process running on the same machine could bind to port 8080 first and receive the authorization code before SFFS does.

**Reasoning:** Google's own installed-app OAuth guidelines recommend ephemeral ports for this reason.

**Reference:** `code3/f16_cloud_sync.py` → `authenticateGoogleDrive()` ~line 85

---

**Q231. In `f16_cloud_sync.py`, the `cloudSync()` function returns structured error dicts (e.g., `{"status": "offline", "message": "..."}`) instead of raising exceptions. What is the design rationale for this approach, and how does this affect the caller's ability to distinguish between network errors, authentication errors, and programming errors?**

**Answer:** The structured-dict design makes `cloudSync()` safe to call from a GUI callback without wrapping every call in try/except; the caller inspects the `status` key and shows the appropriate message or dialog. The drawback is that programming errors (e.g., passing a wrong type) that should raise exceptions are instead returned as `{"status": "error", ...}`, making them harder to distinguish from expected network failures. A better design would raise for programming errors and return dicts only for expected operational failures.

**Reasoning:** The module docstring explicitly states "never raises for network/auth" as the design contract.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 134

---

**Q232. In `f16_cloud_sync.py`, the `cloudSync("upload")` action prefixes the Drive filename with `sffs_`: `remote_name = f"sffs_{lp.name}"`. What naming conflict could arise if a user has two keystore files with different key IDs but the same base name (which should not happen given key_id uniqueness), and how does the SFFS_Backup folder isolation in Google Drive mitigate this?**

**Answer:** If two keystores had the same base name (e.g., `keystore.json`), uploading both would create two Drive files named `sffs_keystore.json` in `SFFS_Backup`. Google Drive allows duplicate names in the same folder (it uses file IDs, not names, as primary keys), so both files would coexist but a `list` operation would return both, making it ambiguous which to download. The `SFFS_Backup` folder isolation prevents collision with any user's other Drive files, but not with other SFFS keystores of the same name.

**Reasoning:** Because `f01_generate_key_pairs.py` encodes the `key_id` in the filename (e.g., `keystore_abc123.json`), this collision should never occur in practice.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 191

---

**Q233. In `f16_cloud_sync.py`, `MediaFileUpload(str(lp), resumable=True)` is used for uploads. Why is `resumable=True` specified for keystore uploads, and what is the typical file size of a keystore JSON that makes resumability relevant or irrelevant?**

**Answer:** `resumable=True` enables Google's resumable upload protocol, which allows an interrupted upload to be continued rather than restarted from scratch. A typical SFFS keystore JSON is only a few kilobytes (RSA-2048 public key + AES-encrypted private key + metadata), far below the 5 MB threshold where resumable uploads provide meaningful benefit. The setting is effectively a no-op for keystores but makes the code correct by default if larger files (e.g., encrypted `.sffs` files) are ever backed up in the future.

**Reasoning:** For sub-1 KB files, the overhead of the resumable protocol initiation request exceeds any recovery benefit.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 193

---

**Q234. In `f16_cloud_sync.py`, the `cloudSync("download")` action uses `MediaIoBaseDownload` and loops with `while not done: _, done = downloader.next_chunk()`. What memory management concern exists when downloading a very large file into a `BytesIO` buffer, and how does this relate to the 2 GB limit in `f03_decrypt_file.py`?**

**Answer:** `BytesIO` holds the entire downloaded file in RAM; downloading a 2 GB file would consume 2 GB of heap memory, and on a 32-bit process or a system with limited RAM this would cause an `MemoryError` or OS-level OOM kill. `f03_decrypt_file.py` enforces a `MAX_FILE_BYTES = 2 GB` guard for the same reason — AES-GCM requires the entire ciphertext in memory for authentication-tag verification. If SFFS ever backs up `.sffs` files, the download code should stream to disk rather than buffer in `BytesIO`.

**Reasoning:** Currently only keystore JSON files (a few KB) are downloaded, so this concern is theoretical but becomes real if the backup scope expands.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 213

---

**Q235. In `f16_cloud_sync.py`, the `_GOOGLE_OK = False` flag is set when Google libraries are not installed, and all entry points return structured dicts instead of raising `ImportError`. What principle of defensive programming does this implement, and how does it enable SFFS to function without network connectivity?**

**Answer:** This implements graceful degradation: if the optional Google SDK (`google-api-python-client`, `google-auth-oauthlib`) is not installed, the cloud sync module silently degrades to a no-op rather than crashing on import. SFFS's core functionality (encrypt, decrypt, authenticate) does not depend on cloud sync; the `{"status": "offline"}` return allows the UI to inform the user that backup is unavailable without blocking the primary workflow.

**Reasoning:** This also means SFFS can be used in air-gapped environments where Google SDK installation is prohibited.

**Reference:** `code3/f16_cloud_sync.py` → module-level try/except import ~line 18

---

**Q236. In `f17_config_loader.py`, the `DEFAULT_CONFIG` dictionary includes `"pbkdf2_iterations": 310000`. If this config value is changed by the user to a lower number (e.g., 100), and `sffs_core.py` uses this value for key derivation, what security impact would reducing iterations have, and does the current code actually use this config value for KDF?**

**Answer:** Reducing PBKDF2 iterations to 100 would make password-based key derivation trivially fast, enabling millions of brute-force attempts per second on commodity hardware. However, examining `f06_secure_key_storage.py`, the `KDF_ITERATIONS = 310_000` constant is hardcoded at module level and is not read from the config file; the config's `pbkdf2_iterations` value is stored but not consumed by the KDF code. The config value is therefore a placeholder for future use and does not currently affect security.

**Reasoning:** This discrepancy should be documented so a future developer does not wire the config value to the KDF without also enforcing a minimum iteration count in `validateConfig()`.

**Reference:** `code3/f17_config_loader.py` → `DEFAULT_CONFIG` ~line 41

---

**Q237. In `f17_config_loader.py`, the `configLoader()` function writes plaintext config to `sffs_config.json` when `encryption_key=None` and emits a `UserWarning`. In `sffs_core.py`'s `initialize()` method, the config is loaded with `configLoader("load", cfg_dir, encryption_key=None)`. What sensitive information in `DEFAULT_CONFIG` could be exposed by this unencrypted config file?**

**Answer:** The `DEFAULT_CONFIG` contains `"google_oauth_token_path"` (which, when populated, reveals where the OAuth token is stored), `"default_encrypt_dir"` and `"default_decrypt_dir"` (which reveal directory structure on the USB), `"cloud_sync_enabled"` (operational metadata), and `"key_size_bits"` (revealing the RSA key strength). An attacker finding the plaintext `sffs_config.json` on a lost USB drive learns the filesystem layout and cloud-sync status, assisting targeted attacks.

**Reasoning:** The `UserWarning` is intended to flag this in development; production should always pass an `encryption_key` derived from the user's login.

**Reference:** `code3/f17_config_loader.py` → `DEFAULT_CONFIG` ~line 27, `_write()` ~line 111

---

**Q238. In `f17_config_loader.py`, the `_write()` function deletes `sffs_config.json` when an `encryption_key` is provided and `enc_path` is written. Why is it important to delete the plaintext file after switching to encrypted storage, and what data recovery tool could recover the deleted plaintext config?**

**Answer:** If the plaintext file is not deleted, both the encrypted and unencrypted versions coexist; the `_read_current()` function reads the encrypted version (because `enc_path.exists()` is checked first), but anyone with filesystem access could read the plaintext version directly. After deletion, filesystem forensics tools such as `testdisk`, `photorec`, `Autopsy`, or `The Sleuth Kit` can recover the deleted file's content from unallocated clusters on FAT/exFAT USB drives, which do not zero blocks on deletion.

**Reasoning:** Secure deletion of the plaintext file (via `f08_secure_memory_wipe.secureWipeFile()`) would be stronger than a simple `unlink()`.

**Reference:** `code3/f17_config_loader.py` → `_write()` ~line 122

---

**Q239. In `f17_config_loader.py`, the `configLoader("get")` action calls `configLoader("load", ...)` recursively and looks up a single key. What is the performance implication of this design — how many disk reads occur for a single `get` operation when the config file is encrypted?**

**Answer:** One `get` call triggers one `load` call, which calls `_read_current()`, which reads the encrypted file from disk, decrypts it with AES-GCM, and parses the JSON — all to return a single value. This is one disk read and one AES-GCM decryption per `get` call. If `get` is called frequently (e.g., in a hot UI render loop), this adds up; a better design would cache the decrypted config in memory and invalidate the cache only when `save` is called.

**Reasoning:** For a USB drive with typical 5–20 MB/s read speed, a config file of a few KB adds negligible latency per call, but the design should still be noted.

**Reference:** `code3/f17_config_loader.py` → `configLoader()` ~line 142

---

**Q240. In `f17_config_loader.py`, the `validateConfig()` function checks `auto_lock_timeout_seconds >= 30`. Why is a minimum of 30 seconds enforced, and what security risk arises if a user could set this to 0 (immediate lock on any idle)?**

**Answer:** A 30-second minimum prevents the application from locking mid-operation (e.g., while AES encryption of a large file is in progress), which could leave the sandbox in an inconsistent state. Setting the timeout to 0 would cause the idle timer to fire almost immediately after any user pause, making the application unusable. It could also be exploited to trigger an emergency lock denial-of-service: an attacker with access to the input event stream could suppress mouse/keyboard events to force repeated locks.

**Reasoning:** The minimum is a usability floor, not a security ceiling; the real concern is preventing operational disruption.

**Reference:** `code3/f17_config_loader.py` → `validateConfig()` ~line 164

---

**Q241. In `f17_config_loader.py`, the `_encrypt_blob()` and `_decrypt_blob()` helper functions use AES-GCM with a fresh 12-byte IV each time. If the same `encryption_key` is used for both the config file and some other data store, what key reuse risk arises, and how should key separation be enforced?**

**Answer:** AES-GCM with a random 12-byte IV has a birthday-paradox collision probability of approximately 1/(2^48) per pair of messages for IV collision. Reusing the same key across the config file and an audit log or keystore means IV collisions between files (not just within one file) become possible, and a collision would allow an attacker to XOR two ciphertexts and eliminate the keystream, leaking information about both plaintexts. Key separation should be enforced by deriving distinct subkeys via HKDF with different `info` labels for each data store.

**Reasoning:** This is the standard "domain separation" principle for AES-GCM keys.

**Reference:** `code3/f17_config_loader.py` → `_encrypt_blob()` ~line 52

---

**Q242. In `f17_config_loader.py`, `configLoader("save", ...)` merges new `updates` into the current config via `merged.update(updates)`. What happens if `updates` contains a key that is NOT in `DEFAULT_CONFIG` — is this key preserved or discarded, and is that behavior secure?**

**Answer:** Unknown keys in `updates` are preserved — `merged.update(updates)` sets any key regardless of whether it appears in `DEFAULT_CONFIG`. This means an attacker or buggy code that injects arbitrary keys into `updates` can pollute the config dict with arbitrary data that is then AES-encrypted and stored, and later returned to all `load` callers. If downstream code uses `config.get("some_key")` with a fallback, an injected key could silently override a security-relevant default.

**Reasoning:** A secure design would whitelist allowed keys before applying `updates` — only keys present in `DEFAULT_CONFIG` should be accepted.

**Reference:** `code3/f17_config_loader.py` → `configLoader()` ~line 137

---

**Q243. In `f17_config_loader.py`, the `_merge_defaults()` function does `out = dict(DEFAULT_CONFIG); out.update(cfg)`. This means user config values override defaults. What security risk exists if a malicious config file sets `"max_login_attempts": 99999` or `"auto_lock_timeout_seconds": 999999`?**

**Answer:** A tampered config file could disable the brute-force lockout by setting `max_login_attempts` to a huge number, giving an attacker unlimited password attempts. Setting `auto_lock_timeout_seconds` to 999999 (~11 days) would prevent the idle lock from ever firing in practice. Both attacks require writing a malicious `sffs_config.enc` (or `sffs_config.json`), which requires access to the USB drive. The `validateConfig()` function enforces `auto_lock_timeout_seconds >= 30` but does not enforce an upper bound, and does not validate `max_login_attempts` at all.

**Reasoning:** `validateConfig()` should add upper-bound checks and be called on load, not just on explicit validation requests.

**Reference:** `code3/f17_config_loader.py` → `_merge_defaults()` ~line 46, `validateConfig()` ~line 152

---

**Q244. In `f18_thread_controller.py`, the `WorkerThread` class inherits from `QThread` and runs `task(*args, **kwargs)` in its `run()` method. Why does Qt require that UI widgets only be updated from the main thread, and how do `pyqtSignal`s safely marshal results back to the main thread?**

**Answer:** Qt's widget rendering pipeline is not thread-safe: internal state like paint events, geometry, and focus management are maintained without locks. Accessing widgets from a background thread causes data races that manifest as crashes, visual glitches, or corrupted state. `pyqtSignal` uses Qt's queued connection mechanism: when a signal is emitted from a non-GUI thread, the slot invocation is posted as an event into the receiver's thread's event queue, where the main event loop dequeues and executes it safely on the GUI thread.

**Reasoning:** This is why `WorkerThread.run()` emits signals (safe) rather than updating `self.progress_bar.setValue()` directly (unsafe).

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.run()` ~line 49

---

**Q245. In `f18_thread_controller.py`, the `WorkerThread` has a `cancel()` method that sets `self._cancelled = True` and an `is_cancelled()` method. However, the `run()` method does not check `_cancelled` at any point. What must the `task` function itself do to support cancellation, and why can't `WorkerThread` cancel the task from outside?**

**Answer:** The `task` function must periodically call `worker.is_cancelled()` (receiving the worker handle via closure or argument) and return early when `True`. Python does not expose a safe way to stop an arbitrary thread from outside: `thread.join(timeout)` only waits, `terminate()` is destructive, and there is no equivalent to `pthread_cancel` in Python's threading model. The cooperative cancellation pattern (polling a flag) is the only safe approach because the task controls its own stack and resources.

**Reasoning:** This is the standard cooperative cancellation pattern in Qt worker thread design.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.cancel()` ~line 43, `run()` ~line 49

---

**Q246. In `f18_thread_controller.py`, exceptions in `task` are caught and emitted via `self.signals.error.emit(f"{e}\n{traceback.format_exc()}")`. What security concern exists with emitting full tracebacks, and in what contexts might this reveal sensitive path or variable information?**

**Answer:** Full tracebacks include absolute file paths (revealing USB drive letter/mount point and directory structure), local variable names and values at each frame (which could include partial key bytes, plaintext snippets, or passwords if they appear in local scope), and the exception message itself (which might contain `ValueError: decryption failed for /media/USB/sffs_data/keys/keystore_abc123.json`). In production, tracebacks should be logged to the encrypted audit database and a generic error message shown in the UI.

**Reasoning:** The `error` signal connects to a UI callback that could display the traceback in a dialog visible on screen.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.run()` ~line 54

---

**Q247. In `f18_thread_controller.py`, the `WorkerSignals` class is a separate `QObject` rather than embedding signals directly in `WorkerThread`. Why does PyQt6 require signals to be defined in a `QObject` subclass, and what would happen if `pyqtSignal` were defined directly in a non-QObject class?**

**Answer:** `pyqtSignal` is a descriptor that is only activated during `QMetaObject` compilation, which happens when the class's metaclass (`pyqtWrapperType`) processes the class body. If `pyqtSignal` is defined in a plain Python class (not inheriting `QObject`), the descriptor is never bound to a meta-object slot and raises `AttributeError` at runtime when accessed. The reason `WorkerSignals` is separate from `WorkerThread` is a PyQt5/6 limitation: `QThread` subclasses in some versions do not reliably support signals defined directly on them.

**Reasoning:** Separating signals into a `QObject` container is a recommended PyQt pattern that avoids this metaclass limitation.

**Reference:** `code3/f18_thread_controller.py` → `WorkerSignals` ~line 22

---

**Q248. In `f18_thread_controller.py`, `threadController()` connects callbacks using Qt's signal/slot mechanism. If `done_callback` raises an unhandled exception, what happens to the main event loop, and is this exception caught anywhere?**

**Answer:** An unhandled exception in a slot called from the Qt event loop propagates up through Qt's C++ dispatch code. In PyQt6, this causes Qt to call `sys.excepthook` and then silently swallow the exception, allowing the event loop to continue. The exception is not caught by `WorkerThread.run()`'s `try/except` because the slot executes on the GUI thread, not the worker thread. This means a buggy `done_callback` can silently fail without any error being reported to the user.

**Reasoning:** Callers should wrap their callbacks in try/except or use `sys.excepthook` to log slot exceptions.

**Reference:** `code3/f18_thread_controller.py` → `threadController()` ~line 84

---

**Q249. In `f18_thread_controller.py`, the `run_in_thread` decorator returns a `WorkerThread` instance from the wrapped function. The caller receives the worker handle. What is the caller's responsibility for memory management of the returned `WorkerThread` object, and what happens if no reference is kept?**

**Answer:** The caller must store the returned `WorkerThread` in a variable (typically an instance attribute) for the duration of the task's execution. If the caller discards the return value (`run_in_thread_decorated_func()`), the `WorkerThread` Python object has no references and becomes eligible for garbage collection. CPython's reference counting will deallocate the Python wrapper, which may call the C++ `QThread` destructor while the thread is still running, causing a crash or segfault.

**Reasoning:** This is the same issue as storing `_auth_worker` as an instance attribute in `SFSSDashboard._run_google_auth()`.

**Reference:** `code3/f18_thread_controller.py` → `run_in_thread` ~line 96

---

**Q250. In `f18_thread_controller.py`, the `threadController()` function starts the thread immediately with `worker.start()` before returning. What race condition exists between `worker.start()` returning and the caller connecting additional signals that were not passed to `threadController()`?**

**Answer:** If the task completes very quickly (e.g., a cached lookup), `signals.result` and `signals.finished` may be emitted before the caller has connected additional slots to them after `threadController()` returns. Those emissions would be missed because no slot was connected at the time of emission. The design assumes all relevant callbacks are passed to `threadController()` before starting; any additional connections made after the call are inherently racy.

**Reasoning:** A safer pattern would start the thread only after all connections are made, or use `Qt.ConnectionType.QueuedConnection` with an idle post.

**Reference:** `code3/f18_thread_controller.py` → `threadController()` ~line 92

---

**Q251. In `f13_init_drive_detection.py`, the path map dict returned by `initDriveDetection()` is shared across all of `sffs_core.py`'s session. If the USB is physically removed mid-session and `monitorUSBPresence()` triggers, why is `emergencyLock()` the correct response rather than simply updating the path map to point to a local fallback?**

**Answer:** The USB drive contains the encrypted keystores, the sandbox with decrypted files, and the audit log — switching to a local fallback would mean sensitive decrypted files in the sandbox are now on the host hard drive without the encrypted protection of the USB. Furthermore, any ongoing crypto operations would reference paths that no longer exist, causing errors. The emergency lock wipes memory and terminates the session precisely to ensure that no sensitive data remains on the host when the USB disappears.

**Reasoning:** The threat model treats USB removal as a physical security event, not a network hiccup to route around.

**Reference:** `code3/f13_init_drive_detection.py` → `monitorUSBPresence()` ~line 158

---

**Q252. In `f16_cloud_sync.py`, `loadCredentials()` reads the OAuth token from `config_dir / "google_token.json"`. This token file is stored on the USB drive alongside the encrypted keystores. What is the risk of token leakage if the USB drive is lost, and does the `drive.file` scope limit the damage?**

**Answer:** If the USB is lost, an attacker who reads `google_token.json` (a plaintext file) has an access token and refresh token that can authenticate to Google Drive as the user. The `drive.file` scope limits the attacker to reading/deleting only files created by this SFFS instance (the encrypted keystores in `SFFS_Backup`). The attacker cannot read other Drive files, but they can download the encrypted keystores. Since the keystores are AES-GCM encrypted with Argon2id, the attacker would still need the user's master password to extract the RSA private key.

**Reasoning:** Encrypting `google_token.json` with the user's session key would add a layer of protection on USB loss.

**Reference:** `code3/f16_cloud_sync.py` → `loadCredentials()` ~line 39

---

**Q253. In `f14_ui_dashboard.py`, the `SFSSDashboard` widget includes `_sandbox_list = QListWidget()` that shows decrypted file paths from `self._core.list_sandbox_files()`. What operational security risk is created by displaying decrypted file names in a visible GUI list?**

**Answer:** The sandbox list shows the names of currently decrypted files (e.g., `quarterly_report_Q3.pdf`, `private_key.pem`), which reveals which sensitive documents are actively in use. Anyone looking at the screen (shoulder surfing) or capturing a screenshot can learn what files are being worked on without having any access to the encrypted vault. The file names alone can be valuable intelligence in a targeted attack.

**Reasoning:** Displaying only generic placeholders or hashed identifiers in the sandbox list would reduce this metadata leakage.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 259, `refresh_sandbox_list()` ~line 313

---

**Q254. In `f15_file_manager_explorer.py`, `QFileSystemModel.setReadOnly(True)` is set, but the file manager still allows double-clicking to emit signals. Why does `setReadOnly` not prevent file-system operations initiated through signal handlers connected to `sffs_file_selected` and `plain_file_selected`?**

**Answer:** `setReadOnly(True)` only prevents the model from accepting edit operations through Qt's standard view-model editing interface (rename, delete via the model's `removeRow()`). It has no effect on application code that reads the emitted file path from a signal and directly invokes OS-level file operations. The signal handlers in `sffs_core.py` can call `encryptFile()`, `decryptFile()`, or `os.unlink()` freely, because those calls bypass the Qt model layer entirely.

**Reasoning:** `setReadOnly` is a UI-layer guard, not a filesystem-level guard; it protects the view from accidental edits, not from intentional application-level operations.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 42

---

**Q255. In `f16_cloud_sync.py`, when uploading, the file is read by Google's `MediaFileUpload` directly from disk. If the keystore file is being written by `secureKeyStorage()` concurrently on another thread, what race condition exists, and how should file locking be added?**

**Answer:** `MediaFileUpload` opens and reads the file while `secureKeyStorage()` may still be writing it (write + flush + fsync sequence). The upload could read a partially written keystore — missing the `auth_tag` or `encrypted_private_key` fields — and upload a corrupt file to Drive. The `_assert_keystore_encrypted()` check would catch the missing fields and abort the upload, but not until after the file is opened. A proper fix would use a file lock (e.g., `fcntl.flock` on Linux, `msvcrt.locking` on Windows) or an application-level mutex around keystore write operations.

**Reasoning:** The `cloudSync()` call should wait for any in-progress keystore write to complete before reading the file.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 193

---

**Q256. In `f17_config_loader.py`, the `configLoader("reset")` action writes `DEFAULT_CONFIG` and ignores any existing config. What operational security incident could result if a user accidentally calls `reset` — what configuration values would be lost and what security settings would revert to defaults?**

**Answer:** A `reset` would overwrite all user customizations: `auto_lock_timeout_seconds` would revert to 300 seconds (which may be longer than the user configured), `max_login_attempts` would revert to 5, `cloud_sync_enabled` would become `False` (disabling backups silently), and any `google_oauth_token_path` pointer would be cleared. The most dangerous consequence is that the user's custom `default_encrypt_dir` and `default_decrypt_dir` would be lost, potentially causing the next encryption to write to an unexpected location.

**Reasoning:** `reset` should require explicit confirmation and should create a backup of the current config before overwriting.

**Reference:** `code3/f17_config_loader.py` → `configLoader()` ~line 125

---

**Q257. In `f14_ui_dashboard.py`, the `_open_sandbox_item()` method calls `show_sandbox_file_viewer(self, Path(item.text()))`. The `item.text()` is the string path stored in the `QListWidgetItem`. What trust assumption is made about the content of list items, and could a malicious process inject a path into the sandbox list?**

**Answer:** The code implicitly trusts that all items in `_sandbox_list` contain valid paths within the sandbox directory. If a malicious process could write to the shared memory or IPC channel used by `list_sandbox_files()`, it could inject an arbitrary path (e.g., `/etc/shadow`), which `show_sandbox_file_viewer` would then attempt to open. In practice, `list_sandbox_files()` reads from the `sffs_data/sandbox` directory whose permissions are controlled by `createIsolatedSandbox()`, making injection difficult but not impossible if the sandbox directory itself is compromised.

**Reasoning:** The path should be validated to be within the expected sandbox directory before being passed to the viewer.

**Reference:** `code3/f14_ui_dashboard.py` → `_open_sandbox_item()` ~line 320

---

**Q258. In `f18_thread_controller.py`, the `WorkerThread.run()` emits `signals.result.emit(out)` if no exception occurs, and `signals.finished.emit()` in the `finally` block. What is the guaranteed order of these two signal emissions, and can connected slots rely on `result` always arriving before `finished`?**

**Answer:** Within a single thread, `result` is always emitted before `finished` because `result` is emitted in the `try` block and `finished` is emitted in the `finally` block, which runs after the `try` completes. However, because these are queued signals delivered to the GUI thread's event queue, the slots are executed in the order the events are enqueued — `result`'s event is posted first, `finished`'s event second — so GUI-thread slots can rely on `result` arriving before `finished`. If an exception occurs, only `finished` is emitted (no `result`), so `finished_callback` must not assume the task succeeded.

**Reasoning:** This ordering guarantee is critical for cleanup callbacks that need the result before they run.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.run()` ~line 49

---

**Q259. In `f16_cloud_sync.py`, the `cloudSync("delete")` action calls `service.files().delete(fileId=file_id).execute()` with no confirmation step. What happens to the deleted file in Google Drive (is it permanently deleted or moved to trash), and what is the implication for key recovery after accidental deletion?**

**Answer:** The Google Drive API `files.delete` permanently deletes the file — it does not move it to the user's trash (unlike user-initiated deletion in the Drive UI). Once the delete call executes, the keystore backup is immediately unrecoverable through Drive. If the USB drive is also lost or damaged, the user permanently loses access to all files encrypted with that RSA key pair with no recovery path. SFFS should use `files.update(body={"trashed": True})` instead to give a recovery window.

**Reasoning:** Permanent deletion without confirmation is appropriate only for ephemeral files; keystore backups warrant a soft-delete or confirmation dialog.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 246

---

**Q260. In `f13_init_drive_detection.py`, all six standard directories are created with `mkdir(parents=True, exist_ok=True)` but without setting restrictive permissions (no `chmod`). Contrast this with `createIsolatedSandbox()` in `f07_create_isolated_sandbox.py` which explicitly calls `os.chmod(sandbox_path, 0o700)`. Why does `initDriveDetection()` not set restrictive permissions, and is this a security gap?**

**Answer:** The standard SFFS directories (`keys_dir`, `logs_dir`, etc.) inherit the USB drive's default permissions, which on FAT/exFAT filesystems do not support Unix permission bits at all. `createIsolatedSandbox()` uses `chmod(0o700)` because sandbox directories are created on the host filesystem (tmpfs or ext4) where permissions are meaningful. Attempting `chmod` on FAT directories would either raise `OSError` or have no effect. This is not a security gap for USB-portable deployments because FAT has no discretionary access control; the physical security of the USB stick is the primary protection.

**Reasoning:** On Linux with ext4 USB drives, adding `chmod` to `initDriveDetection()` would be a valid hardening measure.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 146

---

**Q261. In `f14_ui_dashboard.py`, the `SFSSDashboard` receives `session_token`, `config`, and `paths` in its constructor. The `session_token` is stored as `self._session`. What risk exists if this session token is inadvertently serialized (e.g., via Python's `pickle` or logged to disk) and how should it be handled at logout?**

**Answer:** If `self._session` is pickled (e.g., by Qt's session restore mechanism or a crash reporter) or logged, the raw session token ends up in a file that can outlive the session. An attacker who reads that file gets a valid session token that can authenticate without the user's password. At logout, `self._session` should be explicitly overwritten with `None` (or a zeroed bytearray if it were stored as bytes) and `terminateSession()` should be called to invalidate the token server-side before the dashboard is destroyed.

**Reasoning:** Session tokens are bearer credentials; their lifetime on disk must be bounded to the session duration.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 185

---

**Q262. In `f15_file_manager_explorer.py`, `QFileSystemModel` is initialized with the USB root path as the root. The model's `setRootPath()` call initiates a file-system watcher. On Linux, `QFileSystemModel` uses `inotify` to watch for changes. What resource limit (inotify watches) could be exhausted on a USB drive with thousands of files, and what would happen to the file explorer?**

**Answer:** Linux has a per-user limit on the number of inotify watches (`/proc/sys/fs/inotify/max_user_watches`, default 8192). `QFileSystemModel` creates one watch per directory it has expanded. On a USB drive with thousands of subdirectories, this limit can be exhausted, causing new `inotify_add_watch()` calls to fail. Qt silently stops receiving filesystem change notifications for directories that could not be watched; the file explorer will display stale content and will not update when files are added or removed.

**Reasoning:** Restricting `QFileSystemModel` to the relevant subdirectories (e.g., only `sffs_data`) rather than the entire USB root would reduce watch consumption.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 40

---

**Q263. In `f16_cloud_sync.py`, the `BACKUP_FOLDER_NAME = "SFFS_Backup"` is a fixed, predictable folder name in the user's Google Drive. What information disclosure risk arises from using a fixed, predictable folder name, and how could it be made less guessable?**

**Answer:** Anyone with read access to the user's Google Drive (e.g., via a shared folder or a compromised Google account) can search for "SFFS_Backup" and immediately identify SFFS backup files, learning that the user employs this specific security application. The folder name discloses both the application type and the presence of encrypted key material. A less guessable name could be derived by hashing the user's Google account ID with a fixed salt (e.g., `SFFS_` + first 8 chars of `SHA256(google_email)`).

**Reasoning:** The `drive.file` scope already limits who can see this folder, but the predictable name is an unnecessary information leak.

**Reference:** `code3/f16_cloud_sync.py` → `BACKUP_FOLDER_NAME` ~line 31

---

**Q264. In `f17_config_loader.py`, the `configLoader()` function's inner `_read_current()` tries the encrypted path first and falls back to the plaintext path. What happens if both `sffs_config.enc` and `sffs_config.json` exist simultaneously — which one is used, and could this lead to inconsistent state?**

**Answer:** When `encryption_key` is provided and `enc_path.exists()`, the encrypted version is read; the plaintext version is ignored entirely. This could be inconsistent if the plaintext version contains newer settings (e.g., the user edited `sffs_config.json` manually while the encryption key was unavailable). In the opposite case (no `encryption_key`), `_read_current()` reads the plaintext file even if the encrypted version also exists, potentially serving stale data. The `_write()` function deletes the plaintext file when writing encrypted, so the dual-file state should not occur in normal operation.

**Reasoning:** The comment in `_write()` shows awareness of this: `if plain_path.exists(): plain_path.unlink()` is called after writing the encrypted version.

**Reference:** `code3/f17_config_loader.py` → `_read_current()` ~line 98

---

**Q265. In `f18_thread_controller.py`, the `run_in_thread` decorator can be used without parentheses (`@run_in_thread`) or with keyword arguments (`@run_in_thread(kwargs={"key": "value"})`). Trace through the decorator logic to explain how `fn is not None` handles both usage patterns.**

**Answer:** When `@run_in_thread` is used without parentheses, Python calls `run_in_thread(fn)` where `fn` is the decorated function — a non-None callable. The `if fn is not None: return decorator(fn)` branch executes immediately, wrapping `fn` and returning the wrapper. When `@run_in_thread(kwargs={...})` is used, Python first calls `run_in_thread(fn=None, kwargs={...})` — `fn` is `None` — so the function returns `decorator` (a callable), which Python then calls with the decorated function as its argument, producing the wrapper. The `fn is not None` check distinguishes the two call signatures.

**Reasoning:** This dual-mode decorator pattern (a.k.a. "optional-argument decorator") is a common Python idiom.

**Reference:** `code3/f18_thread_controller.py` → `run_in_thread` ~line 96, `if fn is not None` ~line 112

---

**Q266. In `f14_ui_dashboard.py`, the `updateProgress()` method makes `self._bar` visible and sets its value. What PyQt6 threading rule does this violate if `updateProgress()` is called directly from a `WorkerThread`, and what is the correct way to update the progress bar from a background thread?**

**Answer:** Calling `self._bar.setVisible(True)` and `self._bar.setValue(percent)` from a `WorkerThread` directly manipulates Qt widgets from a non-GUI thread, violating Qt's thread-affinity rule. This can cause crashes, paint artifacts, or silent corruption of the widget's internal state. The correct approach is for `WorkerThread` to emit `signals.progress.emit(percent)`, and for `updateProgress()` to be connected to that signal via `worker.signals.progress.connect(dashboard.updateProgress)` — Qt's queued connection ensures the slot executes on the GUI thread.

**Reasoning:** The `f18_thread_controller.py` design with `WorkerSignals.progress = pyqtSignal(int)` exists precisely for this purpose.

**Reference:** `code3/f14_ui_dashboard.py` → `updateProgress()` ~line 350, `code3/f18_thread_controller.py` → `WorkerSignals` ~line 25

---

**Q267. In `f13_init_drive_detection.py`, `_windows_volume_root()` uses `path.anchor` (e.g., `"D:\\"`), while `_linux_mount_root()` uses `psutil.disk_partitions()`. Why are different approaches needed for the two platforms, and what would `path.anchor` return on Linux for a path like `/media/user/USB`?**

**Answer:** On Windows, the volume root is always the drive letter anchor (`D:\\`), a concept baked into the path structure. On Linux, multiple filesystems can be mounted anywhere in a single directory hierarchy without any path-structure signal — `/media/user/USB` has anchor `/` (same as `/home`), so `path.anchor` would return `/` for both, making it useless for identifying the USB mount point. Linux requires querying the mount table to find the deepest mount point that is a prefix of the path.

**Reasoning:** `path.anchor` on Linux for `/media/user/USB/sffs_data` returns `"/"`, not `"/media/user/USB"`.

**Reference:** `code3/f13_init_drive_detection.py` → `_windows_volume_root()` ~line 36, `_linux_mount_root()` ~line 42

---

**Q268. In `f16_cloud_sync.py`, the `loadCredentials()` function returns `None` if the token file cannot be parsed (catches all `Exception`). What specific exceptions should be caught here rather than `Exception`, and what is the risk of catching too broadly?**

**Answer:** The expected exceptions are `json.JSONDecodeError` (malformed token file), `KeyError`/`ValueError` (missing fields in the JSON), `OSError` (file read failure), and `google.auth.exceptions.GoogleAuthError` (invalid credential fields). Catching all `Exception` risks silently swallowing unexpected errors like `MemoryError`, `RecursionError`, or bugs in the `Credentials.from_authorized_user_info()` implementation — these would all return `None` (unauthenticated) rather than surfacing as bugs, potentially causing confusing "not authenticated" errors that mask real issues.

**Reasoning:** Broad `except Exception` is a pattern the docstring acknowledges but should be narrowed in production.

**Reference:** `code3/f16_cloud_sync.py` → `loadCredentials()` ~line 51

---

**Q269. In `f17_config_loader.py`, the `DEFAULT_CONFIG` includes `"google_oauth_token_path": None`. In production, this field would point to the OAuth token file. If this path is stored in the unencrypted `sffs_config.json` on the USB drive, what information could an attacker infer from it?**

**Answer:** The path reveals the directory structure of the USB drive (e.g., `/media/USB/sffs_data/config/google_token.json`), which confirms SFFS is installed and where sensitive files are stored. Combined with a directory listing, the attacker can find and extract the token file directly. Even if the token is expired, the path confirms the user has a Google Drive connection, which is itself sensitive operational metadata.

**Reasoning:** The config should be encrypted in production precisely because of this metadata leakage risk.

**Reference:** `code3/f17_config_loader.py` → `DEFAULT_CONFIG` ~line 35

---

**Q270. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` uses a `QSplitter` with a tree view on the left and a "list" view (actually another `QTreeView`) on the right. Why is a second `QTreeView` used as a list view instead of `QListView`, and what display inconsistency does this create?**

**Answer:** `QTreeView` is used for the right pane because `QFileSystemModel` is a tree model and does not directly support `QListView`'s flat-list display mode; using `QTreeView` with `setRootIsDecorated(False)` and `setItemsExpandable(False)` approximates a flat list while still working with the same model. The display inconsistency is that the right pane shows column headers (name, size, type, date — even though 1–3 are hidden), expand arrows may flicker, and the tree hierarchy is visible when the root is changed, which looks like a list with unnecessary indentation.

**Reasoning:** A `QListView` would require a proxy model or a separate `QDirModel` instance, adding complexity; the current approach is a pragmatic shortcut.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 54

---

**Q271. In `f14_ui_dashboard.py`, the `SFSSDashboard._pick_sffs_to_view()` calls `QFileDialog.getOpenFileName(self, "Choose .sffs", "", "SFFS (*.sffs)")`. This uses the host OS file dialog. The `f15_file_manager_explorer.py` docstring specifically warns against using host `QFileDialog` because it "leaks paths to OS MRU databases." Why does `SFSSDashboard` still use a host file dialog for this specific operation?**

**Answer:** The `.sffs` file to view may be stored anywhere on the host system (e.g., received via email and downloaded to `~/Downloads`) rather than only on the USB drive. Restricting the dialog to the scoped `FileManagerExplorer` would prevent the user from opening an `.sffs` file that was transferred to the host machine outside the USB vault. The design accepts the MRU leakage trade-off in exchange for the usability of finding `.sffs` files anywhere on the system. This is a deliberate exception, not an oversight.

**Reasoning:** The `.sffs` file extension filter at least limits what appears in the OS MRU to `.sffs` file paths, not plaintext document paths.

**Reference:** `code3/f14_ui_dashboard.py` → `_pick_sffs_to_view()` ~line 329

---

**Q272. In `f18_thread_controller.py`, the `WorkerThread` stores `self.signals = WorkerSignals()`. If two different callers use the same `WorkerThread` instance and both connect to `signals.result`, what happens when the task completes — do both slots receive the signal?**

**Answer:** Yes, both slots receive the signal. Qt signals support multiple connections; when `signals.result.emit(out)` is called, Qt delivers the emission to all connected slots in the order they were connected. Both callers' slots are invoked on the GUI thread (via queued connection) with the same `out` value. This means two callers can both react to the same task result, which is the expected publish-subscribe behavior. However, if both callers trigger independent actions (e.g., both try to write a result to disk), they must coordinate to avoid conflicts.

**Reasoning:** This multi-slot broadcast is a feature, not a bug — it is the foundation of Qt's MVC pattern.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread` ~line 40

---

**Q273. In `f16_cloud_sync.py`, `service = build("drive", "v3", credentials=creds, static_discovery=False)` is called inside `cloudSync()` on every invocation. What is the performance cost of rebuilding the Google Drive service client on every call, and how could it be optimized?**

**Answer:** `build()` fetches the API discovery document from Google's servers (or from a local cache if `static_discovery=False` falls back to a bundled version), parses it, and constructs a `Resource` object. This involves JSON parsing and class generation, taking approximately 50–200 ms per call. The optimization is to cache the `service` object at module level or in `SFFSCore`, rebuilding it only when credentials change. Since credentials can be refreshed, the cache must be invalidated on refresh.

**Reasoning:** For infrequent cloud operations this overhead is acceptable, but batching multiple operations per `cloudSync()` call rather than calling it repeatedly would also help.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 173

---

**Q274. In `f17_config_loader.py`, `validateConfig()` checks `config.get("theme") not in ("dark", "light")`. What security concern motivates validating the theme value — could an adversary exploit an unchecked theme string to perform injection in a stylesheet?**

**Answer:** Yes — Qt stylesheets are applied as CSS-like strings. If `theme` were used unsanitized in a `setStyleSheet()` call (e.g., `f"theme: {config['theme']}"`), a malicious config containing CSS injection payloads could alter the application's visual presentation, hide security alerts, or change button colors to confuse the user into performing unintended actions. Whitelisting `"dark"` and `"light"` ensures only known-safe values reach the stylesheet engine.

**Reasoning:** CSS injection in desktop apps is a lower-risk attack than web XSS, but it can still defeat security UI elements (e.g., hiding the "CRITICAL" alert color).

**Reference:** `code3/f17_config_loader.py` → `validateConfig()` ~line 162

---

**Q275. In `f14_ui_dashboard.py`, the `SFSSDashboard` layout uses `QSplitter(Qt.Orientation.Horizontal)` with `splitter.setSizes([520, 380])`. What happens to these sizes when the window is resized by the user, and does Qt persist the splitter position between sessions?**

**Answer:** When the window is resized, Qt proportionally rescales the splitter panes to maintain their relative ratios from the set sizes. Qt does not automatically persist the splitter position between sessions; the sizes reset to `[520, 380]` on every application start. To persist the splitter state, `splitter.saveState()` should be called at shutdown and its result stored in the config, then `splitter.restoreState()` called at startup. Without persistence, user layout adjustments are lost on every restart.

**Reasoning:** This is a usability issue rather than a security concern, but it affects user experience.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 305

---

**Q276. In `f13_init_drive_detection.py`, `initDriveDetection()` emits a `UserWarning` using `warnings.warn()` when running from a non-removable drive. In a production GUI application, where would this warning be visible, and how should it be surfaced to the user instead?**

**Answer:** `warnings.warn()` writes to `stderr`; in a packaged GUI application with no terminal, `stderr` is typically discarded or redirected to a log file — the user never sees it. The warning should be surfaced by having the caller check `paths_map["is_removable"]` and display a `QMessageBox.warning()` dialog in the GUI, informing the user that SFFS is not running from a USB stick and that sensitive data may be written to the host hard drive.

**Reasoning:** Silent warnings in security-critical paths are dangerous; the user must be informed of the fallback behavior.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 115

---

**Q277. In `f18_thread_controller.py`, `WorkerThread.run()` catches `Exception` broadly and emits the traceback string via `signals.error`. What Python exceptions are NOT subclasses of `Exception` (and thus would NOT be caught), and what would happen to the application if such an exception occurred in `task`?**

**Answer:** `BaseException` subclasses that are not `Exception` subclasses include `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit`. If `task` raised `SystemExit` (e.g., by calling `sys.exit(1)` from within a task — as `emergencyLock()` does), it would propagate uncaught through `WorkerThread.run()`, terminate the QThread, and trigger the Python interpreter's exit machinery. `KeyboardInterrupt` would similarly propagate, potentially crashing the Qt event loop in an uncontrolled way without running `finally` cleanup.

**Reasoning:** This is a known design consideration: `emergencyLock()` intentionally calls `sys.exit(1)`, so it should not be called from a `WorkerThread` task.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.run()` ~line 50

---

**Q278. In `f16_cloud_sync.py`, the OAuth flow `flow.run_local_server(port=0)` opens a browser window for authentication. In a headless server environment where SFFS is running without a display, what would happen when this is called, and how should the code handle this case?**

**Answer:** `flow.run_local_server()` calls `webbrowser.open()` which raises `webbrowser.Error` or silently fails in headless environments. The local redirect server starts on an ephemeral port but the user cannot complete the flow because no browser opens. The `authenticateGoogleDrive()` function would hang waiting for the redirect. The correct fix is to catch `RuntimeError` / check for a display and fall back to `flow.run_console()`, which prints a URL for the user to visit manually and accepts a pasted authorization code.

**Reasoning:** SFFS's CI tests run headless (GitHub Actions), so this path needs a headless fallback or a guard before attempting browser-based OAuth.

**Reference:** `code3/f16_cloud_sync.py` → `authenticateGoogleDrive()` ~line 85

---

**Q279. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` widget accepts `allowed_extensions: list[str] | None`. If `allowed_extensions = [".sffs"]` is passed, `QFileSystemModel.setNameFilters(["*.sffs"])` is set. Does this filter affect the directory tree view or only the file list view? What user confusion could this create?**

**Answer:** `QFileSystemModel` applies name filters globally to the model, so they affect all views sharing the model — including the directory tree on the left. This means the tree view will only show directories that contain `.sffs` files (or no files at all if `setNameFilterDisables(False)` hides non-matching entries). Users would not see directories that contain only non-`.sffs` files, making navigation confusing because valid directories appear to be missing. Ideally, name filters should only apply to the file list pane, not the tree navigation pane.

**Reasoning:** `setNameFilterDisables(False)` hides non-matching files entirely rather than greying them out, amplifying the confusion.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 43

---

**Q280. In `f17_config_loader.py`, the inner function `_write()` calls `_merge_defaults(cfg)` before writing. This means even `configLoader("reset")` passes through `_merge_defaults`. What invariant does `_merge_defaults` guarantee about the stored config, and why is this important for forward compatibility when new keys are added to `DEFAULT_CONFIG`?**

**Answer:** `_merge_defaults` guarantees that every key in `DEFAULT_CONFIG` is present in the stored config, with the default value used if the key was absent in the loaded config. This means that when a new key is added to `DEFAULT_CONFIG` in a future SFFS version, a `load` on an old config file that lacks the new key will return the default value rather than `None` or raising a `KeyError`. This prevents `sffs_core.py` from crashing when it accesses a newly added config key that an older config file never set.

**Reasoning:** This is the standard "fill missing fields with defaults on load" forward-compatibility pattern.

**Reference:** `code3/f17_config_loader.py` → `_merge_defaults()` ~line 46, `_write()` ~line 107

---

**Q281. In `f14_ui_dashboard.py`, the `_on_cloud_backup()` method is connected to the "Cloud backup (optional)" button but only if `core is not None`. What is the behavior if the button is clicked when `core is None` — does Qt prevent the click, silently ignore it, or execute the unconnected handler?**

**Answer:** When `core is None`, the button is disabled with `cloud.setEnabled(False)`. A disabled QPushButton does not emit the `clicked` signal when clicked; Qt's event system ignores all mouse clicks on disabled widgets and renders them in a grayed-out style. The click is silently ignored by Qt — no handler is called, no error is raised. The tooltip `"Enable Google Drive in config when available"` explains to the user why the button is inactive.

**Reasoning:** Disabling the button is both a UI affordance and a runtime safety guard against calling `_core.backupKeys()` on a `None` core.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 294

---

**Q282. In `f13_init_drive_detection.py`, `monitorUSBPresence()` calls `callback()` inside a `try/except Exception: pass` block. What happens if the callback raises `SystemExit` (e.g., from `emergencyLock()` calling `sys.exit(1)`), and does `except Exception` catch `SystemExit`?**

**Answer:** `SystemExit` is a subclass of `BaseException`, not `Exception`, so `except Exception: pass` does NOT catch it. If `callback()` calls `emergencyLock()` which calls `sys.exit(1)`, `SystemExit` propagates uncaught through the `try/except Exception` block, exits the `_run()` function, and terminates the daemon thread — which is the intended behavior. The `except Exception: pass` block correctly limits itself to catching runtime errors in the callback (e.g., a callback that raises `ValueError`) while letting `SystemExit` propagate normally to trigger process exit.

**Reasoning:** This is a correctly designed exception boundary: operational errors are swallowed, intentional exits are allowed through.

**Reference:** `code3/f13_init_drive_detection.py` → `monitorUSBPresence()` ~line 175

---

**Q283. In `f16_cloud_sync.py`, the `cloudSync("list")` action calls `_ensure_backup_folder()` which creates the folder if it doesn't exist. What is the side effect of calling `cloudSync("list")` for the first time, and is this an appropriate side effect for a "read-only" list operation?**

**Answer:** The side effect is that calling `cloudSync("list")` creates the `SFFS_Backup` folder in Google Drive if it does not already exist — a write operation. This is inappropriate for a read-only list operation by the principle of command-query separation. It also means that simply checking whether any backups exist (a diagnostic operation) silently creates infrastructure in the user's Drive. A better design would separate `_ensure_backup_folder()` into an explicit setup step and have `cloudSync("list")` return an empty list (or `{"status": "no_folder"}`) if the folder does not exist.

**Reasoning:** The current design is pragmatic but violates the principle of least side effect for queries.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 221

---

**Q284. In `f18_thread_controller.py`, the `WorkerThread` does not implement `__del__` or any cleanup method. If a `WorkerThread` object is garbage collected while still running, what happens to the underlying OS thread?**

**Answer:** When the Python `WorkerThread` object is garbage collected, Python calls the C++ `QThread` destructor. Qt's `QThread` destructor terminates the thread if it is still running (Qt 5+ emits a warning and waits, or calls `terminate()` depending on version). The OS thread continues executing until the destructor completes or is forcibly terminated; this can leave file handles open, mutexes locked, or partially written files on disk. The safe design is to call `worker.wait()` before allowing garbage collection, which is why storing a reference (as an instance attribute) is essential.

**Reasoning:** This reinforces the importance of keeping a reference to worker threads as discussed in Q215 and Q249.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread` ~line 32

---

**Q285. In `f17_config_loader.py`, `configLoader("save")` reads the current config and merges updates into it. If two threads call `configLoader("save")` concurrently with different updates, describe the race condition that could result and what the final state of the config file might be.**

**Answer:** Thread A reads the current config (state S), Thread B reads the current config (state S), Thread A merges its updates into S to get S+A and writes it, Thread B merges its updates into S (not S+A) to get S+B and writes it — Thread A's updates are lost. The final file contains only Thread B's changes applied to the original state. On FAT32 USBs, file writes are not atomic; a write from Thread B interrupting Thread A's write could also produce a corrupt JSON file. A lock around `_read_current()` + `_write()` is needed.

**Reasoning:** This is a classic TOCTOU race on file-based config storage; the config module has no mutex or file locking.

**Reference:** `code3/f17_config_loader.py` → `configLoader()` ~line 134

---

**Q286. In `f14_ui_dashboard.py`, the status bar at the bottom shows `f"USB free space: ~{free} GB  ·  SFFS v1.0"` using `paths.get("free_space_gb", "?")`. This value is computed once at startup. What happens to the displayed free space after the user encrypts a large file, and why might the displayed value become misleading?**

**Answer:** The `free_space_gb` value is captured by `initDriveDetection()` at startup and stored in the `paths` dict; it is never refreshed. After the user encrypts a large file (producing a `.sffs` file on the USB), the actual free space decreases but the dashboard still shows the startup value. This could mislead the user into believing more space is available than there actually is, potentially causing surprise when a subsequent encryption fails with a disk-full error.

**Reasoning:** The `~` prefix ("approximately") partially mitigates the confusion but the displayed value should be periodically refreshed.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 299

---

**Q287. In `f15_file_manager_explorer.py`, `self._model.setReadOnly(True)` prevents rename/delete through the model. However, the `_ctx_menu()` includes a "Delete" action. If this action were connected to a file deletion handler, what additional checks would be needed to prevent deleting files outside the USB root?**

**Answer:** The handler would need to: (1) resolve the selected path to an absolute path, (2) verify it is a child of `self._root` (the USB root), (3) reject paths with `..` traversal components, (4) confirm the path is a regular file (not a directory or symlink pointing outside the root), and (5) present a confirmation dialog. Without these checks, a symlink inside the USB root pointing to `/etc/passwd` could be followed, or a path like `../../important_host_file` could be accepted if validation is bypassed.

**Reasoning:** The `f07_create_isolated_sandbox.py` sandbox uses similar path confinement checks as a model.

**Reference:** `code3/f15_file_manager_explorer.py` → `_ctx_menu()` ~line 90

---

**Q288. In `f16_cloud_sync.py`, `_ensure_backup_folder()` queries Google Drive with the GDQL query `f"name='{BACKUP_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"`. Is this query vulnerable to GDQL injection if `BACKUP_FOLDER_NAME` contained single quotes, and why is this or is it not a concern in this code?**

**Answer:** Yes, if `BACKUP_FOLDER_NAME` contained a single quote (e.g., `SFFS'Backup`), it would break the GDQL string and could be exploited to inject additional query clauses. However, `BACKUP_FOLDER_NAME = "SFFS_Backup"` is a hardcoded module-level constant containing no special characters, so injection is not possible with the current value. It is a concern only if the folder name were made configurable or user-supplied, at which point the name must be escaped or the query must use a parameter-binding mechanism if the Drive API supports it.

**Reasoning:** The risk is theoretical in the current code but should be flagged for any future refactoring that makes the folder name dynamic.

**Reference:** `code3/f16_cloud_sync.py` → `_ensure_backup_folder()` ~line 124

---

**Q289. In `f18_thread_controller.py`, `WorkerThread.cancel()` sets `self._cancelled = True` but `run()` never checks it. How would you redesign the `WorkerThread.run()` method to support cooperative cancellation at defined checkpoints, and what Python mechanisms (threading.Event, etc.) would you use?**

**Answer:** Replace `self._cancelled = bool` with `self._cancel_event = threading.Event()`. In `cancel()`, call `self._cancel_event.set()`. In `run()`, pass the event (or a lambda `is_cancelled=self._cancel_event.is_set`) to the task as a keyword argument. The task checks the event at safe checkpoints (e.g., between file chunks). If cancellation is detected, the task raises a `CancelledError` or returns a sentinel, which `run()` catches and emits via `signals.error` with a "cancelled" message (or a separate `signals.cancelled` signal). This keeps cancellation cooperative and the task in control of cleanup.

**Reasoning:** `threading.Event` is thread-safe and works across the Python GIL boundary, unlike a plain bool flag.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.cancel()` ~line 43, `run()` ~line 49

---

**Q290. In `f13_init_drive_detection.py`, the `initDriveDetection()` function is called at the start of `SFFSCore.initialize()` and its result stored in `self.paths`. If `initDriveDetection()` raises an exception (e.g., `psutil` fails to enumerate partitions), what is the expected behavior of the application startup, and how should this exception be handled?**

**Answer:** If `initDriveDetection()` raises, `SFFSCore.initialize()` receives an uncaught exception and SFFS cannot start — the path map is essential for all other modules. The expected behavior should be to catch the exception in `main.py` or `SFFSCore.initialize()`, display a user-friendly error message (e.g., `QMessageBox.critical("Startup failed: could not detect USB drive. Ensure psutil is installed.")`), and exit cleanly with a non-zero code. Leaving the exception unhandled would crash to a traceback, leaking path information.

**Reasoning:** Drive detection failure is a hard startup prerequisite; graceful failure with a clear message is the minimum acceptable handling.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 98

---

**Q291. In `f14_ui_dashboard.py`, when `DragDropZone._browse_file()` is called, `QFileDialog.getOpenFileName()` is invoked. What OS-level privileges does opening a native file dialog potentially grant, and why is this more permissive than the scoped `FileManagerExplorer` widget?**

**Answer:** A native file dialog runs with the full filesystem permissions of the SFFS process and allows the user to navigate to any directory on any mounted filesystem. On Windows, the dialog's "Places" sidebar includes `Desktop`, `Documents`, network shares, and all drive letters. On Linux, it can access any path readable by the process user. The `FileManagerExplorer` widget is deliberately scoped to `self._root` (the USB drive), preventing navigation outside the vault. The native dialog grants no additional OS privileges but exposes the entire accessible filesystem to the user's selection, and — critically — records every visited path in the OS MRU.

**Reasoning:** The trade-off is documented: native dialog is used only for the case where `.sffs` files may exist outside the USB vault.

**Reference:** `code3/f14_ui_dashboard.py` → `DragDropZone._browse_file()` ~line 144

---

**Q292. In `f17_config_loader.py`, the `configLoader()` function accepts `action: str` but does not validate it against the allowed set before dispatch (`if action == "reset": ... if action == "load": ...`). The function falls through to `raise ValueError(f"Unknown action: {action}")`. What is the idiomatic Python improvement to this dispatch structure?**

**Answer:** The idiomatic improvement is to use a dispatch dictionary: `handlers = {"reset": _handle_reset, "load": _handle_load, "save": _handle_save, "get": _handle_get}`, then `handler = handlers.get(action)` and `if handler is None: raise ValueError(...)`. Alternatively, Python 3.10+ `match/case` provides structural pattern matching for cleaner dispatch. Both approaches are more readable, easier to extend, and avoid the cascade of sequential `if` statements; the `raise ValueError` at the end then becomes a natural fallback for unmapped keys.

**Reasoning:** The current `if/if/if/if/raise` structure is functionally correct but not idiomatic; it also does not short-circuit early on a valid action.

**Reference:** `code3/f17_config_loader.py` → `configLoader()` ~line 125

---

**Q293. In `f16_cloud_sync.py`, the downloaded backup is written to `Path(local_path).write_bytes(fh.getvalue())`. The `fh` is a `BytesIO` buffer holding the entire downloaded file in memory. For keystore zip files (typically small), this is fine. But what if SFFS were modified to back up `.sffs` encrypted files — what memory limit would this impose?**

**Answer:** `BytesIO` buffers the entire file in RAM before writing. A 1 GB `.sffs` file would require ~1 GB of heap, and a 2 GB file (matching `f03_decrypt_file.py`'s maximum) would require ~2 GB plus Python overhead. On 32-bit systems this would fail; on 64-bit systems with limited RAM it could trigger OOM. The fix is to stream the download directly to disk using `MediaIoBaseDownload` with a real file handle instead of `BytesIO`, which limits RAM usage to one chunk at a time (default 100 MB per chunk).

**Reasoning:** The current code is acceptable for keystores (a few KB) but must be redesigned before extending backup to large files.

**Reference:** `code3/f16_cloud_sync.py` → `cloudSync()` ~line 213

---

**Q294. In `f15_file_manager_explorer.py`, `self._model.setNameFilterDisables(False)` is called when name filters are set. What is the difference between `setNameFilterDisables(True)` and `setNameFilterDisables(False)` in terms of how non-matching files are displayed in the tree view?**

**Answer:** `setNameFilterDisables(True)` (the Qt default) shows non-matching files in the view but renders them as disabled/greyed-out, making them visually distinct but still visible. `setNameFilterDisables(False)` completely hides non-matching files from the view — they do not appear at all. SFFS uses `False` so that only files matching the allowed extensions are visible, providing a cleaner scoped view. The tradeoff is that users cannot see what other files exist in a directory, which could cause confusion if they expect to see all files.

**Reasoning:** For security purposes, hiding non-matching files is preferable; it prevents users from accidentally selecting or noticing files outside the scope.

**Reference:** `code3/f15_file_manager_explorer.py` → `FileManagerExplorer.__init__()` ~line 46

---

**Q295. In `f14_ui_dashboard.py`, the `SFSSDashboard` stores `self._core = core` which is an `SFFSCore` instance. If the user opens a second window (multiple `SFSSDashboard` instances) sharing the same `core`, what concurrency issues would arise when both windows trigger encrypt/decrypt operations simultaneously?**

**Answer:** `SFFSCore` is not designed for concurrent access from multiple windows: two simultaneous encrypt operations would race over shared state like the provenance table (writing duplicate tokens), the sandbox directory (creating conflicting paths), and the audit log (hash chain TOCTOU). Both windows share the same `_session` token, so logout from one window would invalidate the session for the other. In practice, SFFS does not offer multi-window support; `uiDashboard()` creates one window and blocks in `app.exec()`.

**Reasoning:** Single-window design is an implicit architectural constraint enforced by `app.exec()` blocking in `uiDashboard()`.

**Reference:** `code3/f14_ui_dashboard.py` → `SFSSDashboard.__init__()` ~line 188

---

**Q296. In `f17_config_loader.py`, when `encryption_key` is provided but `enc_path` does not yet exist, `_read_current()` returns `{}` and the config is reconstructed from defaults. On subsequent saves, the encrypted config is written. What is the chicken-and-egg problem with providing the encryption key before the config file exists, and how does SFFS resolve this during first-run initialization?**

**Answer:** The encryption key for the config is derived from the user's master password (via Argon2id), but the config itself might store KDF parameters needed to derive that key. On first run, there is no config and no key; SFFS resolves this by running `initDriveDetection()` first (which creates directories), then deriving the key from the user's registration password (hardcoded Argon2id parameters from `f06`), and then calling `configLoader("save", ..., encryption_key=derived_key)` to write the first encrypted config. The `_read_current()` returning `{}` on a missing file is the designed first-run bootstrap path.

**Reasoning:** `_merge_defaults({})` returns a complete config from scratch, so the empty return is handled correctly.

**Reference:** `code3/f17_config_loader.py` → `_read_current()` ~line 104

---

**Q297. In `f13_init_drive_detection.py`, the `drive_label` is obtained from `usb_root.name or str(usb_root)`. On Windows, `Path("D:\\").name` returns `""` (empty string), so `str(usb_root)` is used instead. What is returned for `str(Path("D:\\"))` in Python, and how is this used in the UI?**

**Answer:** `str(Path("D:\\"))` returns `"D:\\"` in Python. This string is used as the `drive_label` in the paths map, which is displayed in the dashboard status bar or drive detection summary. On Windows, users would see `"D:\\"` as the label for their USB drive rather than a volume name like `"USB_DRIVE"`. This is less user-friendly than Windows volume labels but is functionally unambiguous and correctly identifies the drive. On Linux, `usb_root.name` would return the last component of the mount point (e.g., `"USB"`), which is more readable.

**Reasoning:** The fallback to `str(usb_root)` handles the Windows-specific edge case where drive-letter roots have no `name` component.

**Reference:** `code3/f13_init_drive_detection.py` → `initDriveDetection()` ~line 127

---

**Q298. In `f18_thread_controller.py`, `WorkerThread.run()` calls `self.signals.finished.emit()` in a `finally` block, guaranteeing it is always emitted. Why is it important for the GUI application (connected via `finished_callback`) to not assume the task succeeded just because `finished` was emitted?**

**Answer:** `finished` is emitted regardless of whether the task completed successfully or raised an exception. If an exception occurred, `signals.error` was emitted instead of `signals.result`. A `finished_callback` that assumes success (e.g., by proceeding to the next pipeline step without checking whether `result` was received) would incorrectly continue after a failed encryption, potentially creating a corrupt `.sffs` file or leaving the sandbox in a dirty state. The callback should track whether `result` or `error` was received before `finished` fires.

**Reasoning:** `finished` signals completion (success or failure); it is a lifecycle event, not a success indicator.

**Reference:** `code3/f18_thread_controller.py` → `WorkerThread.run()` ~line 55

---

**Q299. In `f16_cloud_sync.py`, the `authenticateGoogleDrive()` function writes the OAuth token to `google_token.json` with `token_path.write_text(creds.to_json(), encoding="utf-8")`. The token JSON contains a `refresh_token`. What is a refresh token, why is it more sensitive than an access token, and what file permission should be applied to protect it?**

**Answer:** An access token is a short-lived credential (typically 1 hour) granting specific API scopes; a refresh token is a long-lived credential (months to years) that can generate new access tokens without user interaction. An attacker with a refresh token can maintain persistent access to the user's Google Drive backup folder indefinitely, even after the original access token expires. `google_token.json` should be written with mode `0o600` (owner read/write only) on Linux/macOS using `os.open()` with `O_CREAT | O_WRONLY` and mode `0o600`, rather than `Path.write_text()` which inherits the umask.

**Reasoning:** On FAT USB drives, file permissions are not enforced, but on ext4 drives or host filesystems they are; the code should set restrictive permissions where supported.

**Reference:** `code3/f16_cloud_sync.py` → `authenticateGoogleDrive()` ~line 87

---

**Q300. In `f14_ui_dashboard.py` and `f18_thread_controller.py` together, the pattern of running crypto operations (`encryptFileOperation`, `decryptFileOperation`) in `WorkerThread` and reporting progress via `pyqtSignal(int)` is described. Trace the full signal-slot chain from a user clicking "Encrypt selection" to the progress bar reaching 100%, identifying every class and signal that participates in keeping the UI responsive while cryptography runs in the background.**

**Answer:** (1) User clicks `_enc` button → `QPushButton.clicked` signal fires on the main (GUI) thread. (2) The connected slot calls `threadController(task=sffs_core.encryptFileOperation, ..., progress_callback=dashboard.updateProgress, done_callback=..., finished_callback=...)`. (3) `threadController` creates a `WorkerThread`, connects `worker.signals.progress` → `updateProgress`, connects other callbacks, calls `worker.start()` and returns the worker. (4) Qt starts the OS thread; `WorkerThread.run()` calls `sffs_core.encryptFileOperation()` on the background thread. (5) Inside `encryptFileOperation`, at each stage (key gen, encrypt chunks, provenance) the task calls `worker.signals.progress.emit(percent)` — this posts a queued event to the GUI thread's event queue. (6) The main event loop dequeues the event and calls `SFSSDashboard.updateProgress(percent)` on the GUI thread, which calls `self._bar.setVisible(True)` and `self._bar.setValue(percent)` — widget updates are safe here. (7) At 100%, `encryptFileOperation` returns a result dict; `WorkerThread.run()` emits `signals.result.emit(result_dict)` (queued to GUI thread) then `signals.finished.emit()` in `finally`. (8) `done_callback` receives the result on the GUI thread, shows a success dialog; `finished_callback` hides the progress bar. Throughout steps 4–7, the Qt event loop continues processing other events (repaints, button presses) on the GUI thread, keeping the UI responsive.

**Reasoning:** The full chain relies on Qt's queued connection mechanism to marshal all UI updates from the background worker thread back to the main GUI thread without explicit locking.

**Reference:** `code3/f14_ui_dashboard.py` → `updateProgress()` ~line 350; `code3/f18_thread_controller.py` → `threadController()` ~line 59, `WorkerThread.run()` ~line 49, `WorkerSignals.progress` ~line 25
