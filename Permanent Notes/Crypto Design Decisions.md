For future Claude. Cryptographic design decisions and rationale for the SFFS system, extracted from code comments and README docs.

## Why AES-256-GCM?
- Authenticated encryption (AEAD) — provides both confidentiality and integrity in one pass
- GCM mode includes an authentication tag that detects tampering
- Replaces AES-CBC + HMAC combination (simpler, faster, standard)
- IV/nonce must be unique per key (12-byte random nonce)

## Why RSA-2048?
- 2048-bit key provides 112-bit security level (NIST minimum through 2030)
- Used for key wrapping only — encrypts the AES-256 key, not the file data
- Hybrid encryption: RSA for key exchange, AES for bulk data

## Why Argon2id?
- Memory-hard function — resistant to GPU/ASIC brute force
- Winner of the Password Hashing Competition (2015)
- Configurable memory cost (prevents parallel attacks)
- Used for deriving encryption key from user password

## Why SHA-256?
- 256-bit output — collision resistance ~2^128
- Used for `hash_pre` in .sffs header (stored before encryption for integrity proof)
- Hash chain for audit log entries (prevents retroactive modification)

## Why Constant-Time Comparison?
- Prevents timing side-channel attacks on hash verification
- Standard Python `hmac.compare_digest()` (not `==` which short-circuits)

## Why Mouse Entropy?
- Augments OS CSPRNG with hardware entropy from mouse movements
- XOR-mixed into per-session file keys
- Mitigates against weak CSPRNG seeding in headless/server environments

## SFFS Binary Format
```
Magic(4) | Version(2) | KeyID(8) | IV(12) | AES-GCM Tag(16) | Ciphertext(*) | hash_pre(32)
```
- Magic: `0xSFFS` (4 bytes)
- Version: 2 bytes (currently 0x0100)
- KeyID: 8 bytes identifying which RSA key encrypted the AES key
- IV: 12 bytes random nonce for GCM
- Tag: 16-byte GCM authentication tag
- Ciphertext: AES-256-GCM encrypted payload
- hash_pre: SHA-256 of ciphertext (for integrity verification before decrypt)

## Related
- [[SFFS Project Overview]]
- [[SFFS Core Architecture]]
- [[01-Projects/Student 1 Crypto Module]]
