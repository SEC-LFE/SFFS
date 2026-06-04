For future Claude. Architectural synthesis from graphify knowledge graph analysis of the SFFS codebase. This note captures the system architecture, component relationships, and design rationale.

## System Architecture
```
┌──────────────────────────────────────────────┐
│                main-code/                     │
│  SFFSCore ── isolated_worker ── provenance   │
│       │         │                  │          │
│    wrap_store   IPC signing    hash chain     │
└───────┬──────────────────────────────────────┘
        │
   ┌────┴────┬────────────────┬────────────────┐
   │         │                │                │
┌──▼──────┐ ┌▼──────────┐ ┌──▼──────────┐ ┌──▼──────┐
│ code1/  │ │ code2/    │ │ code3/      │ │ tests/  │
│ Crypto  │ │ Security  │ │ UI/Cloud    │ │ Suite   │
│ F01-F06 │ │ F07-F12   │ │ F13-F18     │ │ All     │
└─────────┘ └───────────┘ └─────────────┘ └─────────┘
```

## Cross-Cutting Concerns
- **AuditLogger** (52 edges) — touched by every security operation
- **SecurityError** (35 edges) — bridges crypto decryption, IPC, and sandbox
- **WorkerThread** (43 edges) — connects UI to all async operations

## Data Flow
1. User login (F09 Argon2id auth)
2. Dashboard loads (F14) → Drive detection (F13)
3. File selected in explorer (F15) → Encrypt (F02) with key from storage (F06)
4. Hash computed (F04) → Written to .sffs format
5. Decrypt (F03) → Verify hash (F05) → Open in sandbox (F07)
6. All operations logged via AuditLogger (F11)
7. Optional: sync to Google Drive (F16)

## Integration Layer
- `isolated_worker.py` runs decryption in isolated subprocess with signed IPC envelopes (replay protection via nonce tracking + 10s expiry)
- `provenance_table.py` maintains hash-linked audit trail
- `wrap_store.py` handles encrypted secure store
- `sffs_core.py` orchestrates all modules

## Security Properties
- **Confidentiality**: AES-256-GCM + RSA-2048 key wrapping
- **Integrity**: SHA-256 hash_pre in .sffs header + GCM auth tag
- **Authentication**: Argon2id password hashing + constant-time comparison
- **Isolation**: Windows Job Objects / Linux AppArmor sandbox
- **Audit**: SQLite hash chain (tamper-evident log)
- **Memory Safety**: DoD 5220.22-M 3-pass wipe

## Related
- [[SFFS Project Overview]]
- [[Crypto Design Decisions]]
- [[Sandbox Isolation Design]]
- [[Threat Model]]
