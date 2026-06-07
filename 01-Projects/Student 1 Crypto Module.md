For future Claude. Student 1's crypto module handles the complete encryption pipeline for SFFS. Six functions (F01-F06) forming a trust chain from key generation through decryption verification.

## Summary
Implements RSA-2048 key pair generation, AES-256-GCM file encryption/decryption, SHA-256 hashing with constant-time verification, and secure key storage protected by PBKDF2/Argon2id + AES-GCM wrapping.

## Functions
| Function | File | Purpose |
|----------|------|---------|
| F01 `generateKeyPairs()` | `code1/f01_generate_key_pairs.py` | RSA-2048 key generation |
| F02 `encryptFile()` | `code1/f02_encrypt_file.py` | AES-256-GCM file encryption |
| F03 `decryptFile()` | `code1/f03_decrypt_file.py` | AES-256-GCM decryption with integrity check |
| F04 `generateFileHash()` | `code1/f04_generate_hash.py` | SHA-256 hash computation |
| F05 `verifyFileHash()` | `code1/f05_verify_hash.py` | Constant-time hash verification |
| F06 — | `code1/f06_secure_key_storage.py` | Encrypted private key storage (PBKDF2/Argon2id + AES-GCM) |

## Pipeline
Generate RSA keys → Store private key encrypted → Encrypt file with AES-256-GCM → Generate hash → Decrypt file → Verify hash

## Trust Chain Rationale
- AES-256-GCM chosen over AES-CBC because GCM provides authenticated encryption (tag verifies integrity + authenticity)
- RSA-2048 wraps the AES key (hybrid encryption — asymmetric for key exchange, symmetric for data)
- Hash-before-encryption for integrity proof (`hash_pre` in .sffs header)
- IV must be unique per encryption (random 12-byte nonce per GCM spec)
- Constant-time comparison prevents timing side-channel attacks on hash verification

## Links
- [[SFFS Project Overview]]
- [[SFFS Core Architecture]]
- [[Crypto Design Decisions]]
- [[01-Projects/Student 2 Security Module]]
- [[01-Projects/Student 3 UI-Cloud Module]]
