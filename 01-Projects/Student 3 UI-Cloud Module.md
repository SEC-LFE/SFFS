For future Claude. Student 3's module delivers the PyQt6 GUI, USB drive detection, file management, cloud sync (Google Drive), configuration loader, and thread management for SFFS.

## Summary
Provides the user-facing interface: login/dashboard UI, two-pane file explorer, sandbox viewer, mouse entropy pool for session keys, Google Drive backup, encrypted config storage, and Qt worker thread controller. Includes USB drive detection for portable deployment.

## Components
| Component | File | Purpose |
|-----------|------|---------|
| F13 Drive Detection | `code3/f13_init_drive_detection.py` | USB/portable path detection (Windows + Linux) |
| F14 UI Dashboard | `code3/f14_ui_dashboard.py` | PyQt6 main window, dark theme, drag-drop zones |
| F15 File Explorer | `code3/f15_file_explorer.py` | Two-pane explorer: directory tree + file list |
| F16 Cloud Sync | `code3/f16_cloud_sync.py` | Google Drive OAuth2 backup/restore |
| F17 Config Loader | `code3/f17_config_loader.py` | Encrypted JSON config (AES-256-GCM) |
| F18 Thread Ctrl | `code3/f18_thread_controller.py` | Qt WorkerThread for async task execution |
| Mouse Entropy | `code3/mouse_entropy.py` | Mouse-movement entropy pool ⊕ OS CSPRNG |

## UI Features
- Dark, high-contrast stylesheet (shield/lock aesthetic)
- Drag-and-drop file zones (encrypt/decrypt)
- Sandbox file viewer with text preview + secure external viewer launch
- Real-time USB presence monitoring
- Google Drive backup (optional, OAuth 2.0)

## Related
- [[SFFS Project Overview]]
- [[SFFS Core Architecture]]
- [[01-Projects/Student 1 Crypto Module]]
- [[01-Projects/Student 2 Security Module]]
