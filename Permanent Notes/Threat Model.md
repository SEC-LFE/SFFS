For future Claude. SFFS threat model covering attack vectors and mitigations across all modules.

## Threat Model

| Threat | Vector | Mitigation | Module |
|--------|--------|------------|--------|
| Unauthorized file access | Physical access to disk | AES-256-GCM encryption + RSA key wrapping | Student 1 |
| Key theft | Read key file | PBKDF2/Argon2id + AES-GCM encrypted keystore | Student 1 |
| Brute-force password | Login endpoint | Argon2id (memory-hard) + exponential backoff lockout | Student 2 |
| Malicious file execution | Open decrypted file | Sandbox isolation (Job/AppArmor) + viewer manifest | Student 2 |
| Memory scraping | Post-decryption buffer | DoD 5222.22-M 3-pass secure wipe | Student 2 |
| Audit tampering | Modify log entries | SQLite hash chain (each entry links to previous hash) | Student 2 |
| IPC replay attack | Replay valid envelope | Nonce tracking + 10s expiry in isolated_worker | main-code |
| Path traversal | Malicious file path in sandbox | Zip/archive traversal rejection + sandbox root enforcement | Student 2 |
| Weak session keys | Predictable RNG | Mouse entropy ⊕ OS CSPRNG | Student 3 |
| Cloud credential leak | Unencrypted token file | Backup encryption before upload (unencrypted upload blocked) | Student 3 |

## Assumptions
- Attacker has physical access to the machine (no disk encryption assumed)
- Attacker can observe side-channel timing (constant-time comparison required)
- Attacker can replay captured IPC messages (nonce system required)
- User's password may be weak (Argon2id + backoff required)

## Non-Goals
- Network security (no TLS enforcement at application level)
- Side-channel resistance beyond timing (no power/EM analysis protection)
- Full disk encryption (expected to run on top of BitLocker/LUKS)
- Secure enclave/HSM (no hardware security module integration, though noted as future work)

## Related
- [[Sandbox Isolation Design]]
- [[SFFS Core Architecture]]
- [[Crypto Design Decisions]]
- [[01-Projects/Student 2 Security Module]]
