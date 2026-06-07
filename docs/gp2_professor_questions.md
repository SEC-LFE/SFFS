# GP2 Exam Questions — SFFS

## Student 1 — Cryptography (code1, f01–f06)

Q1. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function raises a `ValueError` if `key_size < 2048`. Explain why 2048 bits is enforced as the minimum and what security level (in equivalent symmetric bits) this provides according to the module's own documentation.

Q2. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function uses `public_exponent=65537`. Why is 65537 chosen as the RSA public exponent rather than a smaller value like 3? What are the security and performance tradeoffs?

Q3. In `f01_generate_key_pairs.py`, the key_id is computed as `hashlib.sha256(public_pem).hexdigest()[:16]`. An earlier version used only 8 hex characters. The comment says the change was made because "at 8 chars the birthday collision probability is ~1/2^32 — borderline." Explain the birthday paradox and why 16 hex chars (64 bits) was chosen instead.

Q4. In `f01_generate_key_pairs.py`, the private key is exported using `PrivateFormat.TraditionalOpenSSL` with `NoEncryption()`. Why is `NoEncryption()` used here even though the private key is sensitive, and what must the caller do immediately after receiving `private_key_bytes` to ensure security?

Q5. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function writes the public key to disk but only returns the private key as in-memory bytes. Why is the public key safe to write to disk while the private key is not?

Q6. In `f02_encrypt_file.py`, AES-256-GCM is chosen over AES-256-CBC. List at least two reasons stated in the module's docstring for preferring GCM, and explain what "authenticated encryption" means in practical terms.

Q7. In `f02_encrypt_file.py`, the IV is generated using `secrets.token_bytes(12)` rather than 16 bytes. The comment explains that 12-byte (96-bit) nonces avoid an internal GHASH reduction. Explain what this GHASH reduction is and why the 12-byte IV is the recommended GCM nonce length.

Q8. In `f02_encrypt_file.py`, the `encryptFile()` function requires `aes_key` to be exactly 32 bytes and raises `ValueError` if it is not. What would happen at the cryptographic level if a 16-byte key were silently accepted instead of rejected?

Q9. In `f02_encrypt_file.py`, the SFFS file format header includes `SFFS_MAGIC = b"SFFS"` and `SFFS_VERSION = 0x03`. What is the purpose of the magic bytes, and how does the version byte (`0x03`) assist the decryption module when supporting multiple format generations?

Q10. In `f02_encrypt_file.py`, the original file extension is stored inside the encrypted header rather than preserved in the `.sffs` filename. What security goal does this achieve, and what is the maximum allowed extension length and why?

Q11. In `f02_encrypt_file.py`, a `file_token` of 32 random bytes is generated and stored in the plaintext header of the `.sffs` file. The docstring states "Security comes from the table (secret), not from hiding the token bytes in the file." Explain this provenance design: how does an attacker fail to bypass it even though they can read the token from the file?

Q12. In `f02_encrypt_file.py`, the SHA-256 hash of the plaintext is computed BEFORE encryption and stored in the header as `hash_pre`. Why is it important to hash the plaintext before encryption rather than hashing the ciphertext?

Q13. In `f02_encrypt_file.py`, the `AESGCM.encrypt()` call passes `associated_data=None`. In AES-GCM, what is associated data (AAD), and what security property would be gained if the SFFS file header bytes were passed as AAD?

Q14. In `f02_encrypt_file.py`, the output file is written as `header + ciphertext` in a single `write_bytes()` call. Why is atomic writing of the complete encrypted file important from a security standpoint, compared to writing header and ciphertext in two separate calls?

Q15. In `f03_decrypt_file.py`, the `decryptFile()` function includes a `MAX_FILE_BYTES = 2 * 1024 ** 3` (2 GB) guard. What memory-related risk does this guard prevent, and why does AES-GCM specifically require the entire ciphertext in memory at once?

Q16. In `f03_decrypt_file.py`, the function accepts both version `0x02` (legacy) and `0x03` (current) SFFS files. What design principle does this represent, and what security risk could arise from indefinitely supporting old format versions?

Q17. In `f03_decrypt_file.py`, the `SecurityError` class is a custom exception rather than using Python's built-in `ValueError`. Why does the code define a custom `SecurityError`, and what does this enable in the calling code that catching `ValueError` would not?

Q18. In `f03_decrypt_file.py`, when the GCM auth tag fails, any partial output file is deleted before the `SecurityError` is raised. What attack does this prevent? Give a concrete example of how a partially decrypted file could be exploited.

Q19. In `f03_decrypt_file.py`, the provenance token check occurs BEFORE the AES key is used. The comment states "Nothing is decrypted until provenance passes." Why is this ordering critical from a security standpoint?

Q20. In `f03_decrypt_file.py`, the provenance token comparison uses `hmac.compare_digest(file_token, expected_token)`. Why is `compare_digest` used instead of the `==` operator, and what attack does this constant-time comparison prevent?

Q21. In `f03_decrypt_file.py`, when `UnicodeDecodeError` is raised while reading the original extension from the header, a `ValueError` is raised with the message "SFFS file corrupted." Why might a malformed UTF-8 extension field be a security concern beyond mere file corruption?

Q22. In `f03_decrypt_file.py`, the decrypted output is written to `output_dir` which is described as an isolated sandbox directory. Why does the module docstring state it is a "security risk" to decrypt to the host OS disk (`C:` drive, `/home/user`)?

Q23. In `f04_generate_hash.py`, the `generateHash()` function supports three algorithms: `sha256`, `sha512`, and `blake2b`. Why is MD5 explicitly not supported, and what makes SHA-1 and MD5 unsuitable for security-critical integrity verification?

Q24. In `f04_generate_hash.py`, files are processed in `CHUNK_SIZE = 8 * 1024 * 1024` (8 MB) chunks. Why is streaming hashing in chunks necessary for large files, and what would happen if the entire file were loaded into memory at once on a system with limited RAM?

Q25. In `f04_generate_hash.py`, the `generateHash()` function accepts `Union[Path, bytes, str]` as its `target` parameter. What is the purpose of normalizing `str` inputs to `Path` objects (line 65), and why does this improve the function's usability without compromising security?

Q26. In `f04_generate_hash.py`, the BLAKE2b algorithm is offered as an alternative to SHA-256. The docstring states it is "faster than SHA-256 for large files" and "stdlib since Python 3.6 — no external dependency needed." What are the security tradeoffs of using BLAKE2b versus SHA-256 in a FIPS-140-2 compliant environment?

Q27. In `f04_generate_hash.py`, the `generateFileHash()` convenience function always uses SHA-256 regardless of which algorithm the user prefers. What consistency issue could arise if `generateFileHash()` is used in one place and `generateHash(path, "blake2b")` in another when comparing hash values?

Q28. In `f05_verify_hash.py`, the `verifyHash()` function returns a truncated version of both hashes in its result dict: `hash_pre[:16] + "..."`. Why are full hash values truncated in the output, and what security risk would returning full hashes pose?

Q29. In `f05_verify_hash.py`, the `verifyHash()` function returns `alert_level = "CRITICAL_TAMPER_DETECTED"` when hashes don't match. In a real deployed system, what actions should be taken programmatically when this alert level is returned, and what are the forensic implications?

Q30. In `f05_verify_hash.py`, the `verifyFileIntegrity()` function reads the `hash_pre` from the `.sffs` file header by seeking to byte offset `4 + 1 + 12 = 17`. Why is this calculation fragile with respect to format versioning, and how does this relate to the V3 format adding a variable-length extension field?

Q31. In `f05_verify_hash.py`, the module docstring describes a Man-in-the-Middle (MitM) scenario where an attacker flips bits in the ciphertext. How does AES-GCM's built-in authentication tag already address this threat, and why is the separate SHA-256 hash still necessary?

Q32. In `f05_verify_hash.py`, `hmac.compare_digest(hash_pre, hash_post)` is used for the hash comparison. Describe concretely how a timing attack on a naive `hash_pre == hash_post` comparison would work step-by-step, and why it is more feasible in a network service context than in a local file check.

Q33. In `f06_secure_key_storage.py`, two KDF options are supported: `ARGON2ID` (default) and `PBKDF2-SHA256` (compatibility fallback). What makes Argon2id superior to PBKDF2 for password-based key derivation, specifically against GPU-based brute-force attacks?

Q34. In `f06_secure_key_storage.py`, the `ARGON2_MEMORY_COST = 65536` (KiB = 64 MB). Explain how memory-hardness works as a defense: why does requiring 64 MB of RAM per hash attempt slow down GPU attacks specifically?

Q35. In `f06_secure_key_storage.py`, the salt is 16 bytes generated per keystore. Why must the salt be unique per keystore, and why is it safe to store the salt in plaintext alongside the encrypted private key?

Q36. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function copies `private_key_bytes` into a `bytearray` called `private_key_mutable`, then zeros it byte-by-byte after encryption. Why is a `bytearray` used instead of `bytes`, and why is the byte-by-byte zeroing loop necessary rather than just `del private_key_bytes`?

Q37. In `f06_secure_key_storage.py`, the keystore JSON stores a `"version"` field: `"2.0"` for Argon2id and `"1.0"` for PBKDF2. In `retrieveKey()`, the code reads the `"kdf"` field and dispatches to the appropriate KDF. What backward-compatibility risk exists if the `"kdf"` field is absent in a legacy keystore, and how does the code handle it?

Q38. In `f06_secure_key_storage.py`, the `hashlib_sha256_sandwich()` function computes `hash(salt || hash(iv))` to generate a `key_id`. Why is a "sandwich" construction (inner hash first, then outer hash) used here rather than a simple `hash(salt + iv)`? What length-extension attack does this defend against?

Q39. In `f06_secure_key_storage.py`, the `wrapAESKey()` function uses `RSA-OAEP-SHA256` (via `PKCS1_OAEP.new(public_key, hashAlgo=SHA256)`). Why is OAEP padding required for RSA encryption, and what vulnerability exists with raw RSA (textbook RSA) encryption?

Q40. In `f06_secure_key_storage.py`, the `wrapAESKey()` function includes a `key_commitment` field: `hashlib.sha256(aes_key).hexdigest()`. What does key commitment verify during `unwrapAESKey()`, and what attack does it prevent that RSA-OAEP alone does not prevent?

Q41. In `f06_secure_key_storage.py`, the `wrapAESKey()` function uses `_hmac.new(aes_key, _h.digest(), hashlib.sha256).hexdigest()` to create a `bound_file_mac` instead of storing the raw SHA-256 of the `.sffs` file. The comment explains this prevents a "correlation attack." Describe this correlation attack: what could an attacker learn from the raw file hash?

Q42. In `f06_secure_key_storage.py`, the `unwrapAESKey()` function supports both `bound_file_sha256` (legacy) and `bound_file_mac` (v2.1+). What backwards-compatibility risk does supporting the legacy plaintext SHA-256 binding introduce, and how should this be phased out?

Q43. In `f06_secure_key_storage.py`, the keystore JSON is written via `keystore_path.write_text(json.dumps(keystore, indent=2))` to a `.json` file. What are the security implications of storing the keystore as a human-readable JSON file versus a binary format, and what protection does the AES-GCM encryption provide against file system leakage?

Q44. In `f06_secure_key_storage.py`, the `verifyKeystorePassword()` function attempts to decrypt the private key and returns `{"valid": True}` on success without returning the key itself. What security principle does this function implement, and why is it preferable to calling `retrieveKey()` directly just to check a password?

Q45. In `f06_secure_key_storage.py`, the `KDF_ITERATIONS = 310_000` constant is used for PBKDF2 with the comment "NIST SP 800-63B (2023) recommends ~200k iterations for SHA-256." Why does SFFS use 310,000 iterations rather than exactly 200,000, and what is the tradeoff between increasing iterations and user experience?

Q46. In `f01_generate_key_pairs.py`, the `generated_at` timestamp is produced using `datetime.datetime.now().isoformat()` — a local time without timezone. What auditing problems could arise from using a naive local timestamp in a USB-portable system used across timezones?

Q47. In `f02_encrypt_file.py`, the `file_token` is described as "registered in the provenance table (sffs_data/provenance.json) keyed by hash_pre." Why is `hash_pre` (SHA-256 of the original plaintext) used as the lookup key in the provenance table rather than the filename or the token itself?

Q48. In `f03_decrypt_file.py`, the import `import hmac as _hmac_mod` appears inside the body of the `decryptFile()` function (inside an `if version == 0x03` block). What is the reason for this lazy import rather than placing it at the module top level?

Q49. In `f06_secure_key_storage.py`, the `rng_func` parameter in `secureKeyStorage()` defaults to `get_random_bytes` but can be overridden with a custom callable. The docstring says "Pass `session_random_bytes` to mix in mouse-movement entropy." What are the security implications of allowing an arbitrary `rng_func`, and how does the `mouse_entropy.session_random_bytes` function ensure the random bytes are still cryptographically strong even if the mouse pool is empty?

Q50. In `f06_secure_key_storage.py`, after AES-GCM encryption of the private key, the code stores `auth_tag` as a separate base64 field in the JSON (`"auth_tag": auth_tag_b64`). In `retrieveKey()`, the code calls `cipher.decrypt_and_verify(encrypted_key, auth_tag)`. Why does PyCryptodome's GCM API separate the auth tag from the ciphertext, whereas the `cryptography` library's `AESGCM` (used in f02/f03) appends the tag to the ciphertext automatically?

Q51. In `f02_encrypt_file.py`, the plaintext is encrypted directly: `ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)`. An earlier design described injecting the provenance token into the plaintext at a `token_offset` before encryption. Why was the design changed to store the token in the plaintext header instead of inside the ciphertext?

Q52. In `f01_generate_key_pairs.py`, the public key is saved in `SubjectPublicKeyInfo` format rather than the older `PKCS1` format. What is the difference between these two PEM formats, and why does the `wrapAESKey()` function in `f06_secure_key_storage.py` need to handle the key format correctly when importing it?

Q53. In `f04_generate_hash.py`, when `target` is a `bytes` object, the entire bytes value is hashed in a single call (e.g., `sha256(target).hexdigest()`) rather than using the streaming chunked approach. Is this a security issue? Under what conditions could a `bytes` input cause memory exhaustion?

Q54. In `f05_verify_hash.py`, `verifyFileIntegrity()` has special-case logic for `.sffs` files that reads `hash_pre` from the binary header. What happens if the function is called on a V3 `.sffs` file (which has a variable-length extension field between the file size and the provenance token)? Will the `hash_pre` extraction still be correct?

Q55. In `f03_decrypt_file.py`, `output_path = output_dir / (sffs_path.stem + original_ext)` restores the original filename by combining the `.sffs` stem with the stored extension. What path traversal risk exists if `original_ext` were stored as something like `"/../../../etc/passwd"`, and does the current code guard against this?

Q56. In `f06_secure_key_storage.py`, `restoreKeysFromCloud()` in `sffs_core.py` validates zip members with `if member_path.is_absolute() or ".." in member_path.parts`. Discuss whether this path traversal check is sufficient. Are there edge cases (e.g., on Windows with drive letters, or with symlinks) that it might miss?

Q57. In `f02_encrypt_file.py`, the `SFFS_VERSION` constant is set to `0x03`. If a future version needed to encrypt large files in chunks rather than loading the entire plaintext into memory, what changes would need to be made to the file format and the `encryptFile()` function?

Q58. In `f06_secure_key_storage.py`, the `secureKeyStorage()` and `retrieveKey()` functions both re-derive the AES wrap key from the master password every time they are called. What is the performance cost of Argon2id with `time_cost=3, memory_cost=65536, parallelism=4` at login time, and why is this cost intentional?

Q59. In `f01_generate_key_pairs.py`, no mechanism prevents generating multiple RSA key pairs for the same user. In `sffs_core.py`, `_ensure_rsa_keys()` calls `sorted(keys_dir.glob("public_key_*.pem"))` and picks `candidates[0]`. What could go wrong if two key pairs exist and the user's keystore was created with `candidates[1]`?

Q60. In `f03_decrypt_file.py`, the `decryptFile()` function writes the decrypted plaintext to disk before returning. Describe a scenario in which this represents a security risk even with a properly isolated sandbox, and what additional protection could be added (such as the sandbox watcher in `sffs_core.py`).

Q61. In `f06_secure_key_storage.py`, the `wrapAESKey()` function creates a JSON envelope with `json.dumps(envelope, separators=(",", ":"))`. Why are compact separators used (no spaces), and what is the security significance of the `sort_keys` behavior when creating the HMAC signature in `sffs_core.py`'s `_sign_worker_payload()`?

Q62. In `f02_encrypt_file.py`, the `secrets` module is used for both `file_token = secrets.token_bytes(32)` and `iv = secrets.token_bytes(12)`. Why is `secrets` preferred over `random.getrandbytes()` for cryptographic random generation in Python?

Q63. In `f06_secure_key_storage.py`, `ARGON2_PARALLELISM = 4` is used. Explain what the parallelism parameter controls in Argon2id, and why a higher parallelism value does not proportionally increase GPU attack cost in the way that higher memory cost does.

Q64. In `f05_verify_hash.py`, the `verifyHash()` function returns `"match": True/False` and `"alert_level"`. In the calling context (decryption pipeline), what would be the correct behavior if `match == False`: silently continue, raise an exception, or call `emergencyLock()`? Justify your answer with reference to the threat model.

Q65. In `f02_encrypt_file.py`, the function signature includes `aes_key: bytes` but nowhere generates the AES key itself. In `sffs_core.py`'s `encryptFileOperation()`, the key is generated with `aes_key = session_random_bytes(32)`. Why is key generation deliberately separated from the encryption function rather than letting `encryptFile()` generate its own key?

Q66. In `f01_generate_key_pairs.py`, the module docstring outlines the "Key Lifecycle in SFFS" in four numbered steps. What would happen to the security of the entire system if step 2 (passing the private key to `secureKeyStorage()`) were skipped and the key bytes were instead returned to the caller and stored as a plain text file?

Q67. In `f06_secure_key_storage.py`, the keystore format version is `"2.0"` for Argon2id and `"1.0"` for PBKDF2. If the `"version"` field were used to choose the KDF rather than the `"kdf"` field, what specific attack could a malicious keystore file mount by setting `version = "1.0"` for a keystore that was actually encrypted with Argon2id?

Q68. In `f03_decrypt_file.py`, after the provenance token check, the ciphertext is decrypted with `decrypted = aesgcm.decrypt(iv, ciphertext, None)`. At what point in this call does GCM authentication tag verification occur, and what exception is raised if the tag is invalid?

Q69. In `f04_generate_hash.py`, the `generateHash()` function raises `TypeError` if `target` is neither `Path`, `str`, nor `bytes`. What is the security rationale for raising an exception rather than silently casting an unknown type (e.g., converting an integer to its string representation before hashing)?

Q70. In `f06_secure_key_storage.py`, the `retrieveKey()` function catches `ValueError` from `cipher.decrypt_and_verify()` and re-raises it as a new `ValueError` with a generic message. What information is deliberately omitted from the error message to prevent a timing or oracle attack?

Q71. In `f02_encrypt_file.py`, the function returns a `file_token` field but the caller in `sffs_core.py` is responsible for registering it in the provenance table. What is the risk if a file is encrypted but the provenance registration step is skipped (e.g., due to a crash between `encryptFile()` returning and `_provenance_table.register()` being called)?

Q72. In `f01_generate_key_pairs.py`, the public key filename is `public_key_{key_id}.pem` where `key_id` is derived from the hash of the public key PEM. Why is it important that the filename contains the key_id, as opposed to a fixed name like `public_key.pem`? What data-loss scenario does this prevent?

Q73. In `f06_secure_key_storage.py`, the GCM IV for key wrapping is 12 bytes (`iv = _rng(12)`), matching the NIST-recommended nonce length. If the same IV were accidentally reused with the same derived AES wrap key (e.g., on a system with a weak RNG), what specific property of AES-GCM would be catastrophically broken?

Q74. In `f05_verify_hash.py`, the module explains that `hash_pre` proves "original plaintext integrity" and that "any tampering (even 1 bit) changes the hash completely (avalanche effect)." Explain the avalanche effect mathematically: in SHA-256, approximately how many output bits are expected to change when 1 input bit is flipped?

Q75. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function generates a `key_id` using `hashlib_sha256_sandwich(salt, iv)` when no `key_id` is supplied. This ID is only 16 hex characters (8 bytes). What is the probability of a collision among `N` keystores using the birthday paradox formula, and at what value of N does this probability exceed 1%?

Q76. In `f03_decrypt_file.py`, the module docstring lists 10 steps in the "Decryption Process." Step 9 says "Compare hash_post with hash_pre (via verifyHash module)." In the actual implementation of `decryptFile()`, this comparison is NOT performed — it returns both hashes but leaves comparison to the caller. Is this an implementation bug or intentional design? Justify.

Q77. In `f02_encrypt_file.py`, the comment on line 138 says "no token injection into plaintext." An earlier design injected the 32-byte token at a random `token_offset` inside the plaintext before encryption. What was the security rationale for that approach, and why was it changed to storing the token in the plaintext header?

Q78. In `f06_secure_key_storage.py`, the `KDF_ITERATIONS = 310_000` constant is declared at module level, but Argon2id parameters (`ARGON2_TIME_COST`, etc.) are also declared at module level. Why is it important that these constants match between `secureKeyStorage()` and `retrieveKey()`, and what would happen if a developer changed `ARGON2_MEMORY_COST` in a deployed system?

Q79. In `f01_generate_key_pairs.py`, `from cryptography.hazmat.primitives.asymmetric import rsa` is imported from the `cryptography` library, while `f06_secure_key_storage.py` uses `from Crypto.PublicKey import RSA` from PyCryptodome. Why do two different RSA libraries coexist in the same project? What compatibility issue could arise if both libraries are used on the same key bytes?

Q80. In `f04_generate_hash.py`, the `CHUNK_SIZE = 8 * 1024 * 1024` constant is set to 8 MB. The module says "8MB chunks balance memory usage and I/O performance." How would you empirically determine the optimal chunk size for the target hardware, and what metrics would you measure?

Q81. In `f02_encrypt_file.py`, the header assembles fields with `struct.pack("Q", original_size)` using little-endian byte order (the "Q" format). Why is little-endian chosen, and what interoperability issue would arise if the `decryptFile()` function (or a third-party implementation) assumed big-endian byte order?

Q82. In `f06_secure_key_storage.py`, both `PKCS1_OAEP` (from PyCryptodome) and `SHA256` are imported for use in RSA key wrapping. The `PKCS1_OAEP.new(public_key, hashAlgo=SHA256)` specifies SHA-256 as the hash algorithm for OAEP. Why is the hash algorithm choice in OAEP significant for security, and what minimum hash output size is recommended?

Q83. In `f05_verify_hash.py`, the `verifyFileIntegrity()` function reads the SFFS V3 header but does not skip the provenance token field (32 bytes) before reading the ciphertext. The code reads only `magic(4) + version(1) + IV(12)` then `hash_pre(32)`. Why is the function able to correctly extract `hash_pre` for both V2 and V3 files given that `hash_pre` comes before the version-specific fields?

Q84. In `f03_decrypt_file.py`, after decryption, the function writes the plaintext to `output_path.write_bytes(decrypted)`. The variable `decrypted` is a `bytes` object. What memory security concern does this raise, and how does this differ from the approach taken in `f06_secure_key_storage.py` with `bytearray`?

Q85. In `f06_secure_key_storage.py`, `_hmac.new(aes_key, _h.digest(), hashlib.sha256).hexdigest()` is used to create the `bound_file_mac`. The `_hmac` module is imported as `import hmac as _hmac`. Why is the module imported with an alias (`_hmac`), and what naming conflict would occur without the alias?

Q86. In `f02_encrypt_file.py`, the `output_path` defaults to `input_path.with_suffix(".sffs")`. This means encrypting `document.pdf` produces `document.sffs` in the same directory. What is the risk if the user then accidentally deletes the original `document.pdf` before verifying that decryption works correctly?

Q87. In `f06_secure_key_storage.py`, the keystore JSON is written with `json.dumps(keystore, indent=2)`. The `indent=2` makes the file human-readable. What attack surface does this create compared to compact JSON, and under what conditions could an attacker exploit a readable keystore file?

Q88. In `f03_decrypt_file.py`, the guard `if len(ciphertext) < 16` checks that there are at least 16 bytes of ciphertext. Why is 16 bytes the minimum: what does it correspond to, and what error would occur without this check if the file were truncated?

Q89. In `f01_generate_key_pairs.py`, the module uses `from cryptography.hazmat.primitives.serialization import (PrivateFormat, NoEncryption, PublicFormat)`. The `hazmat` prefix stands for "Hazardous Materials." What does this naming convention signal to developers about using these primitives?

Q90. In `f06_secure_key_storage.py`, the `unwrapAESKey()` function first tries to detect a JSON envelope by checking `blob.startswith(b"{")`. If the input is raw RSA-encrypted bytes that happen to start with `{` (ASCII 123), this check could incorrectly try to parse them as JSON. What defense does the code have against this ambiguity, and is it sufficient?

Q91. In `f04_generate_hash.py`, the `generateFileHash()` function always returns `"algorithm": "sha256"` regardless of which hash function was used. Is this accurate in all cases, and what downstream bug could this hardcoded string cause?

Q92. In `f05_verify_hash.py`, the module imports `from f04_generate_hash import generateHash` using a relative module name without a package prefix. What Python path requirements does this impose, and how might this import fail in certain deployment scenarios?

Q93. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function accepts a `kdf` parameter defaulting to `"ARGON2ID"`. A caller could pass `kdf="PBKDF2-SHA256"` to explicitly use the weaker KDF. Should this be protected with access controls or warnings, and what principle from secure API design is relevant here?

Q94. In `f02_encrypt_file.py` and `f03_decrypt_file.py`, the constants `SFFS_MAGIC = b"SFFS"` and `SFFS_VERSION = 0x03` are redefined in each module independently rather than being imported from a shared constants file. What software engineering problem does this duplication create, and what security bug could result if the constants diverge between the two files?

Q95. In `f01_generate_key_pairs.py`, the `generated_at` timestamp is included in the returned dict but is NOT stored inside the public key PEM file or the keystore. Where is this metadata expected to be stored, and what auditing gap exists if it is not persisted?

Q96. In `f06_secure_key_storage.py`, the `wrapAESKey()` function streams the `.sffs` file in 8 MB chunks when computing the `bound_file_mac`. Why must the same streaming approach be used in `unwrapAESKey()` when recomputing the hash for verification, and what would happen if `unwrapAESKey()` used `read_bytes()` on a large file?

Q97. In `f03_decrypt_file.py`, the function takes a keyword-only argument `expected_token: bytes | None = None` (after the `*` in the signature). What Python syntax makes this argument keyword-only, and why is it semantically important to enforce keyword-only usage for a security-sensitive parameter like `expected_token`?

Q98. In `f02_encrypt_file.py`, `secrets.token_bytes(32)` generates the `file_token`. The `secrets` module's documentation guarantees cryptographic randomness. If an attacker can predict the token (e.g., on a system with a compromised RNG), what specific attack does this enable given that the provenance table is the security mechanism?

Q99. In `f06_secure_key_storage.py`, the full module-level import `import hashlib` appears twice: once at the top of the file (line 68) and once again just before `hashlib_sha256_sandwich()` (line 200). What does this duplicate import reveal about the history of the code, and what Python behavior makes this harmless (rather than re-executing the module)?

Q100. In `f06_secure_key_storage.py`, the `ARGON2_TIME_COST = 3`, `ARGON2_MEMORY_COST = 65536`, `ARGON2_PARALLELISM = 4` match the OWASP 2023 recommendations from `f09_authenticate_user.py`. Why is it significant that both Student 1 (key storage) and Student 2 (user authentication) use the same Argon2id parameters, and what consistency risk exists if they are independently tuned in the future?

---

## Student 2 — Security (code2, f07–f12)

Q101. In `f07_create_isolated_sandbox.py`, the `_wipe_stale_sandboxes()` function is called at the start of every `createIsolatedSandbox()` call. What security threat does wiping stale sandboxes prevent, and what is the "stale" detection criterion (how is a sandbox determined to be from a crashed session)?

Q102. In `f07_create_isolated_sandbox.py`, the sandbox directory is created with `exist_ok=False` (line 99). What happens if a `sandbox_<session_id>` directory already exists, and why is it safer to fail with an error rather than silently reusing the existing directory?

Q103. In `f07_create_isolated_sandbox.py`, on Linux the sandbox is created with `os.chmod(sandbox_path, 0o700)`. What does the octal permission `0o700` mean in terms of read/write/execute for owner, group, and others? Why is execute permission included for a directory that contains files?

Q104. In `f07_create_isolated_sandbox.py`, the Windows path uses `icacls` with `/inheritance:r` and `/grant:r`. What does `/inheritance:r` do to the inherited ACL entries, and what security risk exists on Windows if this flag is omitted?

Q105. In `f07_create_isolated_sandbox.py`, after `icacls` runs on Windows, the code calls `isSandboxIntact(sandbox_path)` to verify the ACLs were actually applied. Why is this post-creation verification necessary — what attack or system misconfiguration could cause `icacls` to succeed (return code 0) but leave broad permissions?

Q106. In `f07_create_isolated_sandbox.py`, the `sandbox.lock` file on Linux is created using `os.open()` with `os.O_WRONLY | os.O_CREAT | os.O_TRUNC` and mode `0o600`, while on Windows it is created with `Path.write_text()`. Why does the Linux path use the low-level `os.open()` with an explicit mode, and what security issue would arise from using `Path.write_text()` on Linux?

Q107. In `f07_create_isolated_sandbox.py`, the `createIsolatedSandbox()` creates three subdirectories: `decrypted/`, `temp/`, and `keys_runtime/`. What is the security purpose of having separate subdirectories rather than placing all files in the sandbox root?

Q108. In `f07_create_isolated_sandbox.py`, the `destroySandbox()` function calls `secureWipeDirectory()` before `shutil.rmtree()`. The docstring explicitly states that `shutil.rmtree()` alone is "NOT sufficient for secure deletion." Explain technically why deleting a file without overwriting it first still leaves the data recoverable on many filesystems.

Q109. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` function implements a 3-pass DOD 5220.22-M overwrite (zeros, ones, random). For modern SSDs with wear-leveling firmware, why might even 3-pass overwrite fail to guarantee erasure of sensitive data?

Q110. In `f07_create_isolated_sandbox.py`, the `_write_and_sync()` helper calls `fh.flush()` followed by `os.fsync(fh.fileno())` after each overwrite pass. What is the difference between `flush()` and `fsync()`, and why are both needed when writing security-critical overwrites?

Q111. In `f07_create_isolated_sandbox.py`, the `isSandboxIntact()` function on Linux checks if the permission mode is in `("700", "400", "500")`. Why are `400` and `500` considered acceptable alternatives to `700`, and under what administrative scenario would these stricter modes appear?

Q112. In `f07_create_isolated_sandbox.py`, the `isSandboxIntact()` function on Windows checks for "broad access entries" including `"Everyone"`, `"BUILTIN\\Users"`, and `"NT AUTHORITY\\Authenticated Users"`. Why are these three specific principal names considered threats to sandbox isolation?

Q113. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function raises `TypeError` if `target` is not a `bytearray`. The docstring explains that Python strings are "immutable and interned by the interpreter." What does interning mean in CPython, and give a concrete example of how interning prevents secure erasure of a string containing a password.

Q114. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function performs a final `target[:] = b'\x00' * len(target)` zero-out after all passes complete (line 107). Why is this final zeroing pass performed even though pass 3 already overwrites with random bytes?

Q115. In `f08_secure_memory_wipe.py`, the `wipeString()` function encodes the string to UTF-8, creates a `bytearray`, and calls `secureMemoryWipe()` on the bytearray. The docstring warns this is "best-effort only." What fundamental limitation prevents true erasure of the original Python string object, even after this function completes?

Q116. In `f08_secure_memory_wipe.py`, the docstring explains: "A cold boot attack occurs when an attacker freezes RAM." What is the physical basis for cold boot attacks — why does cooling RAM preserve its contents after power loss — and what does this imply about the minimum viable duration for secure memory wipe operations?

Q117. In `f08_secure_memory_wipe.py`, `os.urandom(len(target))` is used for the random-bytes pass. Why is `os.urandom()` preferred over Python's `random.getrandbytes()` for the security-critical final pass of the DOD wipe standard?

Q118. In `f08_secure_memory_wipe.py`, the `createSecureBuffer(size)` function simply returns `bytearray(size)`. Why is creating a zeroed `bytearray` specifically through this function (rather than just calling `bytearray(size)` inline) considered a best practice from a code-review and security standpoint?

Q119. In `f09_authenticate_user.py`, a `_DUMMY_HASH` is pre-computed at module load time (lines 57–59). Explain the timing-based username enumeration attack this prevents, and calculate approximately how long an attacker could enumerate usernames without this defense if Argon2id takes 100 ms per verification.

Q120. In `f09_authenticate_user.py`, the `_compute_lock_until()` function uses `min(30 * (2 ** (failed_attempts - 1)), 3600)`. Calculate the lockout duration after the 5th, 6th, and 7th consecutive failed attempts, and explain why the lockout is capped at 3600 seconds.

Q121. In `f09_authenticate_user.py`, the `authenticateUser()` function calls `secureMemoryWipe(password)` inside a `finally` block (line 239). Why is `finally` critical here — what specific scenario would cause the password to NOT be wiped if `finally` were replaced with a plain call after `pw.verify()`?

Q122. In `f09_authenticate_user.py`, `registerUser()` accepts `password: bytearray` rather than `password: str`. The caller must pass a mutable bytearray. From the perspective of the function's security contract, what obligation does this API design place on the caller after `registerUser()` returns?

Q123. In `f09_authenticate_user.py`, the `sessions` table stores `expires_at` as an ISO timestamp string. In `validateSession()`, the check `expires_at > now` is a lexicographic string comparison. Under what conditions could lexicographic ISO string comparison fail, and is it reliable for this purpose?

Q124. In `f09_authenticate_user.py`, the `registerUser()` function enforces a password policy: minimum 12 characters, with uppercase, lowercase, digit, and special character. Why is minimum length (12 chars) considered more important than complexity requirements by modern security standards (NIST SP 800-63B)?

Q125. In `f09_authenticate_user.py`, SQLite is chosen for the authentication database over other options. The comment says it is "USB-portable" and "no server needed." What are the security tradeoffs of using a local SQLite file for authentication compared to a remote authentication server?

Q126. In `f09_authenticate_user.py`, on successful authentication, `failed_attempts` is reset to 0 and `locked_until` is set to `NULL`. What security implication does resetting the counter on success have — could an attacker exploit this to brute-force a password without triggering permanent lockout?

Q127. In `f09_authenticate_user.py`, the session token is generated with `secrets.token_urlsafe(32)`. Why is `token_urlsafe` used rather than `token_hex`, and what is the effective entropy in bits of a 32-byte URL-safe token?

Q128. In `f09_authenticate_user.py`, the `authenticateUser()` function uses `conn.execute("BEGIN EXCLUSIVE")` is NOT explicitly used — the session insertion is done after the `UPDATE` with standard `conn.commit()`. What race condition could occur in a multi-process environment where two processes try to authenticate the same user simultaneously?

Q129. In `f10_monitor_process.py`, the `isDebuggerPresent()` function on Linux reads `/proc/self/status` and checks the `TracerPid:` field. What is TracerPid, and under what Linux privilege model can a process trace (ptrace) another process?

Q130. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` caps the process iteration at `MAX_PROCS = 1000` using `itertools.islice()`. The comment says "Legitimate debuggers typically appear early in the list." Is this assumption reliable, and how could an attacker exploit the 1000-process cap to evade detection?

Q131. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` on Windows checks for `["x64dbg.exe", "ollydbg.exe", "windbg.exe", "ida64.exe", "processhacker.exe", "wireshark.exe"]`. What is the limitation of signature-based detection of "suspicious" processes by name, and what simple evasion technique would defeat this list entirely?

Q132. In `f10_monitor_process.py`, the `ProcessMonitor` class inherits from `threading.Thread` and is created with `daemon=True`. What does daemon mode mean for a thread, and what would happen to the monitoring thread if the main SFFS process terminates unexpectedly?

Q133. In `f10_monitor_process.py`, the `ProcessMonitor.run()` loop uses `self._stop_event.wait(self.check_interval)` instead of `time.sleep(self.check_interval)`. What is the advantage of using `threading.Event.wait()` for the sleep in a monitoring thread?

Q134. In `f10_monitor_process.py`, when a threat is detected, `_handleThreat()` calls `self.threat_detected.set()` and `self._stop_event.set()` before invoking the callback. Why is the stop event set before the callback runs, and what could go wrong if the callback raised an unhandled exception?

Q135. In `f10_monitor_process.py`, `checkSuspiciousProcesses()` catches `psutil.NoSuchProcess`, `psutil.AccessDenied`, and `psutil.ZombieProcess` exceptions when iterating. Why is `psutil.AccessDenied` especially common on Windows, and does silently continuing on `AccessDenied` represent a security gap?

Q136. In `f11_write_audit_log.py`, the `AuditLogger` class uses `threading.Lock()` to serialize writes. The lock is acquired in the `log()` method via `with self.lock:`. What specific data corruption scenario would occur without this lock in a multi-threaded application where Student 1, Student 2, and Student 3 modules all call `writeAuditLog()` concurrently?

Q137. In `f11_write_audit_log.py`, the `log()` method uses `BEGIN EXCLUSIVE` transaction for each write. The comment explains this "prevents race condition between concurrent processes reading prev_hash and inserting." Explain the specific TOCTOU (Time-of-Check-Time-of-Use) vulnerability that a non-exclusive transaction would introduce for the hash chain.

Q138. In `f11_write_audit_log.py`, the `_compute_entry_hash()` method computes `SHA-256(timestamp|level|event|module|user_id|metadata_json|prev_hash)` using `|` as a delimiter. What subtle collision attack could be mounted if the hash were computed over concatenated fields WITHOUT delimiters?

Q139. In `f11_write_audit_log.py`, the hash chain starts with `prev_hash = "GENESIS"` for the first entry. How does this GENESIS sentinel enable tamper detection for the very first log entry, and what would happen if an attacker deleted all log entries and started a fresh chain?

Q140. In `f11_write_audit_log.py`, the `_encrypt_field()` method encrypts individual fields with AES-GCM, but the `entry_hash` and `prev_hash` fields are stored in PLAINTEXT (not encrypted). Why must these integrity fields remain in plaintext even though they contain metadata about log entries?

Q141. In `f11_write_audit_log.py`, the `verifyLogIntegrity()` method decrypts fields before recomputing hashes. The comment explains "entry_hash was computed over plaintext, so we must decrypt first." If an attacker has the encryption key, could they forge a log entry that passes integrity verification? Explain your reasoning.

Q142. In `f11_write_audit_log.py`, the `_checkRotation()` method deletes the oldest log entries when count exceeds 10,000. What forensic problem does log rotation create, and what would be a more security-conscious approach to log management?

Q143. In `f11_write_audit_log.py`, the `viewLogs()` method decrypts fields using `_decrypt_field()` but catches `json.JSONDecodeError` and `KeyError` for backward compatibility with "legacy plaintext fields." What security risk is introduced by treating decryption failures as "legacy plaintext" rather than as errors?

Q144. In `f11_write_audit_log.py`, the `AuditLogger.__init__()` calls `_initialize()` which runs `ALTER TABLE audit_log ADD COLUMN prev_hash TEXT` if the column is missing. This is a backward-compatible schema migration. What happens to the `prev_hash` values for all existing rows after this migration, and does this break the hash chain verification?

Q145. In `f11_write_audit_log.py`, the global singleton `_logger_instance` is created lazily by `_getLogger()` with a hardcoded path `"./code2/test_output/audit.db"`. What is the risk of this hardcoded path in production, and how does the production code in `sffs_core.py` avoid this problem?

Q146. In `f12_emergency_lock.py`, the `emergencyLock()` function wraps each step in an independent `try/except` block. Why is it critical that a failure in step 3 (memory wipe) does not prevent execution of step 4 (sandbox destroy) and step 5 (session termination)?

Q147. In `f12_emergency_lock.py`, step 7 calls `sys.exit(1)` with exit code 1 rather than 0. The comment explains "a non-zero code lets callers and monitoring tools distinguish a successful clean exit from an emergency lock trigger." What monitoring infrastructure would use this exit code, and how does using `sys.exit()` rather than `raise SystemExit()` help testing?

Q148. In `f12_emergency_lock.py`, the `EMERGENCY_ACTIVE = False` flag is a module-level global variable. What threading issue exists with reading and setting this flag without a lock, and why might this not matter in the emergency lock context?

Q149. In `f12_emergency_lock.py`, the audit log write (step 6) happens AFTER the sandbox destruction (step 4) and session termination (step 5). Why is this ordering important, and what information does the audit log record that could not be recorded if logging happened first?

Q150. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` function uses polling with `check_interval = 0.5` seconds rather than kernel filesystem events (inotify on Linux). What is the maximum theoretical latency between USB removal and lock trigger with this approach, and when would this latency be unacceptable?

Q151. In `f12_emergency_lock.py`, the `setupIdleTimeout()` function uses a `global last_activity` variable updated by `resetIdleTimer()`. What is the threading safety of this approach — could a race condition cause the idle timer to fire even though the user was recently active?

Q152. In `f12_emergency_lock.py`, the `usbMonitor()` inner function in `setupUSBRemovalDetection()` checks `if not usb_root.exists()`. What false-positive scenario could trigger this condition on a network drive or a slow filesystem, causing an erroneous emergency lock?

Q153. In `f07_create_isolated_sandbox.py`, the `secureWipeFile()` function does nothing if the file does not exist (`if not file_path.exists()`). What TOCTOU (time-of-check time-of-use) race condition exists between the existence check and the subsequent `stat()` call, and why is this acceptable in this context?

Q154. In `f09_authenticate_user.py`, the `initAuthDatabase()` function uses `CREATE TABLE IF NOT EXISTS`. What happens if the database file already exists with an incompatible schema (e.g., missing columns), and how would this affect the authentication system at runtime?

Q155. In `f10_monitor_process.py`, on Windows, `kernel32 = ctypes.windll.kernel32` is executed at import time (line 35). What happens when this module is imported on Linux, and why is the conditional `if platform.system() == "Windows":` guard around the `kernel32` assignment important?

Q156. In `f11_write_audit_log.py`, the `log()` method has a retry loop that retries `BEGIN EXCLUSIVE` up to 3 times with linear back-off (0.1s, 0.2s). What scenario causes `sqlite3.OperationalError` during `BEGIN EXCLUSIVE`, and why is 3 retries sufficient for a USB-portable single-user application?

Q157. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` function calls itself recursively for subdirectories (`secureWipeDirectory(dir_path)`). What risk of unbounded recursion exists, and how deep could the sandbox directory tree legitimately grow?

Q158. In `f12_emergency_lock.py`, the five trigger types are: `USB_REMOVED`, `DEBUGGER_DETECTED`, `TIMEOUT`, `MANUAL`, `MAX_FAILURES`. For which of these triggers should the audit log entry be written before `sys.exit(1)` is called, and for which might a post-exit log write be too late?

Q159. In `f09_authenticate_user.py`, the `PasswordHasher` is instantiated with `time_cost=3, memory_cost=65536, parallelism=4` but without specifying `hash_len`. What is the default `hash_len` for the argon2-cffi `PasswordHasher`, and does omitting it affect security compared to explicitly specifying 32 bytes?

Q160. In `f10_monitor_process.py`, the `ProcessMonitor.stop()` method only sets `_stop_event` without waiting for the thread to terminate (`join()`). What happens if code calls `stop()` and then immediately checks `threat_detected` — could a race condition produce a false negative?

Q161. In `f07_create_isolated_sandbox.py`, the function `_wipe_stale_sandboxes()` silently ignores all exceptions with `except Exception: pass` in the per-sandbox cleanup. What forensic information is lost by swallowing these exceptions, and how should this be improved in production code?

Q162. In `f09_authenticate_user.py`, the `terminateSession()` function deletes the session row from the database. What happens if `terminateSession()` is called with a `session_token` that does not exist (e.g., already expired), and is this behavior safe?

Q163. In `f11_write_audit_log.py`, the `AuditLogger` constructor accepts an optional `encryption_key: bytes = None`. When `None` is passed, log fields are stored in plaintext. What is the minimum viable key management scheme for production to ensure the audit log encryption key is not the same as the AES key used for file encryption?

Q164. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function operates on a `bytearray` in-place but does not return a new object — the caller's reference is modified. What Python memory model property makes this in-place modification work correctly when the `bytearray` is passed by reference?

Q165. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` returns a daemon thread. After `emergencyLock()` calls `sys.exit(1)`, what happens to the monitoring daemon thread, and why is it safe to exit without explicitly stopping the thread first?

Q166. In `f09_authenticate_user.py`, the `registerUser()` function returns `{"user_id": None, "status": "error", "message": "Username already exists"}` on duplicate username. Should the error message reveal whether the username exists? What user enumeration attack does this enable, and how would you redesign this response?

Q167. In `f07_create_isolated_sandbox.py`, `uuid.uuid4()` is used to generate the `session_id` when none is provided. UUID4 is randomly generated. How many bits of entropy does UUID4 provide, and is this sufficient to prevent session ID collisions between simultaneous sessions?

Q168. In `f10_monitor_process.py`, the Linux `checkSuspiciousProcesses()` list includes `"gdb"`, `"strace"`, `"ltrace"`, `"radare2"`, `"frida"`, `"valgrind"`. Which of these tools would appear as a child process of SFFS (and thus be most reliably detected), versus appearing as a separate process that attaches to SFFS?

Q169. In `f11_write_audit_log.py`, the `viewLogs()` method queries with `ORDER BY log_id DESC` to return newest-first. What happens to the hash chain verification if `log_id` values are not monotonically increasing (e.g., due to log rotation deleting middle entries followed by new insertions)?

Q170. In `f07_create_isolated_sandbox.py`, the `secureWipeDirectory()` uses `os.walk(directory)` with default `topdown=True` for the first pass (files) and `topdown=False` for the second pass (directories). Why must the directory removal pass use `topdown=False`?

Q171. In `f12_emergency_lock.py`, step 2 in the `emergencyLock()` function is documented as "Close all open file handles (best-effort)" but the comment says "Python does not offer a safe 'close all process handles' primitive." What operating system facilities could be used instead, and does the lack of handle closure create a specific data leak risk?

Q172. In `f09_authenticate_user.py`, the `PasswordHasher` object `pw` is created fresh for each `authenticateUser()` call (line 185). What is the performance impact of re-instantiating `PasswordHasher` per call versus creating it once at module load time?

Q173. In `f07_create_isolated_sandbox.py`, `subprocess.run(['icacls', ...], check=True, capture_output=True, stdin=subprocess.DEVNULL)` is used with `stdin=subprocess.DEVNULL`. Why is it important to redirect stdin to DEVNULL when running a security-critical subprocess?

Q174. In `f11_write_audit_log.py`, the `_encrypt_field()` method generates a fresh 12-byte IV for every field encrypted in every log entry. In a system writing 10,000 log entries with 4 encrypted fields each, what is the total number of GCM IV values used, and how does this compare to the GCM IV birthday bound?

Q175. In `f08_secure_memory_wipe.py`, after `secureMemoryWipe()` returns, the bytearray still exists in memory (filled with zeros). What additional step must the caller take to fully remove the reference from scope, and does CPython's reference counting guarantee immediate deallocation?

Q176. In `f09_authenticate_user.py`, the `sessions` table has no index on `session_token`. In `validateSession()`, the query `SELECT user_id, expires_at FROM sessions WHERE session_token = ?` performs a full table scan. At what session table size would this become a performance problem, and should `session_token` be indexed?

Q177. In `f12_emergency_lock.py`, `last_activity = time.time()` is a module-level global. If `f12_emergency_lock` is imported by multiple modules (e.g., by `sffs_core.py`), do they share the same `last_activity` value, or does each import get its own copy? How does Python's import system handle this?

Q178. In `f10_monitor_process.py`, on Windows, `kernel32.IsDebuggerPresent()` is a well-known anti-debugging technique that advanced debuggers can bypass by patching the PEB (Process Environment Block) flag. What does this imply about the reliability of `isDebuggerPresent()` as a security control?

Q179. In `f07_create_isolated_sandbox.py`, `shutil.rmtree(sandbox_path, ignore_errors=True)` is called after `secureWipeDirectory()`. Why might `shutil.rmtree()` fail even after the secure wipe, and what cleanup state remains if it does fail?

Q180. In `f11_write_audit_log.py`, the module level has a `_logger_instance = None` singleton. If `writeAuditLog()` is called from a `multiprocessing` worker process (not a thread), each worker process gets its own copy of `_logger_instance`. What database corruption could result from multiple processes writing to the same SQLite file without coordination?

Q181. In `f09_authenticate_user.py`, `password_str = password.decode('utf-8')` is called in `registerUser()` before hashing. What error occurs if the bytearray contains non-UTF-8 bytes (e.g., from a binary paste), and how should the function handle this gracefully?

Q182. In `f07_create_isolated_sandbox.py`, the `createIsolatedSandbox()` returns a dict containing the full `sandbox_path`, `decrypted_dir`, `temp_dir`, and `keys_runtime_dir`. If this dict is logged to the audit log, what information leakage risk arises?

Q183. In `f10_monitor_process.py`, the `ProcessMonitor` thread runs as a daemon but `_handleThreat()` invokes `self.on_threat_detected` callback. If the callback blocks indefinitely (e.g., waiting for a GUI event), what happens to the threat response system?

Q184. In `f09_authenticate_user.py`, the `initAuthDatabase()` function connects to the database and calls `conn.commit()` but does not verify that the WAL (Write-Ahead Logging) mode is appropriate for concurrent access. What SQLite journal mode would be better for a multi-reader scenario, and how would you enable it?

Q185. In `f12_emergency_lock.py`, `destroySandbox(sandbox_path)` is called in step 4. If the sandbox path no longer exists (e.g., it was already cleaned up by a previous emergency lock call), what happens in `destroySandbox()`, and is the error handled gracefully?

Q186. In `f11_write_audit_log.py`, each encrypted field produces a JSON blob with `iv`, `ct`, and `tag`. The entire JSON blob is stored as a single SQLite TEXT column. What is the storage overhead per log entry when all four encrypted fields (`event`, `module`, `user_id`, `metadata`) are encrypted compared to plaintext storage?

Q187. In `f09_authenticate_user.py`, the password policy check (`len(password_str) < 12`, uppercase/lowercase/digit/special checks) is performed BEFORE hashing. What is the security implication of a policy check that leaks length information through timing (e.g., the check for a 1-character password is faster than for an 11-character password)?

Q188. In `f07_create_isolated_sandbox.py`, `_wipe_stale_sandboxes()` uses `cutoff = 24 * 3600` seconds (24 hours) as the staleness threshold. Is 24 hours an appropriate threshold for a USB-portable security application? What threat arises from stale sandboxes that are only 1 hour old?

Q189. In `f10_monitor_process.py`, the `checkSuspiciousProcesses()` function checks processes by name and also checks the full executable path (`proc.exe()`) on Windows. What privilege is required to call `proc.exe()` on another user's process, and what exception is caught when this fails?

Q190. In `f11_write_audit_log.py`, the `AuditLogger.log()` method returns `{"log_id": None, "timestamp": ..., "status": "error", "error": str(e)}` on failure rather than raising an exception. What is the security implication of silently swallowing logging errors — which categories of security events could go unrecorded?

Q191. In `f09_authenticate_user.py`, `cursor.execute("SELECT user_id, password_hash, failed_attempts, locked_until FROM users WHERE username = ?", (username,))` uses parameterized queries. Why are parameterized queries important here, and what SQL injection payload would succeed against a naive string-formatted query?

Q192. In `f12_emergency_lock.py`, when the `TIMEOUT` trigger fires, the module docstring says it is "graceful, can be resumed with re-authentication." But `emergencyLock()` calls `sys.exit(1)` for all trigger types. Is the "resumable" claim accurate, and what would need to change to make TIMEOUT truly resumable?

Q193. In `f08_secure_memory_wipe.py`, the `secureMemoryWipe()` function returns a dict with `passes_completed` and `bytes_wiped`. What information should the caller use this return value for, and what is the risk of ignoring the return value?

Q194. In `f10_monitor_process.py`, `psutil.process_iter(["name", "exe"])` is called with attribute filters. Why is filtering attributes important for performance, and what would happen if `process_iter()` were called without any filters on a Windows system with thousands of processes?

Q195. In `f07_create_isolated_sandbox.py`, `secureWipeDirectory()` recursively calls itself for subdirectories. Given the sandbox structure (`decrypted/`, `temp/`, `keys_runtime/`), trace through the full recursion order that occurs when `destroySandbox()` is called on a sandbox containing files in each subdirectory.

Q196. In `f09_authenticate_user.py`, the `_DUMMY_HASH` is computed once at import time. If the module is imported in a subprocess worker (e.g., `isolated_worker.py`), the Argon2 hash is recomputed on every worker spawn. What is the performance impact of this, and how could it be optimized?

Q197. In `f11_write_audit_log.py`, the `verifyLogIntegrity()` function checks both hash correctness AND chain linkage (`chain_ok = (prev_hash or "GENESIS") == expected_prev_hash`). Why is checking both conditions necessary — what specific tampering would pass the hash check but fail the chain check?

Q198. In `f12_emergency_lock.py`, the `setupUSBRemovalDetection()` creates a daemon thread with `thread = threading.Thread(target=usbMonitor, daemon=True)`. If the main process calls `emergencyLock()` due to `TIMEOUT` and then `sys.exit(1)`, does the USB monitor thread cleanly stop? What race condition exists between the thread's final check and the process exit?

Q199. In `f07_create_isolated_sandbox.py`, the Windows `icacls` command grants permissions with `(OI)(CI)F` (Object Inherit, Container Inherit, Full Control). What do OI and CI mean in terms of how permissions are inherited by files and subdirectories created inside the sandbox after it is set up?

Q200. In `f09_authenticate_user.py`, the `authenticateUser()` function checks `if locked_until and locked_until > now` using ISO string comparison. What happens if `locked_until` is stored in a format that is NOT ISO 8601 (e.g., due to locale settings affecting `datetime.now().isoformat()`), and how would you make this comparison timezone-aware and format-agnostic?

---

## Student 3 — UI / Cloud (code3, f13–f18)

Q201. In `f13_init_drive_detection.py`, the `initDriveDetection()` function uses `sys.argv[0]` to resolve the application directory. Why is `sys.argv[0]` preferred over `__file__` for determining the USB root, and what edge case arises when the application is run as a frozen executable (e.g., PyInstaller)?

Q202. In `f13_init_drive_detection.py`, the `_linux_mount_root()` function iterates over `psutil.disk_partitions(all=False)` and returns the mount point with the longest prefix match for the given path. Why is the "longest prefix match" strategy needed rather than just finding any partition that matches?

Q203. In `f13_init_drive_detection.py`, when `is_removable` is `False`, the function issues a `UserWarning` and falls back to the repository root rather than the OS volume root. What production misconfiguration could silently cause `sffs_data/` to be created on the host hard drive instead of the USB stick?

Q204. In `f13_init_drive_detection.py`, the `getAvailableSpace()` function uses `psutil.disk_usage(str(path))`. Why must the path be converted to a string (`str(path)`) rather than passed as a `Path` object, and what does `psutil.disk_usage()` return that cannot be inferred from the `Path.stat()` method alone?

Q205. In `f13_init_drive_detection.py`, the `initDriveDetection()` function creates six subdirectories (`data_dir`, `keys_dir`, `sandbox_dir`, `logs_dir`, `config_dir`, `backups_dir`) using `mkdir(parents=True, exist_ok=True)`. Why does creating these directories at startup prevent race conditions in subsequent modules that assume their existence?

Q206. In `f13_init_drive_detection.py`, the `monitorUSBPresence()` function polls `usb_root.exists()` every 0.5 seconds. How does this polling-based approach compare to kernel event–based monitoring (e.g., using `pyudev` on Linux or `ReadDirectoryChangesW` on Windows) in terms of latency, reliability, and CPU usage?

Q207. In `f13_init_drive_detection.py`, the daemon thread in `monitorUSBPresence()` is named `"SFFS-USBWatch"`. Why is naming threads in Python important for debugging, and what tools would you use to inspect running thread names in a crashed Python application?

Q208. In `f13_init_drive_detection.py`, the `_partition_for_path()` function returns `(device, is_removable, opts)`. On Linux, `is_removable` is determined by whether `"removable"` appears in partition opts. How reliable is this approach on Linux where the `opts` field may not consistently report removability across different kernel versions and USB controllers?

Q209. In `f14_ui_dashboard.py`, the `apply_sffs_theme()` function applies a dark stylesheet globally to the `QApplication`. Why is a dark theme specifically named in the docstring as "high-contrast," and what accessibility concern does this raise for users with certain visual impairments?

Q210. In `f14_ui_dashboard.py`, the `DragDropZone` class emits `file_dropped = pyqtSignal(str)` when a file is dropped. The signal payload is a `str` path. What security check is missing before emitting the signal — what malicious input could an attacker provide by constructing a specially crafted file URL?

Q211. In `f14_ui_dashboard.py`, the `DragDropZone.dropEvent()` method calls `urls[0].toLocalFile()` and emits only the first URL. What happens if a user drags multiple files onto the drop zone, and is this single-file constraint clearly communicated to the user?

Q212. In `f14_ui_dashboard.py`, the `SFSSDashboard.__init__()` includes a `hint` label that says "AES file keys mix OS randomness with your mouse movement." This label is only shown `if core is not None`. What is the meaning of `core` being `None` in the dashboard context, and when does this condition occur?

Q213. In `f14_ui_dashboard.py`, `self._lock_btn.clicked.connect(on_logout)` and `self._out_btn.clicked.connect(on_logout)` both connect to the same callback. What is the difference between "End session" and "Logout" from a security standpoint, and should these buttons trigger different behaviors?

Q214. In `f14_ui_dashboard.py`, the `_on_cloud_backup()` method calls `self._core.backupKeys()` and checks `result.get("status")`. If `status == "not_authenticated"`, a `QMessageBox.question()` dialog is shown. Why is it important that this dialog blocks the UI thread, and what could go wrong if the authentication flow ran in the background thread?

Q215. In `f14_ui_dashboard.py`, the `_run_google_auth()` method defines an inner `_AuthWorker(QThread)` class and stores it as `self._auth_worker`. Why must the worker be stored as an instance attribute rather than a local variable, and what would happen if it were a local variable?

Q216. In `f14_ui_dashboard.py`, the Google auth worker calls `self._auth_worker.terminate()` when the progress dialog is cancelled. What does `QThread.terminate()` do, and why is using `terminate()` considered unsafe for threads that hold locks or open file handles?

Q217. In `f14_ui_dashboard.py`, `uiDashboard()` uses `QApplication.instance() or QApplication(sys.argv)` to reuse an existing QApplication if one exists. Why can only one `QApplication` instance exist per process, and what would happen if a second `QApplication` were created?

Q218. In `f14_ui_dashboard.py`, the `showSecurityAlert()` method changes the color of `self._sec` label to red (`#f28b82`) for CRITICAL alerts and yellow (`#fdd663`) for others. How are these color alerts communicated to screen reader software for visually impaired users?

Q219. In `f14_ui_dashboard.py`, the `refreshLogs()` method displays only the last 5 log entries: `log_entries[-5:]`. What information could be lost if a burst of security events exceeds 5 entries in one refresh cycle?

Q220. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` uses a `QFileSystemModel` with `setReadOnly(True)`. Despite this setting, the context menu created in `_ctx_menu()` includes "Encrypt", "Decrypt", and "Delete" actions. What is the discrepancy between the model's read-only setting and these context menu actions?

Q221. In `f15_file_manager_explorer.py`, the docstring states "A host `QFileDialog` leaks paths to OS MRU databases and thumbnail caches." Explain concretely what an OS MRU (Most Recently Used) database is and how an adversary with physical access to the host computer could exploit it after a user browsed files with the host file dialog.

Q222. In `f15_file_manager_explorer.py`, the `FileManagerExplorer._on_double_click()` emits `sffs_file_selected` for `.sffs` files and `plain_file_selected` for others. The `_status` label updates with the file size. Why is displaying the file size of an `.sffs` file potentially useful to an attacker who cannot read its contents?

Q223. In `f15_file_manager_explorer.py`, the `QFileSystemModel` is set with `setNameFilters()` only when `allowed_extensions` does not contain `"*"`. What happens to the file listing if `allowed_extensions = ["*"]` is passed explicitly versus passing `None`?

Q224. In `f15_file_manager_explorer.py`, hiding columns 1–3 (size, type, date modified) with `self._tree.hideColumn(col)` reduces information leakage in the tree view. Why is the date-modified column specifically sensitive in a security-focused file browser?

Q225. In `f15_file_manager_explorer.py`, the `_ctx_menu()` method creates a `QMenu` with "Encrypt", "Decrypt", "Delete" labels but does not connect any of these actions to callbacks (`menu.addAction("Encrypt")` without a slot). What is the design intent here, and what risk does a partially implemented context menu create in a security application?

Q226. In `f16_cloud_sync.py`, the OAuth scope is `"https://www.googleapis.com/auth/drive.file"`. What does the `drive.file` scope restrict Google Drive access to, and why is it chosen over the broader `drive` scope?

Q227. In `f16_cloud_sync.py`, the `_BUNDLED_SECRET` path points to `code3/google_client_secret.json`. The docstring explains that a "Desktop-app client_secret is intentionally semi-public (Google's own guidance for installed-application OAuth)." Why does Google consider the client secret of an installed/desktop application to be semi-public, and what is the actual security boundary in OAuth 2.0 for installed apps?

Q228. In `f16_cloud_sync.py`, the `_assert_keystore_encrypted()` function checks for required fields `{"kdf", "encrypted_private_key", "auth_tag", "iv", "salt"}` before allowing upload. Why is this pre-upload check critical — what specific secret would be exposed if a raw (unencrypted) private key file were uploaded to Google Drive?

Q229. In `f16_cloud_sync.py`, the `cloudSync()` function attempts to refresh an expired OAuth token with `creds.refresh(Request())` and re-saves the updated token to `google_token.json`. What happens if the refresh token itself has expired (e.g., the user hasn't used SFFS for 6 months), and how does the code handle this case?

Q230. In `f16_cloud_sync.py`, the `authenticateGoogleDrive()` function calls `flow.run_local_server(port=0)`. What does `port=0` specify, and what security benefit does using a random ephemeral port have compared to a fixed port for the OAuth redirect server?

Q231. In `f16_cloud_sync.py`, the `cloudSync()` function returns structured error dicts (e.g., `{"status": "offline", "message": "..."}`) instead of raising exceptions. What is the design rationale for this approach, and how does this affect the caller's ability to distinguish between network errors, authentication errors, and programming errors?

Q232. In `f16_cloud_sync.py`, the `cloudSync("upload")` action prefixes the Drive filename with `sffs_`: `remote_name = f"sffs_{lp.name}"`. What naming conflict could arise if a user has two keystore files with different key IDs but the same base name (which should not happen given key_id uniqueness), and how does the SFFS_Backup folder isolation in Google Drive mitigate this?

Q233. In `f16_cloud_sync.py`, `MediaFileUpload(str(lp), resumable=True)` is used for uploads. Why is `resumable=True` specified for keystore uploads, and what is the typical file size of a keystore JSON that makes resumability relevant or irrelevant?

Q234. In `f16_cloud_sync.py`, the `cloudSync("download")` action uses `MediaIoBaseDownload` and loops with `while not done: _, done = downloader.next_chunk()`. What memory management concern exists when downloading a very large file into a `BytesIO` buffer, and how does this relate to the 2 GB limit in `f03_decrypt_file.py`?

Q235. In `f16_cloud_sync.py`, the `_GOOGLE_OK = False` flag is set when Google libraries are not installed, and all entry points return structured dicts instead of raising `ImportError`. What principle of defensive programming does this implement, and how does it enable SFFS to function without network connectivity?

Q236. In `f17_config_loader.py`, the `DEFAULT_CONFIG` dictionary includes `"pbkdf2_iterations": 310000`. If this config value is changed by the user to a lower number (e.g., 100), and `sffs_core.py` uses this value for key derivation, what security impact would reducing iterations have, and does the current code actually use this config value for KDF?

Q237. In `f17_config_loader.py`, the `configLoader()` function writes plaintext config to `sffs_config.json` when `encryption_key=None` and emits a `UserWarning`. In `sffs_core.py`'s `initialize()` method, the config is loaded with `configLoader("load", cfg_dir, encryption_key=None)`. What sensitive information in `DEFAULT_CONFIG` could be exposed by this unencrypted config file?

Q238. In `f17_config_loader.py`, the `_write()` function deletes `sffs_config.json` when an `encryption_key` is provided and `enc_path` is written. Why is it important to delete the plaintext file after switching to encrypted storage, and what data recovery tool could recover the deleted plaintext config?

Q239. In `f17_config_loader.py`, the `configLoader("get")` action calls `configLoader("load", ...)` recursively and looks up a single key. What is the performance implication of this design — how many disk reads occur for a single `get` operation when the config file is encrypted?

Q240. In `f17_config_loader.py`, the `validateConfig()` function checks `auto_lock_timeout_seconds >= 30`. Why is a minimum of 30 seconds enforced, and what security risk arises if a user could set this to 0 (immediate lock on any idle)?

Q241. In `f17_config_loader.py`, the `_encrypt_blob()` and `_decrypt_blob()` helper functions use AES-GCM with a fresh 12-byte IV each time. If the same `encryption_key` is used for both the config file and some other data store, what key reuse risk arises, and how should key separation be enforced?

Q242. In `f17_config_loader.py`, `configLoader("save", ...)` merges new `updates` into the current config via `merged.update(updates)`. What happens if `updates` contains a key that is NOT in `DEFAULT_CONFIG` — is this key preserved or discarded, and is that behavior secure?

Q243. In `f17_config_loader.py`, the `_merge_defaults()` function does `out = dict(DEFAULT_CONFIG); out.update(cfg)`. This means user config values override defaults. What security risk exists if a malicious config file sets `"max_login_attempts": 99999` or `"auto_lock_timeout_seconds": 999999`?

Q244. In `f18_thread_controller.py`, the `WorkerThread` class inherits from `QThread` and runs `task(*args, **kwargs)` in its `run()` method. Why does Qt require that UI widgets only be updated from the main thread, and how do `pyqtSignal`s safely marshal results back to the main thread?

Q245. In `f18_thread_controller.py`, the `WorkerThread` has a `cancel()` method that sets `self._cancelled = True` and an `is_cancelled()` method. However, the `run()` method does not check `_cancelled` at any point. What must the `task` function itself do to support cancellation, and why can't `WorkerThread` cancel the task from outside?

Q246. In `f18_thread_controller.py`, exceptions in `task` are caught and emitted via `self.signals.error.emit(f"{e}\n{traceback.format_exc()}")`. What security concern exists with emitting full tracebacks, and in what contexts might this reveal sensitive path or variable information?

Q247. In `f18_thread_controller.py`, the `WorkerSignals` class is a separate `QObject` rather than embedding signals directly in `WorkerThread`. Why does PyQt6 require signals to be defined in a `QObject` subclass, and what would happen if `pyqtSignal` were defined directly in a non-QObject class?

Q248. In `f18_thread_controller.py`, `threadController()` connects callbacks using Qt's signal/slot mechanism. If `done_callback` raises an unhandled exception, what happens to the main event loop, and is this exception caught anywhere?

Q249. In `f18_thread_controller.py`, the `run_in_thread` decorator returns a `WorkerThread` instance from the wrapped function. The caller receives the worker handle. What is the caller's responsibility for memory management of the returned `WorkerThread` object, and what happens if no reference is kept?

Q250. In `f18_thread_controller.py`, the `threadController()` function starts the thread immediately with `worker.start()` before returning. What race condition exists between `worker.start()` returning and the caller connecting additional signals that were not passed to `threadController()`?

Q251. In `f13_init_drive_detection.py`, the path map dict returned by `initDriveDetection()` is shared across all of `sffs_core.py`'s session. If the USB is physically removed mid-session and `monitorUSBPresence()` triggers, why is `emergencyLock()` the correct response rather than simply updating the path map to point to a local fallback?

Q252. In `f16_cloud_sync.py`, `loadCredentials()` reads the OAuth token from `config_dir / "google_token.json"`. This token file is stored on the USB drive alongside the encrypted keystores. What is the risk of token leakage if the USB drive is lost, and does the `drive.file` scope limit the damage?

Q253. In `f14_ui_dashboard.py`, the `SFSSDashboard` widget includes `_sandbox_list = QListWidget()` that shows decrypted file paths from `self._core.list_sandbox_files()`. What operational security risk is created by displaying decrypted file names in a visible GUI list?

Q254. In `f15_file_manager_explorer.py`, `QFileSystemModel.setReadOnly(True)` is set, but the file manager still allows double-clicking to emit signals. Why does `setReadOnly` not prevent file-system operations initiated through signal handlers connected to `sffs_file_selected` and `plain_file_selected`?

Q255. In `f16_cloud_sync.py`, when uploading, the file is read by Google's `MediaFileUpload` directly from disk. If the keystore file is being written by `secureKeyStorage()` concurrently on another thread, what race condition exists, and how should file locking be added?

Q256. In `f17_config_loader.py`, the `configLoader("reset")` action writes `DEFAULT_CONFIG` and ignores any existing config. What operational security incident could result if a user accidentally calls `reset` — what configuration values would be lost and what security settings would revert to defaults?

Q257. In `f14_ui_dashboard.py`, the `_open_sandbox_item()` method calls `show_sandbox_file_viewer(self, Path(item.text()))`. The `item.text()` is the string path stored in the `QListWidgetItem`. What trust assumption is made about the content of list items, and could a malicious process inject a path into the sandbox list?

Q258. In `f18_thread_controller.py`, the `WorkerThread.run()` emits `signals.result.emit(out)` if no exception occurs, and `signals.finished.emit()` in the `finally` block. What is the guaranteed order of these two signal emissions, and can connected slots rely on `result` always arriving before `finished`?

Q259. In `f16_cloud_sync.py`, the `cloudSync("delete")` action calls `service.files().delete(fileId=file_id).execute()` with no confirmation step. What happens to the deleted file in Google Drive (is it permanently deleted or moved to trash), and what is the implication for key recovery after accidental deletion?

Q260. In `f13_init_drive_detection.py`, all six standard directories are created with `mkdir(parents=True, exist_ok=True)` but without setting restrictive permissions (no `chmod`). Contrast this with `createIsolatedSandbox()` in `f07_create_isolated_sandbox.py` which explicitly calls `os.chmod(sandbox_path, 0o700)`. Why does `initDriveDetection()` not set restrictive permissions, and is this a security gap?

Q261. In `f14_ui_dashboard.py`, the `SFSSDashboard` receives `session_token`, `config`, and `paths` in its constructor. The `session_token` is stored as `self._session`. What risk exists if this session token is inadvertently serialized (e.g., via Python's `pickle` or logged to disk) and how should it be handled at logout?

Q262. In `f15_file_manager_explorer.py`, `QFileSystemModel` is initialized with the USB root path as the root. The model's `setRootPath()` call initiates a file-system watcher. On Linux, `QFileSystemModel` uses `inotify` to watch for changes. What resource limit (inotify watches) could be exhausted on a USB drive with thousands of files, and what would happen to the file explorer?

Q263. In `f16_cloud_sync.py`, the `BACKUP_FOLDER_NAME = "SFFS_Backup"` is a fixed, predictable folder name in the user's Google Drive. What information disclosure risk arises from using a fixed, predictable folder name, and how could it be made less guessable?

Q264. In `f17_config_loader.py`, the `configLoader()` function's inner `_read_current()` tries the encrypted path first and falls back to the plaintext path. What happens if both `sffs_config.enc` and `sffs_config.json` exist simultaneously — which one is used, and could this lead to inconsistent state?

Q265. In `f18_thread_controller.py`, the `run_in_thread` decorator can be used without parentheses (`@run_in_thread`) or with keyword arguments (`@run_in_thread(kwargs={"key": "value"})`). Trace through the decorator logic to explain how `fn is not None` handles both usage patterns.

Q266. In `f14_ui_dashboard.py`, the `updateProgress()` method makes `self._bar` visible and sets its value. What PyQt6 threading rule does this violate if `updateProgress()` is called directly from a `WorkerThread`, and what is the correct way to update the progress bar from a background thread?

Q267. In `f13_init_drive_detection.py`, `_windows_volume_root()` uses `path.anchor` (e.g., `"D:\\"`), while `_linux_mount_root()` uses `psutil.disk_partitions()`. Why are different approaches needed for the two platforms, and what would `path.anchor` return on Linux for a path like `/media/user/USB`?

Q268. In `f16_cloud_sync.py`, the `loadCredentials()` function returns `None` if the token file cannot be parsed (catches all `Exception`). What specific exceptions should be caught here rather than `Exception`, and what is the risk of catching too broadly?

Q269. In `f17_config_loader.py`, the `DEFAULT_CONFIG` includes `"google_oauth_token_path": None`. In production, this field would point to the OAuth token file. If this path is stored in the unencrypted `sffs_config.json` on the USB drive, what information could an attacker infer from it?

Q270. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` uses a `QSplitter` with a tree view on the left and a "list" view (actually another `QTreeView`) on the right. Why is a second `QTreeView` used as a list view instead of `QListView`, and what display inconsistency does this create?

Q271. In `f14_ui_dashboard.py`, the `SFSSDashboard._pick_sffs_to_view()` calls `QFileDialog.getOpenFileName(self, "Choose .sffs", "", "SFFS (*.sffs)")`. This uses the host OS file dialog. The `f15_file_manager_explorer.py` docstring specifically warns against using host `QFileDialog` because it "leaks paths to OS MRU databases." Why does `SFSSDashboard` still use a host file dialog for this specific operation?

Q272. In `f18_thread_controller.py`, the `WorkerThread` stores `self.signals = WorkerSignals()`. If two different callers use the same `WorkerThread` instance and both connect to `signals.result`, what happens when the task completes — do both slots receive the signal?

Q273. In `f16_cloud_sync.py`, `service = build("drive", "v3", credentials=creds, static_discovery=False)` is called inside `cloudSync()` on every invocation. What is the performance cost of rebuilding the Google Drive service client on every call, and how could it be optimized?

Q274. In `f17_config_loader.py`, `validateConfig()` checks `config.get("theme") not in ("dark", "light")`. What security concern motivates validating the theme value — could an adversary exploit an unchecked theme string to perform injection in a stylesheet?

Q275. In `f14_ui_dashboard.py`, the `SFSSDashboard` layout uses `QSplitter(Qt.Orientation.Horizontal)` with `splitter.setSizes([520, 380])`. What happens to these sizes when the window is resized by the user, and does Qt persist the splitter position between sessions?

Q276. In `f13_init_drive_detection.py`, `initDriveDetection()` emits a `UserWarning` using `warnings.warn()` when running from a non-removable drive. In a production GUI application, where would this warning be visible, and how should it be surfaced to the user instead?

Q277. In `f18_thread_controller.py`, `WorkerThread.run()` catches `Exception` broadly and emits the traceback string via `signals.error`. What Python exceptions are NOT subclasses of `Exception` (and thus would NOT be caught), and what would happen to the application if such an exception occurred in `task`?

Q278. In `f16_cloud_sync.py`, the OAuth flow `flow.run_local_server(port=0)` opens a browser window for authentication. In a headless server environment where SFFS is running without a display, what would happen when this is called, and how should the code handle this case?

Q279. In `f15_file_manager_explorer.py`, the `FileManagerExplorer` widget accepts `allowed_extensions: list[str] | None`. If `allowed_extensions = [".sffs"]` is passed, `QFileSystemModel.setNameFilters(["*.sffs"])` is set. Does this filter affect the directory tree view or only the file list view? What user confusion could this create?

Q280. In `f17_config_loader.py`, the inner function `_write()` calls `_merge_defaults(cfg)` before writing. This means even `configLoader("reset")` passes through `_merge_defaults`. What invariant does `_merge_defaults` guarantee about the stored config, and why is this important for forward compatibility when new keys are added to `DEFAULT_CONFIG`?

Q281. In `f14_ui_dashboard.py`, the `_on_cloud_backup()` method is connected to the "Cloud backup (optional)" button but only if `core is not None`. What is the behavior if the button is clicked when `core is None` — does Qt prevent the click, silently ignore it, or execute the unconnected handler?

Q282. In `f13_init_drive_detection.py`, `monitorUSBPresence()` calls `callback()` inside a `try/except Exception: pass` block. What happens if the callback raises `SystemExit` (e.g., from `emergencyLock()` calling `sys.exit(1)`), and does `except Exception` catch `SystemExit`?

Q283. In `f16_cloud_sync.py`, the `cloudSync("list")` action calls `_ensure_backup_folder()` which creates the folder if it doesn't exist. What is the side effect of calling `cloudSync("list")` for the first time, and is this an appropriate side effect for a "read-only" list operation?

Q284. In `f18_thread_controller.py`, the `WorkerThread` does not implement `__del__` or any cleanup method. If a `WorkerThread` object is garbage collected while still running, what happens to the underlying OS thread?

Q285. In `f17_config_loader.py`, `configLoader("save")` reads the current config and merges updates into it. If two threads call `configLoader("save")` concurrently with different updates, describe the race condition that could result and what the final state of the config file might be.

Q286. In `f14_ui_dashboard.py`, the status bar at the bottom shows `f"USB free space: ~{free} GB  ·  SFFS v1.0"` using `paths.get("free_space_gb", "?")`. This value is computed once at startup. What happens to the displayed free space after the user encrypts a large file, and why might the displayed value become misleading?

Q287. In `f15_file_manager_explorer.py`, `self._model.setReadOnly(True)` prevents rename/delete through the model. However, the `_ctx_menu()` includes a "Delete" action. If this action were connected to a file deletion handler, what additional checks would be needed to prevent deleting files outside the USB root?

Q288. In `f16_cloud_sync.py`, `_ensure_backup_folder()` queries Google Drive with the GDQL query `f"name='{BACKUP_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"`. Is this query vulnerable to GDQL injection if `BACKUP_FOLDER_NAME` contained single quotes, and why is this or is it not a concern in this code?

Q289. In `f18_thread_controller.py`, `WorkerThread.cancel()` sets `self._cancelled = True` but `run()` never checks it. How would you redesign the `WorkerThread.run()` method to support cooperative cancellation at defined checkpoints, and what Python mechanisms (threading.Event, etc.) would you use?

Q290. In `f13_init_drive_detection.py`, the `initDriveDetection()` function is called at the start of `SFFSCore.initialize()` and its result stored in `self.paths`. If `initDriveDetection()` raises an exception (e.g., `psutil` fails to enumerate partitions), what is the expected behavior of the application startup, and how should this exception be handled?

Q291. In `f14_ui_dashboard.py`, when `DragDropZone._browse_file()` is called, `QFileDialog.getOpenFileName()` is invoked. What OS-level privileges does opening a native file dialog potentially grant, and why is this more permissive than the scoped `FileManagerExplorer` widget?

Q292. In `f17_config_loader.py`, the `configLoader()` function accepts `action: str` but does not validate it against the allowed set before dispatch (`if action == "reset": ... if action == "load": ...`). The function falls through to `raise ValueError(f"Unknown action: {action}")`. What is the idiomatic Python improvement to this dispatch structure?

Q293. In `f16_cloud_sync.py`, the downloaded backup is written to `Path(local_path).write_bytes(fh.getvalue())`. The `fh` is a `BytesIO` buffer holding the entire downloaded file in memory. For keystore zip files (typically small), this is fine. But what if SFFS were modified to back up `.sffs` encrypted files — what memory limit would this impose?

Q294. In `f15_file_manager_explorer.py`, `self._model.setNameFilterDisables(False)` is called when name filters are set. What is the difference between `setNameFilterDisables(True)` and `setNameFilterDisables(False)` in terms of how non-matching files are displayed in the tree view?

Q295. In `f14_ui_dashboard.py`, the `SFSSDashboard` stores `self._core = core` which is an `SFFSCore` instance. If the user opens a second window (multiple `SFSSDashboard` instances) sharing the same `core`, what concurrency issues would arise when both windows trigger encrypt/decrypt operations simultaneously?

Q296. In `f17_config_loader.py`, when `encryption_key` is provided but `enc_path` does not yet exist, `_read_current()` returns `{}` and the config is reconstructed from defaults. On subsequent saves, the encrypted config is written. What is the chicken-and-egg problem with providing the encryption key before the config file exists, and how does SFFS resolve this during first-run initialization?

Q297. In `f13_init_drive_detection.py`, the `drive_label` is obtained from `usb_root.name or str(usb_root)`. On Windows, `Path("D:\\").name` returns `""` (empty string), so `str(usb_root)` is used instead. What is returned for `str(Path("D:\\"))` in Python, and how is this used in the UI?

Q298. In `f18_thread_controller.py`, `WorkerThread.run()` calls `self.signals.finished.emit()` in a `finally` block, guaranteeing it is always emitted. Why is it important for the GUI application (connected via `finished_callback`) to not assume the task succeeded just because `finished` was emitted?

Q299. In `f16_cloud_sync.py`, the `authenticateGoogleDrive()` function writes the OAuth token to `google_token.json` with `token_path.write_text(creds.to_json(), encoding="utf-8")`. The token JSON contains a `refresh_token`. What is a refresh token, why is it more sensitive than an access token, and what file permission should be applied to protect it?

Q300. In `f14_ui_dashboard.py` and `f18_thread_controller.py` together, the pattern of running crypto operations (`encryptFileOperation`, `decryptFileOperation`) in `WorkerThread` and reporting progress via `pyqtSignal(int)` is described. Trace the full signal-slot chain from a user clicking "Encrypt selection" to the progress bar reaching 100%, identifying every class and signal that participates in keeping the UI responsive while cryptography runs in the background.
