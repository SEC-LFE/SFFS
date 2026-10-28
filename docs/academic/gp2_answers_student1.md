# GP2 Exam Answers — Student 1: Cryptography (code1, f01–f06)

---

**Q1. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function raises a `ValueError` if `key_size < 2048`. Explain why 2048 bits is enforced as the minimum and what security level (in equivalent symmetric bits) this provides according to the module's own documentation.**

**Answer:** 2048-bit RSA provides approximately 112 bits of equivalent symmetric security, matching a 112-bit symmetric key. The module docstring states "Current best attacks can only break 1024-bit RSA, making 2048-bit secure for now" and cites NIST's recommendation of at least 2048 bits for new deployments. Accepting smaller keys would expose the system to factoring attacks feasible with modern hardware.

**Reasoning:** The 112-bit symmetric equivalence is stated directly in the module's docstring and matches NIST SP 800-57 key-strength tables.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 75

---

**Q2. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function uses `public_exponent=65537`. Why is 65537 chosen as the RSA public exponent rather than a smaller value like 3? What are the security and performance tradeoffs?**

**Answer:** 65537 (2^16 + 1) is chosen because it is a Fermat prime with only two set bits, making modular exponentiation fast while avoiding the mathematical weaknesses of small exponents like 3. With e=3, certain padding attacks and cube-root attacks on unpadded messages become feasible; 65537 closes those attack vectors while still keeping public-key operations efficient.

**Reasoning:** The low Hamming weight of 65537 keeps encryption fast; its size is large enough to prevent known small-exponent attacks. This is the universal industry standard for RSA public exponents.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 83

---

**Q3. In `f01_generate_key_pairs.py`, the key_id is computed as `hashlib.sha256(public_pem).hexdigest()[:16]`. An earlier version used only 8 hex characters. The comment says the change was made because "at 8 chars the birthday collision probability is ~1/2^32 — borderline." Explain the birthday paradox and why 16 hex chars (64 bits) was chosen instead.**

**Answer:** The birthday paradox states that in a group of N items drawn from a space of size M, collisions become probable when N ≈ √M. For 8 hex chars (32-bit space), a collision becomes likely around √(2^32) ≈ 65,536 keys — plausible for large deployments. Expanding to 16 hex chars (64-bit space) raises the collision threshold to ~2^32 keys, making collisions negligible in practice.

**Reasoning:** The code comment explicitly cites "~1/2^32 — borderline" for 8 chars; doubling to 16 chars squares the collision resistance to 1/2^64.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 101

---

**Q4. In `f01_generate_key_pairs.py`, the private key is exported using `PrivateFormat.TraditionalOpenSSL` with `NoEncryption()`. Why is `NoEncryption()` used here even though the private key is sensitive, and what must the caller do immediately after receiving `private_key_bytes` to ensure security?**

**Answer:** `NoEncryption()` is used because the key is never written to disk here — it is returned as in-memory bytes only. The module docstring explicitly says "We use NoEncryption because we immediately encrypt with PBKDF2 + AES in secureKeyStorage()." The caller must immediately pass `private_key_bytes` to `secureKeyStorage()` and never log, print, or persist it in any other way.

**Reasoning:** Using library-level encryption on top would add a second unnecessary layer; the real protection is the AES-GCM wrap in f06. The security contract is on the caller, not the serialisation format.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 113

---

**Q5. In `f01_generate_key_pairs.py`, the `generateKeyPairs()` function writes the public key to disk but only returns the private key as in-memory bytes. Why is the public key safe to write to disk while the private key is not?**

**Answer:** A public key is mathematically designed to be shared openly — it can only encrypt data or verify signatures, not decrypt them. The private key holds the factored secret that can decrypt all files encrypted under the corresponding public key, so persisting it in plaintext on disk would give any reader of that disk full decryption capability.

**Reasoning:** Asymmetric cryptography's security model explicitly assumes the public key is non-secret; secrecy of the private key is the entire security foundation.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 107

---

**Q6. In `f02_encrypt_file.py`, AES-256-GCM is chosen over AES-256-CBC. List at least two reasons stated in the module's docstring for preferring GCM, and explain what "authenticated encryption" means in practical terms.**

**Answer:** The module docstring states: (1) "GCM provides BOTH confidentiality AND authentication in a single pass," and (2) "CBC mode requires a separate MAC." Authenticated encryption means the cipher simultaneously encrypts the data and computes an authentication tag; any modification of the ciphertext or IV invalidates the tag, so a decryption call will fail before returning any plaintext.

**Reasoning:** In practical terms, authenticated encryption removes an entire class of chosen-ciphertext attacks (e.g., padding oracle) that affect unauthenticated modes like CBC.

**Reference:** `code1/f02_encrypt_file.py` → module docstring ~line 7

---

**Q7. In `f02_encrypt_file.py`, the IV is generated using `secrets.token_bytes(12)` rather than 16 bytes. The comment explains that 12-byte (96-bit) nonces avoid an internal GHASH reduction. Explain what this GHASH reduction is and why the 12-byte IV is the recommended GCM nonce length.**

**Answer:** In GCM, nonces other than 96 bits are processed by hashing them through GHASH to produce a 96-bit counter block, which adds computation overhead and, more importantly, makes the security reduction less tight. NIST SP 800-38D specifies 96-bit (12-byte) nonces as the recommended length because they are used directly as the initial counter block with no reduction, giving the full security proof and optimal performance.

**Reasoning:** The 12-byte path bypasses the GHASH derivation step; any other length triggers it, weakening the provable security bound.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 127

---

**Q8. In `f02_encrypt_file.py`, the `encryptFile()` function requires `aes_key` to be exactly 32 bytes and raises `ValueError` if it is not. What would happen at the cryptographic level if a 16-byte key were silently accepted instead of rejected?**

**Answer:** A 16-byte key selects AES-128 instead of AES-256, reducing the key search space from 2^256 to 2^128. While AES-128 is still computationally secure today, SFFS's security documentation and provenance model assume AES-256 strength; silent key-length downgrade could also violate FIPS-140-2 compliance requirements and could enable brute-force attacks in a post-quantum context.

**Reasoning:** The explicit check enforces the 256-bit security level promised by the design; mismatched key sizes between encryption and decryption would also cause `InvalidTag` errors at decryption.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 102

---

**Q9. In `f02_encrypt_file.py`, the SFFS file format header includes `SFFS_MAGIC = b"SFFS"` and `SFFS_VERSION = 0x03`. What is the purpose of the magic bytes, and how does the version byte (`0x03`) assist the decryption module when supporting multiple format generations?**

**Answer:** The magic bytes `b"SFFS"` act as a file-type signature so the decryption module can reject non-SFFS files immediately with a clear error rather than producing garbage output. The version byte `0x03` allows `decryptFile()` to dispatch to different header-parsing logic — the code in f03 accepts both `0x02` (legacy, no provenance token) and `0x03` (current, includes provenance token in header), enabling backward compatibility without ambiguity.

**Reasoning:** Without magic bytes, the decryptor would silently try to parse arbitrary binary files as SFFS headers, potentially leaking partial data or crashing unpredictably.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 66

---

**Q10. In `f02_encrypt_file.py`, the original file extension is stored inside the encrypted header rather than preserved in the `.sffs` filename. What security goal does this achieve, and what is the maximum allowed extension length and why?**

**Answer:** Storing the extension inside the header (and using only `.sffs` as the visible suffix) hides the file type from directory listings — an attacker who sees the USB drive sees only `.sffs` files with no indication of whether the contents are `.docx`, `.pdf`, `.pem`, or any other sensitive type. The maximum allowed extension length is 32 bytes, enforced by the `ext_len > 32` check, because a `uint8` header field could technically hold up to 255 but real file extensions are always short and a large value signals a malformed or malicious input.

**Reasoning:** Limiting to 32 bytes prevents header bloat and catches corrupt or adversarially crafted inputs early before they consume header space.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 146

---

**Q11. In `f02_encrypt_file.py`, a `file_token` of 32 random bytes is generated and stored in the plaintext header of the `.sffs` file. The docstring states "Security comes from the table (secret), not from hiding the token bytes in the file." Explain this provenance design: how does an attacker fail to bypass it even though they can read the token from the file?**

**Answer:** Reading the token from the header only tells an attacker what the token value is; it does not tell them whether that token is registered in the provenance table (`sffs_data/provenance.json`). During decryption, SFFS looks up `expected_token = table[hash_pre]` and compares it to the file header token. An attacker who creates a forged `.sffs` file cannot guess or forge an entry in the provenance table (which is kept on the SFFS system), so provenance verification will fail even if they can read and copy the token.

**Reasoning:** The security boundary is the secrecy of the provenance table's contents, not the secrecy of the token bytes themselves — a token without a matching table entry is worthless to an attacker.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 117

---

**Q12. In `f02_encrypt_file.py`, the SHA-256 hash of the plaintext is computed BEFORE encryption and stored in the header as `hash_pre`. Why is it important to hash the plaintext before encryption rather than hashing the ciphertext?**

**Answer:** Hashing the plaintext proves the integrity of the original content: after decryption, `hash_post = SHA256(decrypted)` can be compared to `hash_pre` to confirm the plaintext was not modified before or after encryption. Hashing the ciphertext would only verify that the ciphertext bytes were unchanged, which AES-GCM's authentication tag already guarantees — it adds no new information about plaintext integrity.

**Reasoning:** The two-hash design (pre- and post-decryption) provides an independent integrity layer beyond the GCM tag, useful for detecting logic bugs or corruption in the decryption pipeline itself.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 114

---

**Q13. In `f02_encrypt_file.py`, the `AESGCM.encrypt()` call passes `associated_data=None`. In AES-GCM, what is associated data (AAD), and what security property would be gained if the SFFS file header bytes were passed as AAD?**

**Answer:** Associated data (AAD) is plaintext that is authenticated but not encrypted — it is fed into the GCM authentication tag computation alongside the ciphertext. Passing the SFFS file header as AAD would bind the ciphertext to that specific header: any attacker who copied the ciphertext into a different header (different IV, different `hash_pre`, different extension) would invalidate the authentication tag, preventing header-swapping attacks.

**Reasoning:** Without AAD, an attacker can detach a valid ciphertext block and re-embed it in a crafted header — AES-GCM would still authenticate it, but the header metadata would be attacker-controlled.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 136

---

**Q14. In `f02_encrypt_file.py`, the output file is written as `header + ciphertext` in a single `write_bytes()` call. Why is atomic writing of the complete encrypted file important from a security standpoint, compared to writing header and ciphertext in two separate calls?**

**Answer:** Atomic writing ensures that a partial file (header only, or truncated ciphertext) cannot exist on disk — if the write fails or the process crashes, there is no partially-written `.sffs` file that a concurrent reader could interpret as a valid encrypted file. Writing in two separate calls risks leaving a file with valid magic bytes and a header but a truncated or missing ciphertext, which could confuse the decryptor or trigger unexpected code paths.

**Reasoning:** In security-critical code, partial state on disk is as dangerous as incorrect state; a single `write_bytes(header + ciphertext)` either fully succeeds or fails without intermediate visible state.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 182

---

**Q15. In `f03_decrypt_file.py`, the `decryptFile()` function includes a `MAX_FILE_BYTES = 2 * 1024 ** 3` (2 GB) guard. What memory-related risk does this guard prevent, and why does AES-GCM specifically require the entire ciphertext in memory at once?**

**Answer:** Without the guard, an attacker could craft a `.sffs` file whose embedded `original_size` field indicates a multi-terabyte payload, causing `read_bytes()` to allocate RAM until the process is killed or the OS crashes (OOM). AES-GCM requires the entire ciphertext in memory because the authentication tag is computed over all ciphertext bytes; the `cryptography` library's `AESGCM.decrypt()` API does not support streaming decryption — it must process the full buffer to verify the tag before returning any plaintext.

**Reasoning:** GCM is a counter mode cipher combined with GHASH, and the tag verification is a post-processing step over all ciphertext; there is no partial-verification API that would be safe to use incrementally.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 113

---

**Q16. In `f03_decrypt_file.py`, the function accepts both version `0x02` (legacy) and `0x03` (current) SFFS files. What design principle does this represent, and what security risk could arise from indefinitely supporting old format versions?**

**Answer:** This represents the backward-compatibility design principle: existing encrypted files must remain decryptable after a format upgrade. The security risk is that V2 files lack the provenance token field, meaning provenance verification is skipped for them — an attacker could forge a V2 file or downgrade a V3 file to V2 to bypass the provenance check. Indefinitely maintaining V2 support also prevents the team from deprecating weaker security assumptions made at that version.

**Reasoning:** Legacy support always widens the attack surface; the safest approach is to set a migration deadline after which V2 files must be re-encrypted to V3 format.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 141

---

**Q17. In `f03_decrypt_file.py`, the `SecurityError` class is a custom exception rather than using Python's built-in `ValueError`. Why does the code define a custom `SecurityError`, and what does this enable in the calling code that catching `ValueError` would not?**

**Answer:** `SecurityError` is a semantically distinct exception that unambiguously signals a security violation (tampered file, provenance mismatch) rather than a generic invalid-argument error. Calling code can catch `SecurityError` specifically to trigger emergency responses — such as locking the system, writing an audit log, or notifying the user — without accidentally catching unrelated `ValueError` exceptions that arise from programmer mistakes or malformed inputs that should be handled differently.

**Reasoning:** Exception hierarchy design is a security-relevant API decision; conflating security violations with programming errors makes callers more likely to swallow or mishandle them.

**Reference:** `code1/f03_decrypt_file.py` → `SecurityError` ~line 57

---

**Q18. In `f03_decrypt_file.py`, when the GCM auth tag fails, any partial output file is deleted before the `SecurityError` is raised. What attack does this prevent? Give a concrete example of how a partially decrypted file could be exploited.**

**Answer:** Deleting the partial output prevents an attacker from harvesting fragments of decrypted plaintext written before authentication failed. For example, if AES-GCM decrypted in a streaming fashion (it does not in AESGCM, but in a hypothetical design), partial plaintext might appear on disk; an attacker who crafted a specific ciphertext could flip bits to produce controlled bytes in the first N blocks, then cause authentication to fail — leaving a partially decrypted file containing, say, a malicious script that a user might inadvertently open.

**Reasoning:** Even in non-streaming GCM, defense-in-depth dictates cleaning up any output file on error to prevent residual data leakage in edge cases.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 208

---

**Q19. In `f03_decrypt_file.py`, the provenance token check occurs BEFORE the AES key is used. The comment states "Nothing is decrypted until provenance passes." Why is this ordering critical from a security standpoint?**

**Answer:** Checking provenance first ensures that the AES key is never applied to files that do not originate from this SFFS instance. If decryption happened first and provenance was checked afterward, an attacker could present a valid ciphertext (encrypted with a key they stole) without being registered in the provenance table — the decryption would succeed and plaintext would be produced before the provenance failure could delete it. Fail-early ordering minimises the window in which sensitive data exists.

**Reasoning:** Security checks should be ordered so that the most restrictive and cheapest checks run first, before any sensitive computation or data exposure occurs.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 176

---

**Q20. In `f03_decrypt_file.py`, the provenance token comparison uses `hmac.compare_digest(file_token, expected_token)`. Why is `compare_digest` used instead of the `==` operator, and what attack does this constant-time comparison prevent?**

**Answer:** Python's `==` operator returns `False` as soon as the first differing byte is found (short-circuit comparison), so a comparison against a partially-correct token completes faster than one against a completely wrong token. An attacker who can measure response times could exploit this to brute-force the expected token one byte at a time. `hmac.compare_digest` always examines every byte regardless of where the mismatch occurs, making all comparisons take the same time and eliminating the timing side-channel.

**Reasoning:** Timing attacks are especially feasible when the token check is exposed over a network API; even in a local context, the constant-time habit prevents inadvertent future exposure.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 181

---

**Q21. In `f03_decrypt_file.py`, when `UnicodeDecodeError` is raised while reading the original extension from the header, a `ValueError` is raised with the message "SFFS file corrupted." Why might a malformed UTF-8 extension field be a security concern beyond mere file corruption?**

**Answer:** A crafted malformed UTF-8 extension string could be an attempt to exploit a parsing vulnerability — for example, feeding overlong encodings or BOM markers that confuse downstream string handling to produce a different extension value, potentially enabling path traversal or type-confusion attacks. Treating it as a security-relevant failure (rather than silently using a default extension) prevents the file from proceeding further in the decryption pipeline with an attacker-influenced filename.

**Reasoning:** Input validation on file format fields is part of secure parsing; invalid encoding in a security-sensitive field should always be treated as a potential attack signal, not just a benign error.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 162

---

**Q22. In `f03_decrypt_file.py`, the decrypted output is written to `output_dir` which is described as an isolated sandbox directory. Why does the module docstring state it is a "security risk" to decrypt to the host OS disk (`C:` drive, `/home/user`)?**

**Answer:** Decrypting directly to the host disk means sensitive plaintext files land alongside system files, application caches, browser histories, and other OS components. An attacker with OS-level access could exfiltrate the plaintext files, OS temp/thumbnail caches may copy them automatically, and antivirus or file-indexing services may scan and log their contents. The sandbox isolates the decrypted files in a directory with tight access controls that is wiped on session end.

**Reasoning:** The threat model explicitly includes host-OS compromise; the sandbox is the boundary between the trusted SFFS environment and the untrusted host.

**Reference:** `code1/f03_decrypt_file.py` → module docstring ~line 19

---

**Q23. In `f04_generate_hash.py`, the `generateHash()` function supports three algorithms: `sha256`, `sha512`, and `blake2b`. Why is MD5 explicitly not supported, and what makes SHA-1 and MD5 unsuitable for security-critical integrity verification?**

**Answer:** MD5 has known trivial collision attacks — two different files can be crafted to produce the same MD5 hash with modest effort — making it useless for tamper detection. SHA-1 also has demonstrated practical collision attacks (the SHAttered attack in 2017 produced two different PDF files with identical SHA-1 hashes). The module docstring states "MD5 is broken (trivial collisions)" and "SHA-1 is deprecated (practical attacks exist)"; SFFS uses SHA-256 or stronger for FIPS-140-2 compliance.

**Reasoning:** For integrity verification in a security product, a collision in the hash algorithm means an attacker can substitute a malicious file that passes the integrity check.

**Reference:** `code1/f04_generate_hash.py` → module docstring ~line 13

---

**Q24. In `f04_generate_hash.py`, files are processed in `CHUNK_SIZE = 8 * 1024 * 1024` (8 MB) chunks. Why is streaming hashing in chunks necessary for large files, and what would happen if the entire file were loaded into memory at once on a system with limited RAM?**

**Answer:** Loading an entire large file (e.g., a 10 GB video archive) into RAM at once would exhaust available memory, causing the OS to either kill the process (OOM killer on Linux) or cause severe swap thrashing that effectively freezes the system. Streaming in 8 MB chunks keeps memory usage bounded and constant regardless of file size, allowing the hash to be computed on multi-GB files on modest hardware.

**Reasoning:** The module docstring explicitly states "8MB chunks balance memory usage and I/O performance" and "enables hashing multi-GB files on modest hardware."

**Reference:** `code1/f04_generate_hash.py` → `generateHash()` ~line 100

---

**Q25. In `f04_generate_hash.py`, the `generateHash()` function accepts `Union[Path, bytes, str]` as its `target` parameter. What is the purpose of normalizing `str` inputs to `Path` objects (line 65), and why does this improve the function's usability without compromising security?**

**Answer:** Normalising string paths to `Path` objects allows callers to pass file path strings without importing `pathlib.Path` themselves, reducing the API friction. Security is not compromised because the conversion is one-to-one — `Path(str_path)` produces the exact same filesystem path, so there is no risk of silent path reinterpretation or traversal injection beyond what `Path` already handles.

**Reasoning:** The comment in the code says "Normalize str paths to Path objects so callers don't need to import Path"; this is purely ergonomic with no security impact.

**Reference:** `code1/f04_generate_hash.py` → `generateHash()` ~line 64

---

**Q26. In `f04_generate_hash.py`, the BLAKE2b algorithm is offered as an alternative to SHA-256. The docstring states it is "faster than SHA-256 for large files" and "stdlib since Python 3.6 — no external dependency needed." What are the security tradeoffs of using BLAKE2b versus SHA-256 in a FIPS-140-2 compliant environment?**

**Answer:** SHA-256 is FIPS-140-2 approved and is the only hash algorithm accepted by many US government and regulated-industry compliance frameworks; BLAKE2b is not on the FIPS-approved algorithm list. Using BLAKE2b in a FIPS-140-2 environment would cause a compliance failure even though BLAKE2b is considered cryptographically strong. In non-regulated contexts BLAKE2b's performance advantage (faster on 64-bit platforms) is the primary reason to choose it over SHA-256.

**Reasoning:** The module docstring notes SHA-256 is "FIPS-140-2 approved" while BLAKE2b is justified by speed and standard-library availability — the two goals conflict in regulated deployments.

**Reference:** `code1/f04_generate_hash.py` → module docstring ~line 19

---

**Q27. In `f04_generate_hash.py`, the `generateFileHash()` convenience function always uses SHA-256 regardless of which algorithm the user prefers. What consistency issue could arise if `generateFileHash()` is used in one place and `generateHash(path, "blake2b")` in another when comparing hash values?**

**Answer:** SHA-256 and BLAKE2b produce different hash values for the same input, so comparing a SHA-256 digest from `generateFileHash()` to a BLAKE2b digest from `generateHash(..., "blake2b")` will always fail — reporting a false tamper detection. The `generateFileHash()` return dict hardcodes `"algorithm": "sha256"`, so if the calling code trusts that field, it may attempt an algorithm-matched comparison that still fails because the actual comparison bytes differ from the other call's output.

**Reasoning:** Algorithm consistency is critical for hash-based integrity checks; mixing algorithms silently breaks equality comparisons without any exception being raised.

**Reference:** `code1/f04_generate_hash.py` → `generateFileHash()` ~line 129

---

**Q28. In `f05_verify_hash.py`, the `verifyHash()` function returns a truncated version of both hashes in its result dict: `hash_pre[:16] + "..."`. Why are full hash values truncated in the output, and what security risk would returning full hashes pose?**

**Answer:** Returning a full SHA-256 hex digest (64 characters) in the result dict exposes the exact hash value to any code path that logs, serialises, or displays the return value. An attacker who obtains the full `hash_pre` could use it as a lookup key to search for known plaintext files (preimage attacks against known content) or to verify whether a file they have access to matches the protected original. Truncating to 16 characters provides enough information for human diagnostics while preventing full hash leakage.

**Reasoning:** The module docstring describes the truncation as "prevent hash leakage"; even non-secret hashes act as content fingerprints that can reveal file identity.

**Reference:** `code1/f05_verify_hash.py` → `verifyHash()` ~line 83

---

**Q29. In `f05_verify_hash.py`, the `verifyHash()` function returns `alert_level = "CRITICAL_TAMPER_DETECTED"` when hashes don't match. In a real deployed system, what actions should be taken programmatically when this alert level is returned, and what are the forensic implications?**

**Answer:** On `CRITICAL_TAMPER_DETECTED`, the system should: (1) immediately abort any further processing of the file, (2) call `emergencyLock()` to wipe the sandbox and terminate the session, (3) write a forensic audit log entry including the truncated hashes, file path, and timestamp, and (4) alert the user. Forensically, the mismatch means someone modified either the `.sffs` header's `hash_pre` field or the plaintext after decryption; the audit log chain and the GCM tag status together help distinguish header tampering from post-decryption tampering.

**Reasoning:** Tamper detection without automated response is insufficient in a security system; the response must be proportionate to the threat — loss of integrity means the file cannot be trusted.

**Reference:** `code1/f05_verify_hash.py` → `verifyHash()` ~line 76

---

**Q30. In `f05_verify_hash.py`, the `verifyFileIntegrity()` function reads the `hash_pre` from the `.sffs` file header by seeking to byte offset `4 + 1 + 12 = 17`. Why is this calculation fragile with respect to format versioning, and how does this relate to the V3 format adding a variable-length extension field?**

**Answer:** The offset calculation `4+1+12 = 17` assumes the SFFS header layout never changes before `hash_pre`. In fact, `hash_pre` still starts at byte 17 in both V2 and V3 (Magic(4) + Version(1) + IV(12)), so this specific read is correct. However, the function then manually skips `orig_size(8) + ext_len(1) + ext(N)` to reach subsequent fields — if V3 added any new fixed-width field before `hash_pre`, the hardcoded 17-byte offset would silently read the wrong bytes. The fragility is in post-hash parsing, not the hash offset itself.

**Reasoning:** Hardcoded offsets without a version-aware parser become maintenance liabilities; any future format change risks silently reading wrong field values.

**Reference:** `code1/f05_verify_hash.py` → `verifyFileIntegrity()` ~line 109

---

**Q31. In `f05_verify_hash.py`, the module docstring describes a Man-in-the-Middle (MitM) scenario where an attacker flips bits in the ciphertext. How does AES-GCM's built-in authentication tag already address this threat, and why is the separate SHA-256 hash still necessary?**

**Answer:** AES-GCM's authentication tag detects any bit flip in the ciphertext during decryption — `AESGCM.decrypt()` raises `InvalidTag` immediately, so no modified plaintext is ever produced. The separate SHA-256 `hash_pre`/`hash_post` check provides an independent integrity layer for a different threat: corruption or logic bugs in the decryption pipeline itself (e.g., a software bug that returns the wrong plaintext), and for verifying that the original file was not modified before encryption took place.

**Reasoning:** Defense-in-depth uses redundant controls from different mechanisms; GCM covers ciphertext integrity, while SHA-256 covers plaintext identity across the full lifecycle.

**Reference:** `code1/f05_verify_hash.py` → module docstring ~line 29

---

**Q32. In `f05_verify_hash.py`, `hmac.compare_digest(hash_pre, hash_post)` is used for the hash comparison. Describe concretely how a timing attack on a naive `hash_pre == hash_post` comparison would work step-by-step, and why it is more feasible in a network service context than in a local file check.**

**Answer:** Step-by-step: (1) attacker sends many requests with a guessed hash that differs only in the last byte; (2) the `==` comparison returns `False` at byte position 63 (almost at the end) — this takes slightly longer than a hash differing at byte 0; (3) by comparing thousands of response times, the attacker identifies which prefix produces the longest comparison time, revealing the next correct byte; (4) repeating this recovers the full expected hash. Over a network this is feasible because the attacker can send thousands of requests, average timing noise, and measure precise response-time differences of microseconds. Locally, OS scheduling jitter usually drowns out the signal.

**Reasoning:** Network timing oracles amplify tiny timing differences through statistical averaging over many samples; local function calls are dominated by OS/CPU scheduling noise that hides the signal.

**Reference:** `code1/f05_verify_hash.py` → `verifyHash()` ~line 69

---

**Q33. In `f06_secure_key_storage.py`, two KDF options are supported: `ARGON2ID` (default) and `PBKDF2-SHA256` (compatibility fallback). What makes Argon2id superior to PBKDF2 for password-based key derivation, specifically against GPU-based brute-force attacks?**

**Answer:** Argon2id is memory-hard: it requires a configurable amount of RAM (64 MB in SFFS) for each hash computation. GPUs have limited per-core RAM bandwidth and thousands of cores designed for parallel low-memory operations — the memory requirement serialises their attack by forcing each attempt to occupy a full 64 MB RAM window. PBKDF2 uses only CPU cycles (HMAC-SHA256 iterations), which GPUs can compute millions of times per second in parallel using their many small cores and shared memory.

**Reasoning:** Memory hardness is the key differentiator; GPU attacks on PBKDF2 with 310,000 iterations are orders of magnitude faster than against Argon2id with the same wall-clock cost for a legitimate user.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 118

---

**Q34. In `f06_secure_key_storage.py`, the `ARGON2_MEMORY_COST = 65536` (KiB = 64 MB). Explain how memory-hardness works as a defense: why does requiring 64 MB of RAM per hash attempt slow down GPU attacks specifically?**

**Answer:** A modern GPU has thousands of compute cores but a shared, bandwidth-limited memory system. Computing Argon2id requires each core to perform pseudo-random reads and writes across the full 64 MB working set; because GPU memory bandwidth is shared among all cores, only a small number of cores can simultaneously maintain an independent 64 MB window. This reduces effective parallelism from thousands of parallel guesses to perhaps a handful, cutting GPU throughput by 2–3 orders of magnitude compared to PBKDF2.

**Reasoning:** Memory bandwidth is the bottleneck, not compute; 64 MB × (number of parallel attempts) must fit within GPU VRAM, and VRAM bandwidth limits how fast those 64 MB blocks can be accessed.

**Reference:** `code1/f06_secure_key_storage.py` → module constants ~line 77

---

**Q35. In `f06_secure_key_storage.py`, the salt is 16 bytes generated per keystore. Why must the salt be unique per keystore, and why is it safe to store the salt in plaintext alongside the encrypted private key?**

**Answer:** A unique salt per keystore ensures that even if two users share the same master password, their derived AES wrap keys will differ — preventing a single precomputed dictionary (rainbow table) from cracking multiple keystores at once. The salt is safe to store in plaintext because it provides no advantage without the password: the KDF takes `f(password, salt)` and the salt alone cannot reveal the derived key or the password.

**Reasoning:** Salts are non-secret by design; their purpose is to make each password-to-key derivation unique, defeating precomputation attacks.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 115

---

**Q36. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function copies `private_key_bytes` into a `bytearray` called `private_key_mutable`, then zeros it byte-by-byte after encryption. Why is a `bytearray` used instead of `bytes`, and why is the byte-by-byte zeroing loop necessary rather than just `del private_key_bytes`?**

**Answer:** Python `bytes` objects are immutable — their backing memory cannot be overwritten after creation. A `bytearray` is mutable, allowing in-place zeroing of each byte. `del private_key_bytes` only removes the Python reference and schedules the object for garbage collection, but the GC may not run immediately (or ever, in CPython's reference-counting model when there are other references) — leaving the private key bytes in memory for an arbitrary duration. The byte-by-byte `for _i in range(len(...)): private_key_mutable[_i] = 0` deterministically overwrites the memory before the reference is dropped.

**Reasoning:** The code comment explicitly notes "A bytearray lets us overwrite every byte with 0 deterministically"; CPython GC timing is nondeterministic, so relying on `del` for sensitive data is insufficient.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 149

---

**Q37. In `f06_secure_key_storage.py`, the keystore JSON stores a `"version"` field: `"2.0"` for Argon2id and `"1.0"` for PBKDF2. In `retrieveKey()`, the code reads the `"kdf"` field and dispatches to the appropriate KDF. What backward-compatibility risk exists if the `"kdf"` field is absent in a legacy keystore, and how does the code handle it?**

**Answer:** A legacy keystore created before the `"kdf"` field was introduced will have no `"kdf"` key. In `retrieveKey()`, `kdf_name = (keystore_data.get("kdf") or "PBKDF2-SHA256").upper()` handles this: `.get("kdf")` returns `None` for absent keys, the `or "PBKDF2-SHA256"` default kicks in, and the code falls back to PBKDF2 — which is the only KDF the legacy version would have used. This means legacy keystores transparently upgrade to PBKDF2 behaviour without error.

**Reasoning:** The `or "PBKDF2-SHA256"` guard is an explicit backward-compatibility shim; without it a missing `"kdf"` field would cause a `KeyError` at runtime.

**Reference:** `code1/f06_secure_key_storage.py` → `retrieveKey()` ~line 235

---

**Q38. In `f06_secure_key_storage.py`, the `hashlib_sha256_sandwich()` function computes `hash(salt || hash(iv))` to generate a `key_id`. Why is a "sandwich" construction (inner hash first, then outer hash) used here rather than a simple `hash(salt + iv)`? What length-extension attack does this defend against?**

**Answer:** SHA-256 (like all Merkle-Damgård hash functions) is vulnerable to length-extension attacks: given `hash(M)`, an attacker can compute `hash(M || padding || X)` for any chosen `X` without knowing `M`. A simple `hash(salt + iv)` could be length-extended if an attacker knows `salt` and the result. The sandwich construction `hash(salt || hash(iv))` embeds the inner hash as fixed-size input to the outer hash, breaking the length-extension property because the inner digest is a fixed 32-byte block regardless of `iv` length.

**Reasoning:** The sandwich/double-hash pattern is a lightweight defense against Merkle-Damgård length extension; HMAC is the more formal solution, but the double-hash achieves the same goal here.

**Reference:** `code1/f06_secure_key_storage.py` → `hashlib_sha256_sandwich()` ~line 203

---

**Q39. In `f06_secure_key_storage.py`, the `wrapAESKey()` function uses `RSA-OAEP-SHA256` (via `PKCS1_OAEP.new(public_key, hashAlgo=SHA256)`). Why is OAEP padding required for RSA encryption, and what vulnerability exists with raw RSA (textbook RSA) encryption?**

**Answer:** Textbook RSA (`c = m^e mod n`) is deterministic and malleable: the same plaintext always produces the same ciphertext, allowing an attacker to detect when the same AES key is encrypted twice; and RSA ciphertexts are multiplicatively homomorphic (`encrypt(m1) * encrypt(m2) = encrypt(m1*m2)`), enabling chosen-ciphertext attacks. OAEP adds randomised padding before encryption, making each encryption of the same key produce a different ciphertext, while the OAEP structure prevents the multiplicative relationship.

**Reasoning:** OAEP is the standard padding for RSA encryption mandated by PKCS#1 v2.1 and NIST; raw RSA is universally considered insecure for production use.

**Reference:** `code1/f06_secure_key_storage.py` → `wrapAESKey()` ~line 322

---

**Q40. In `f06_secure_key_storage.py`, the `wrapAESKey()` function includes a `key_commitment` field: `hashlib.sha256(aes_key).hexdigest()`. What does key commitment verify during `unwrapAESKey()`, and what attack does it prevent that RSA-OAEP alone does not prevent?**

**Answer:** Key commitment verifies that the AES key produced by RSA-OAEP decryption matches the key that was originally wrapped — i.e., it detects wrap-envelope substitution attacks where an attacker replaces the wrapped key bytes with a different RSA-wrapped value that decrypts without error but produces a different AES key. RSA-OAEP alone only ensures the decryption succeeds syntactically; it cannot verify that the result is the intended key rather than some other valid RSA ciphertext.

**Reasoning:** Without commitment, an attacker who can produce a valid RSA-OAEP ciphertext for an arbitrary 32-byte value could substitute a key that decrypts `file.sffs` into garbage, evading detection.

**Reference:** `code1/f06_secure_key_storage.py` → `unwrapAESKey()` ~line 394

---

**Q41. In `f06_secure_key_storage.py`, the `wrapAESKey()` function uses `_hmac.new(aes_key, _h.digest(), hashlib.sha256).hexdigest()` to create a `bound_file_mac` instead of storing the raw SHA-256 of the `.sffs` file. The comment explains this prevents a "correlation attack." Describe this correlation attack: what could an attacker learn from the raw file hash?**

**Answer:** If the wrap envelope stored the raw SHA-256 of the `.sffs` file, anyone who can read wrap envelopes (which may be less protected than the encrypted files themselves) could compute the SHA-256 of any file they suspect was encrypted and compare it to the stored hash — thereby confirming whether that specific file was encrypted by this key pair. This is a content-fingerprinting correlation attack: the raw hash acts as a unique identifier for the ciphertext, enabling an adversary to de-anonymise which files a user encrypted. HMAC-keying the hash with the AES session key makes it unguessable without the key.

**Reasoning:** The code comment states "Storing the raw SHA-256 ... lets an attacker with read access to the wrap envelope fingerprint which encrypted files share content."

**Reference:** `code1/f06_secure_key_storage.py` → `wrapAESKey()` ~line 346

---

**Q42. In `f06_secure_key_storage.py`, the `unwrapAESKey()` function supports both `bound_file_sha256` (legacy) and `bound_file_mac` (v2.1+). What backwards-compatibility risk does supporting the legacy plaintext SHA-256 binding introduce, and how should this be phased out?**

**Answer:** Supporting `bound_file_sha256` allows the correlation attack described in Q41 to remain exploitable for any wrap envelope created with the old code — an attacker who read the plaintext hash from a legacy envelope can still fingerprint file contents. The safe phasing strategy is: (1) set a deprecation date, (2) re-wrap all legacy keys at next login (converting `bound_file_sha256` to `bound_file_mac`), (3) stop accepting `bound_file_sha256` after the migration window.

**Reasoning:** Backward compatibility is a security debt; the legacy path survives indefinitely unless explicitly migrated and removed.

**Reference:** `code1/f06_secure_key_storage.py` → `unwrapAESKey()` ~line 414

---

**Q43. In `f06_secure_key_storage.py`, the keystore JSON is written via `keystore_path.write_text(json.dumps(keystore, indent=2))` to a `.json` file. What are the security implications of storing the keystore as a human-readable JSON file versus a binary format, and what protection does the AES-GCM encryption provide against file system leakage?**

**Answer:** Human-readable JSON is easier to inspect, copy, and parse by an attacker with filesystem access — field names, base64-encoded salt, IV, and KDF parameters are immediately visible. However, AES-GCM encrypts `encrypted_private_key` with a GCM authentication tag; without the master password, the ciphertext is computationally indistinguishable from random bytes. The security implication is that readable JSON exposes the KDF parameters (time/memory cost), which an attacker can use to optimise their brute-force attack, but the private key itself remains protected.

**Reasoning:** Readable metadata helps attackers tune their attacks; binary formats would at least require reverse-engineering, but the mathematical protection is the same as long as AES-GCM is unbroken.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 191

---

**Q44. In `f06_secure_key_storage.py`, the `verifyKeystorePassword()` function attempts to decrypt the private key and returns `{"valid": True}` on success without returning the key itself. What security principle does this function implement, and why is it preferable to calling `retrieveKey()` directly just to check a password?**

**Answer:** `verifyKeystorePassword()` implements the principle of least privilege / minimal exposure: it verifies the password is correct by attempting decryption and checking the GCM authentication tag, then discards the decrypted private key bytes without ever returning them to the caller. Calling `retrieveKey()` just to check a password would return the raw private key bytes to the caller who may not need them, widening the surface for accidental logging, caching, or memory leakage of the private key.

**Reasoning:** The private key should only be exposed in memory when it is immediately needed for an RSA operation; a password-check function has no legitimate use for the key itself.

**Reference:** `code1/f06_secure_key_storage.py` → `verifyKeystorePassword()` ~line 271

---

**Q45. In `f06_secure_key_storage.py`, the `KDF_ITERATIONS = 310_000` constant is used for PBKDF2 with the comment "NIST SP 800-63B (2023) recommends ~200k iterations for SHA-256." Why does SFFS use 310,000 iterations rather than exactly 200,000, and what is the tradeoff between increasing iterations and user experience?**

**Answer:** SFFS uses 310,000 (55% above the NIST floor) to provide a buffer against increasing CPU speeds — as hardware improves, 200,000 iterations will become faster and easier to brute-force, but 310,000 extends the useful security lifetime. The tradeoff is login latency: each additional 100,000 iterations adds roughly 30–100 ms (hardware-dependent) to the login time, and at 310,000 iterations on modest hardware the wait may be noticeable but remains under 1 second for most users.

**Reasoning:** Setting iterations above the minimum recommendation is a standard practice to future-proof the system; the user-experience cost is bounded and acceptable for a security application.

**Reference:** `code1/f06_secure_key_storage.py` → module constants ~line 75

---

**Q46. In `f01_generate_key_pairs.py`, the `generated_at` timestamp is produced using `datetime.datetime.now().isoformat()` — a local time without timezone. What auditing problems could arise from using a naive local timestamp in a USB-portable system used across timezones?**

**Answer:** When the USB drive is used in different timezones, `datetime.now()` returns a different local time for the same absolute moment, making it impossible to reconstruct the chronological order of key generation events when auditing logs from different sessions. For example, a key generated at 11 PM in UTC+2 and another generated at 1 AM in UTC-5 would both show as "22:00" and "01:00" without timezone context, potentially appearing to swap their order. Using `datetime.utcnow().isoformat() + "Z"` or `datetime.now(tz=timezone.utc).isoformat()` would fix this.

**Reasoning:** Timezone-naive timestamps are a common auditability anti-pattern in portable applications; they violate the requirement for a canonical global timeline.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 120

---

**Q47. In `f02_encrypt_file.py`, the `file_token` is described as "registered in the provenance table (sffs_data/provenance.json) keyed by hash_pre." Why is `hash_pre` (SHA-256 of the original plaintext) used as the lookup key in the provenance table rather than the filename or the token itself?**

**Answer:** Filenames can be changed by the user, making them unreliable as stable identifiers. Using the token itself as the key would require a separate reverse-index and create a lookup loop (you need the expected token to verify the token). `hash_pre` is derived from the file's content, making it a stable content-addressing key: if the same file is re-encrypted, it will produce the same `hash_pre` and retrieve the same expected token, enabling provenance verification even if the file is renamed or moved.

**Reasoning:** Content-addressing (keying by hash of plaintext) is robust to filename changes and enables deterministic provenance lookup during decryption.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 114

---

**Q48. In `f03_decrypt_file.py`, the import `import hmac as _hmac_mod` appears inside the body of the `decryptFile()` function (inside an `if version == 0x03` block). What is the reason for this lazy import rather than placing it at the module top level?**

**Answer:** The `hmac` module is only needed for V3 provenance token comparison; placing the import inside the `if version == 0x03` block is a form of lazy/deferred import that avoids an unconditional dependency for V2 files. It also makes it explicit to a code reader that this import is specific to the V3 code path — the local `as _hmac_mod` alias avoids any naming conflict with outer-scope variables. Additionally, this pattern was likely added when V3 support was retrofitted without restructuring the whole module.

**Reasoning:** Lazy imports for code paths that are not always executed are a valid Python pattern for clarity and minor startup-time reduction; the alias avoids namespace pollution.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 180

---

**Q49. In `f06_secure_key_storage.py`, the `rng_func` parameter in `secureKeyStorage()` defaults to `get_random_bytes` but can be overridden with a custom callable. The docstring says "Pass `session_random_bytes` to mix in mouse-movement entropy." What are the security implications of allowing an arbitrary `rng_func`, and how does the `mouse_entropy.session_random_bytes` function ensure the random bytes are still cryptographically strong even if the mouse pool is empty?**

**Answer:** Allowing an arbitrary `rng_func` means a caller could accidentally pass a weak or deterministic function, producing predictable salts and IVs — a critical vulnerability since salt uniqueness is the foundation of rainbow-table resistance. `session_random_bytes` is designed to XOR OS-provided entropy (from `os.urandom`) with mouse-pool bytes; if the mouse pool is empty it falls back to pure `os.urandom`, ensuring the output is never weaker than the OS CSPRNG. The security level cannot be below `os.urandom` regardless of mouse entropy.

**Reasoning:** The mouse entropy is an optional additive enhancement, not a replacement for OS entropy; the implementation guarantees a floor of CSPRNG-quality randomness.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 110

---

**Q50. In `f06_secure_key_storage.py`, after AES-GCM encryption of the private key, the code stores `auth_tag` as a separate base64 field in the JSON (`"auth_tag": auth_tag_b64`). In `retrieveKey()`, the code calls `cipher.decrypt_and_verify(encrypted_key, auth_tag)`. Why does PyCryptodome's GCM API separate the auth tag from the ciphertext, whereas the `cryptography` library's `AESGCM` (used in f02/f03) appends the tag to the ciphertext automatically?**

**Answer:** PyCryptodome's `AES.MODE_GCM` uses a two-phase API: `encrypt_and_digest()` returns `(ciphertext, tag)` as separate objects, giving the caller explicit control over storage layout. The `cryptography` library's `AESGCM` follows the TLS/AEAD convention of appending the 16-byte tag to the end of the ciphertext blob, making the combined `ciphertext+tag` a single opaque value. Both approaches are cryptographically equivalent — the choice is an API design decision, not a security difference — but SFFS f06 uses PyCryptodome while f02/f03 use `cryptography`, hence the different handling.

**Reasoning:** The two libraries were chosen for different reasons (PyCryptodome for its PBKDF2/RSA/OAEP API in f06; `cryptography` for its AESGCM high-level API in f02/f03); the tag-handling difference follows from the libraries' different conventions.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 153

---

**Q51. In `f02_encrypt_file.py`, the plaintext is encrypted directly: `ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)`. An earlier design described injecting the provenance token into the plaintext at a `token_offset` before encryption. Why was the design changed to store the token in the plaintext header instead of inside the ciphertext?**

**Answer:** Injecting the token inside the ciphertext means the provenance check cannot happen until after decryption — the token is not readable without the AES key. Storing the token in the plaintext header allows provenance verification before any decryption occurs ("Nothing is decrypted until provenance passes"), which is the current design goal. This ordering ensures that if provenance fails, no plaintext is ever produced, eliminating an entire class of attacks where a failed provenance check still exposes partial decrypted data.

**Reasoning:** The architectural change prioritised the "fail before any plaintext exposure" principle over the earlier design that embedded the token in ciphertext for cryptographic binding.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 132

---

**Q52. In `f01_generate_key_pairs.py`, the public key is saved in `SubjectPublicKeyInfo` format rather than the older `PKCS1` format. What is the difference between these two PEM formats, and why does the `wrapAESKey()` function in `f06_secure_key_storage.py` need to handle the key format correctly when importing it?**

**Answer:** PKCS#1 format contains only the RSA public-key parameters (modulus and exponent) with a `BEGIN RSA PUBLIC KEY` header. SubjectPublicKeyInfo (SPKI) is a container that includes an algorithm identifier (`rsaEncryption` OID) plus the PKCS#1 data inside, using `BEGIN PUBLIC KEY` header. PyCryptodome's `RSA.import_key()` in `wrapAESKey()` handles both formats transparently, but if the wrong parser were used or a format mismatch occurred, `import_key()` would raise an exception — meaning the AES key wrap would fail and encryption would abort.

**Reasoning:** SPKI is the modern standard for public key interoperability (X.509, TLS); using it in f01 while importing in f06 via `RSA.import_key()` is safe because PyCryptodome auto-detects the format.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 91

---

**Q53. In `f04_generate_hash.py`, when `target` is a `bytes` object, the entire bytes value is hashed in a single call (e.g., `sha256(target).hexdigest()`) rather than using the streaming chunked approach. Is this a security issue? Under what conditions could a `bytes` input cause memory exhaustion?**

**Answer:** It is not a security issue from a hash-correctness standpoint — the result is identical to chunked hashing. However, it can cause memory exhaustion: if the caller passes a `bytes` object representing a very large in-memory buffer (e.g., a 500 MB decrypted file read via `read_bytes()`), that buffer must already be in memory plus the hash function needs to hold a copy of it. If the system is already memory-constrained, this double allocation could trigger OOM. The 2 GB limit in f03 limits the size of decrypted content but does not prevent large `bytes` inputs to `generateHash` from other callers.

**Reasoning:** The single-call `sha256(target)` approach copies the bytes into the hash function's internal buffer; for large inputs, this doubles effective memory usage briefly.

**Reference:** `code1/f04_generate_hash.py` → `generateHash()` ~line 76

---

**Q54. In `f05_verify_hash.py`, `verifyFileIntegrity()` has special-case logic for `.sffs` files that reads `hash_pre` from the binary header. What happens if the function is called on a V3 `.sffs` file (which has a variable-length extension field between the file size and the provenance token)? Will the `hash_pre` extraction still be correct?**

**Answer:** Yes, `hash_pre` extraction is still correct for V3 files because `hash_pre` is always located at bytes 17–49 (after Magic(4) + Version(1) + IV(12)), which is the same fixed offset in both V2 and V3. The variable-length extension field appears after `hash_pre` (at byte 57+), not before it. The `verifyFileIntegrity()` function then correctly skips `orig_size(8) + ext_len(1) + ext(N)` bytes after reading `hash_pre`, so subsequent field reads are also position-accurate.

**Reasoning:** The V3 format was designed to keep `hash_pre` at the same fixed offset to avoid breaking V2-era parsing code like `verifyFileIntegrity()`.

**Reference:** `code1/f05_verify_hash.py` → `verifyFileIntegrity()` ~line 109

---

**Q55. In `f03_decrypt_file.py`, `output_path = output_dir / (sffs_path.stem + original_ext)` restores the original filename by combining the `.sffs` stem with the stored extension. What path traversal risk exists if `original_ext` were stored as something like `"/../../../etc/passwd"`, and does the current code guard against this?**

**Answer:** If `original_ext` contained path traversal sequences like `/../../../etc/passwd`, then `output_dir / (stem + original_ext)` could resolve to a path outside `output_dir` — for example `output_dir/document/../../../etc/passwd`, potentially overwriting a sensitive system file with decrypted content. The current code does guard against this in part: the extension length is capped at 32 bytes during encryption (preventing long traversal strings), but the decryption code does not explicitly check that the assembled `output_path` remains inside `output_dir`, which could still be exploited if an attacker crafts a short traversal string.

**Reasoning:** The 32-byte cap limits but does not fully eliminate path traversal; a proper fix would require `output_path.resolve().is_relative_to(output_dir.resolve())` check after construction.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 226

---

**Q56. In `f06_secure_key_storage.py`, `restoreKeysFromCloud()` in `sffs_core.py` validates zip members with `if member_path.is_absolute() or ".." in member_path.parts`. Discuss whether this path traversal check is sufficient. Are there edge cases (e.g., on Windows with drive letters, or with symlinks) that it might miss?**

**Answer:** The check covers the most common traversal patterns but has edge cases: (1) on Windows, `Path("C:\\evil")` is absolute and caught, but `Path("C:evil")` (a drive-relative path without backslash) has `is_absolute() == False` and `".."` not in parts — this could resolve unexpectedly; (2) `zipfile` on Python can extract symlinks that point outside the target directory, and neither `is_absolute()` nor `".."` checks detect a symlink target string; (3) null bytes in member names could confuse path parsing on some systems. A safer check uses `member_path.resolve()` within the extraction target and verifies it stays under `keys_dir`.

**Reasoning:** The check is a reasonable first layer but incomplete for Windows drive-relative paths and symlink attacks; `extractall` should be replaced with per-member `extract` with a resolved-path check.

**Reference:** `main-code/sffs_core.py` → `restoreKeysFromCloud()` ~line 760

---

**Q57. In `f02_encrypt_file.py`, the `SFFS_VERSION` constant is set to `0x03`. If a future version needed to encrypt large files in chunks rather than loading the entire plaintext into memory, what changes would need to be made to the file format and the `encryptFile()` function?**

**Answer:** A chunked format (e.g., version `0x04`) would need to: (1) add a chunk-count or chunk-size field to the header; (2) write each chunk as `(chunk_iv_12B)(chunk_ciphertext+tag)` in sequence; (3) use independent IVs per chunk (or a deterministic counter-nonce scheme); (4) add an optional top-level authentication tag over all chunk hashes to detect reordering or deletion of chunks. The `encryptFile()` function would need to process input as a stream, writing chunks incrementally rather than calling `input_path.read_bytes()` once.

**Reasoning:** Chunked GCM encryption (as used in TLS record-layer design) requires per-chunk nonce management and sequence integrity to prevent chunk reordering attacks.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 109

---

**Q58. In `f06_secure_key_storage.py`, the `secureKeyStorage()` and `retrieveKey()` functions both re-derive the AES wrap key from the master password every time they are called. What is the performance cost of Argon2id with `time_cost=3, memory_cost=65536, parallelism=4` at login time, and why is this cost intentional?**

**Answer:** With Argon2id at `time_cost=3, memory_cost=65536 KiB (64 MB), parallelism=4`, the derivation typically takes 0.3–2 seconds on modern consumer hardware (exact time depends on CPU and RAM bandwidth). This cost is intentional because it directly limits how many password guesses an attacker can make per second — at 1 second per guess, even a fast server can test only ~86,400 passwords per day per thread, making brute-force of even a moderately weak password computationally infeasible.

**Reasoning:** The entire security model of password-based key derivation relies on the derivation being expensive; reducing the cost to improve performance would proportionally weaken the brute-force resistance.

**Reference:** `code1/f06_secure_key_storage.py` → module constants ~line 76

---

**Q59. In `f01_generate_key_pairs.py`, no mechanism prevents generating multiple RSA key pairs for the same user. In `sffs_core.py`, `_ensure_rsa_keys()` calls `sorted(keys_dir.glob("public_key_*.pem"))` and picks `candidates[0]`. What could go wrong if two key pairs exist and the user's keystore was created with `candidates[1]`?**

**Answer:** `sorted(keys_dir.glob("public_key_*.pem"))` sorts by filename, which means `candidates[0]` is the lexicographically first public key file. If the user's keystore was created with the second key pair (`candidates[1]`), `_ensure_rsa_keys()` would return the public key of the first pair — and `encryptFile` would encrypt new files with the first pair's public key. When decryption is attempted, `unwrapAESKey()` would try to decrypt the wrapped AES key using the keystore for the first key pair, which holds a different private key than the one that was used to wrap — RSA-OAEP decryption would fail with a `ValueError`, blocking all file operations.

**Reasoning:** The key-selection logic picks by sort order rather than by matching keystore; a multi-key scenario creates a mismatch between the public key used for encryption and the private key stored in the selected keystore.

**Reference:** `main-code/sffs_core.py` → `_ensure_rsa_keys()` ~line 305

---

**Q60. In `f03_decrypt_file.py`, the `decryptFile()` function writes the decrypted plaintext to disk before returning. Describe a scenario in which this represents a security risk even with a properly isolated sandbox, and what additional protection could be added (such as the sandbox watcher in `sffs_core.py`).**

**Answer:** If the sandbox directory is shared or accessible by another process on the same system (e.g., a privileged system service, antivirus scanner, or malicious process with elevated permissions), it could read the decrypted file between the moment `write_bytes()` writes it and the moment the user closes it. Additionally, if the SFFS process is killed abnormally before sandbox cleanup, the decrypted file persists indefinitely. The sandbox watcher in `sffs_core.py` addresses this by scanning for files not registered in `_decrypted_registry` and wiping them, but it also only runs every 2 seconds — a narrow window still exists.

**Reasoning:** Writing plaintext to disk, even in a sandbox, introduces a race window; the sandbox watcher closes most of this gap but cannot eliminate the initial write-to-register interval.

**Reference:** `main-code/sffs_core.py` → `_start_sandbox_watcher()` ~line 434

---

**Q61. In `f06_secure_key_storage.py`, the `wrapAESKey()` function creates a JSON envelope with `json.dumps(envelope, separators=(",", ":"))`. Why are compact separators used (no spaces), and what is the security significance of the `sort_keys` behavior when creating the HMAC signature in `sffs_core.py`'s `_sign_worker_payload()`?**

**Answer:** Compact separators (`","` and `":"` without spaces) produce a deterministic, minimal JSON serialisation — no formatting variation means the same data always serialises to the same bytes, which is critical for HMAC signing where even a single extra space would invalidate the signature. In `_sign_worker_payload()`, `json.dumps(envelope, sort_keys=True, separators=(",", ":"))` further normalises key ordering; without `sort_keys=True`, Python dict serialisation order can vary between versions (though CPython 3.7+ preserves insertion order), and a signature computed on one ordering would fail verification if the dict keys were iterated in different order on the receiving end.

**Reasoning:** Canonical serialisation (compact + sorted keys) ensures the HMAC is computed over an identical byte sequence regardless of dict construction order or Python version.

**Reference:** `main-code/sffs_core.py` → `_sign_worker_payload()` ~line 622

---

**Q62. In `f02_encrypt_file.py`, the `secrets` module is used for both `file_token = secrets.token_bytes(32)` and `iv = secrets.token_bytes(12)`. Why is `secrets` preferred over `random.getrandbytes()` for cryptographic random generation in Python?**

**Answer:** The `secrets` module is explicitly designed for cryptographic use and internally calls `os.urandom()`, which reads from the OS's CSPRNG (Cryptographically Secure Pseudo-Random Number Generator) — `/dev/urandom` on Linux or `CryptGenRandom`/`BCryptGenRandom` on Windows. Python's `random` module uses the Mersenne Twister algorithm, which is a statistical PRNG, not a CSPRNG; its state can be reconstructed from 624 consecutive 32-bit outputs, making it unsuitable for key material, tokens, or IVs.

**Reasoning:** Python's own documentation explicitly states `random` must not be used for security purposes; `secrets` was added in Python 3.6 specifically to provide a clear, unambiguous interface for cryptographic randomness.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 121

---

**Q63. In `f06_secure_key_storage.py`, `ARGON2_PARALLELISM = 4` is used. Explain what the parallelism parameter controls in Argon2id, and why a higher parallelism value does not proportionally increase GPU attack cost in the way that higher memory cost does.**

**Answer:** The parallelism parameter controls how many independent lanes (threads) Argon2id uses internally when computing a single hash — it sets the number of parallel computation threads that fill and traverse the memory matrix. A higher parallelism value allows legitimate users on multi-core hardware to use multiple cores and complete the computation faster. However, it does not proportionally hurt GPU attackers because GPUs already have enough cores to match any practical parallelism value; the bottleneck for GPUs is memory bandwidth (determined by `memory_cost`), not thread count.

**Reasoning:** Memory cost scales linearly with GPU attack cost; parallelism primarily affects how well legitimate multi-core CPUs can exploit the operation, without adding proportional GPU resistance.

**Reference:** `code1/f06_secure_key_storage.py` → module constants ~line 79

---

**Q64. In `f05_verify_hash.py`, the `verifyHash()` function returns `"match": True/False` and `"alert_level"`. In the calling context (decryption pipeline), what would be the correct behavior if `match == False`: silently continue, raise an exception, or call `emergencyLock()`? Justify your answer with reference to the threat model.**

**Answer:** The correct response is to raise an exception (specifically `SecurityError`) and trigger `emergencyLock()`. The threat model includes active tamper attacks: `match == False` after decryption means the file's plaintext does not match the pre-encryption hash, which could indicate the AES key was wrong (a bug), the header was tampered with, or the decrypted output was modified post-decryption. Silently continuing would present corrupted or malicious data to the user; just raising without `emergencyLock()` would leave the tampered file and sandbox state intact, potentially allowing further exploitation.

**Reasoning:** A tamper detection event is a security incident, not a recoverable error; the SFFS threat model mandates fail-closed behaviour (emergencyLock) when integrity is violated.

**Reference:** `code1/f05_verify_hash.py` → `verifyHash()` ~line 76

---

**Q65. In `f02_encrypt_file.py`, the function signature includes `aes_key: bytes` but nowhere generates the AES key itself. In `sffs_core.py`'s `encryptFileOperation()`, the key is generated with `aes_key = session_random_bytes(32)`. Why is key generation deliberately separated from the encryption function rather than letting `encryptFile()` generate its own key?**

**Answer:** Separating key generation from encryption enables the caller to control key quality (entropy source) and key lifecycle — specifically, to wrap and store the key (via `wrapAESKey`) before encrypting and to ensure the same key is used if encryption needs to be retried. If `encryptFile()` generated its own key internally and returned it, the caller would need to immediately wrap and store that returned key, which creates a race condition if the process crashes between encryption and key storage. The current design lets `encryptFileOperation()` wrap the key first, then encrypt.

**Reasoning:** Single-responsibility principle: `encryptFile()` is a pure cryptographic primitive; key management is an orchestration concern handled by `sffs_core.py`.

**Reference:** `main-code/sffs_core.py` → `encryptFileOperation()` ~line 345

---

**Q66. In `f01_generate_key_pairs.py`, the module docstring outlines the "Key Lifecycle in SFFS" in four numbered steps. What would happen to the security of the entire system if step 2 (passing the private key to `secureKeyStorage()`) were skipped and the key bytes were instead returned to the caller and stored as a plain text file?**

**Answer:** The entire system's security would be catastrophically compromised: any attacker with read access to the filesystem (or USB drive) could read the plaintext `.pem` private key file, decrypt any `.sffs` file encrypted with the corresponding public key, and impersonate the legitimate user for all future encryptions. The private key is the root secret protecting all encrypted files — its plaintext exposure eliminates all downstream cryptographic protections regardless of how strong the AES encryption or hash verification layers are.

**Reasoning:** The security chain is only as strong as its weakest link; a plaintext private key on disk is the weakest possible link, rendering the entire cryptographic system useless.

**Reference:** `code1/f01_generate_key_pairs.py` → module docstring ~line 23

---

**Q67. In `f06_secure_key_storage.py`, the keystore format version is `"2.0"` for Argon2id and `"1.0"` for PBKDF2. If the `"version"` field were used to choose the KDF rather than the `"kdf"` field, what specific attack could a malicious keystore file mount by setting `version = "1.0"` for a keystore that was actually encrypted with Argon2id?**

**Answer:** An attacker who can modify the keystore file on disk (e.g., by gaining filesystem access) could set `"version": "1.0"` while leaving the ciphertext encrypted with Argon2id parameters. `retrieveKey()` would then use PBKDF2 to derive the key, producing a completely different derived key — decryption would fail with a MAC error, effectively locking the user out. Alternatively, if the attacker generated the ciphertext with PBKDF2 and set `"version": "2.0"`, retrieval would try Argon2id, again failing — a denial-of-service attack on key access. Using the explicit `"kdf"` field makes the KDF selection unambiguous and independent of the version number.

**Reasoning:** Separate `"kdf"` and `"version"` fields prevent a version downgrade from silently changing the KDF; the `"kdf"` field is authoritative for KDF selection.

**Reference:** `code1/f06_secure_key_storage.py` → `retrieveKey()` ~line 235

---

**Q68. In `f03_decrypt_file.py`, after the provenance token check, the ciphertext is decrypted with `decrypted = aesgcm.decrypt(iv, ciphertext, None)`. At what point in this call does GCM authentication tag verification occur, and what exception is raised if the tag is invalid?**

**Answer:** In the `cryptography` library's `AESGCM.decrypt()`, tag verification occurs atomically before any plaintext is returned — the GCM counter-mode decryption runs, and then the GHASH over the ciphertext and AAD is computed and compared to the stored tag; if the comparison fails, no plaintext is ever returned. The exception raised is `cryptography.exceptions.InvalidTag` (imported at the top of f03 as `from cryptography.exceptions import InvalidTag`). The `except (ValueError, InvalidTag)` block in `decryptFile()` catches both.

**Reasoning:** The `cryptography` library's AESGCM API is specified to raise `InvalidTag` on authentication failure; `ValueError` is also caught as a defensive measure for malformed inputs.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 204

---

**Q69. In `f04_generate_hash.py`, the `generateHash()` function raises `TypeError` if `target` is neither `Path`, `str`, nor `bytes`. What is the security rationale for raising an exception rather than silently casting an unknown type (e.g., converting an integer to its string representation before hashing)?**

**Answer:** Silently casting an unknown type would allow callers to accidentally pass non-file data (like a session token, a password integer representation, or a debug object) and receive a hash value that appears to be a valid file hash but is semantically incorrect. This could silently corrupt the integrity-verification pipeline — for example, a caller who passes an integer file descriptor instead of a `Path` object would get a hash of the string "5" rather than the file's contents, and the mismatch would never raise an error. Raising `TypeError` fails loudly, ensuring such programmer errors are caught immediately during development.

**Reasoning:** Fail-loudly is a core secure-coding principle; silent type coercion hides bugs that can corrupt the security-critical integrity chain.

**Reference:** `code1/f04_generate_hash.py` → `generateHash()` ~line 110

---

**Q70. In `f06_secure_key_storage.py`, the `retrieveKey()` function catches `ValueError` from `cipher.decrypt_and_verify()` and re-raises it as a new `ValueError` with a generic message. What information is deliberately omitted from the error message to prevent a timing or oracle attack?**

**Answer:** The generic message "Keystore decryption failed — wrong password or corrupted keystore" deliberately omits: (1) which specific field caused the failure (MAC tag mismatch vs. key derivation error vs. padding error), (2) the length or any bytes of the derived key, and (3) whether the failure occurred during key derivation or during AES-GCM decryption. Distinguishing "wrong password" from "corrupted ciphertext" would allow an attacker to use the decryption routine as a key-correctness oracle — learning whether a guessed password derived the right key even without fully decrypting the data.

**Reasoning:** Error messages that distinguish failure modes enable oracle attacks; a uniform error message eliminates the attacker's ability to gain information from decryption failures.

**Reference:** `code1/f06_secure_key_storage.py` → `retrieveKey()` ~line 263

---

**Q71. In `f02_encrypt_file.py`, the function returns a `file_token` field but the caller in `sffs_core.py` is responsible for registering it in the provenance table. What is the risk if a file is encrypted but the provenance registration step is skipped (e.g., due to a crash between `encryptFile()` returning and `_provenance_table.register()` being called)?**

**Answer:** If provenance is not registered, the decryption provenance check will fail for that file — when `sffs_core.py` looks up `table[hash_pre]` it will find no entry and either skip the check (if `expected_token is None`) or raise a `SecurityError`. In the current implementation, `expected_token_hex = ""` is passed if no provenance entry is found, so the file can still be decrypted without provenance verification — effectively treating the file as if it were V2. This means the provenance security guarantee is silently degraded for any file whose registration was lost.

**Reasoning:** The two-phase commit problem (encrypt then register) creates a window where the invariant "every V3 file has a provenance entry" can be violated; a crash-safe implementation would use a transaction or write-ahead log.

**Reference:** `main-code/sffs_core.py` → `encryptFileOperation()` ~line 351

---

**Q72. In `f01_generate_key_pairs.py`, the public key filename is `public_key_{key_id}.pem` where `key_id` is derived from the hash of the public key PEM. Why is it important that the filename contains the key_id, as opposed to a fixed name like `public_key.pem`? What data-loss scenario does this prevent?**

**Answer:** Using a fixed filename `public_key.pem` would mean that generating a second key pair silently overwrites the first public key file — and with it, the only way to identify which keystore corresponds to which public key. With `key_id` in the filename, multiple key pairs coexist without collision; the code comment states "Filename includes key_id to prevent silent overwrite of existing keys." The data-loss scenario prevented is: user generates a second key pair (e.g., after a perceived key compromise), the new public key overwrites the old file, but all existing encrypted files were wrapped with the old public key — they become permanently undecryptable because the matching keystore cannot be identified.

**Reasoning:** Content-derived filenames provide both uniqueness and a stable key-to-file mapping; fixed filenames create destructive overwrite risk.

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 106

---

**Q73. In `f06_secure_key_storage.py`, the GCM IV for key wrapping is 12 bytes (`iv = _rng(12)`), matching the NIST-recommended nonce length. If the same IV were accidentally reused with the same derived AES wrap key (e.g., on a system with a weak RNG), what specific property of AES-GCM would be catastrophically broken?**

**Answer:** IV reuse under the same AES-GCM key completely destroys confidentiality and authentication. If two different messages are encrypted with the same `(key, IV)` pair, XORing the two ciphertexts cancels the keystream, revealing `plaintext1 XOR plaintext2` — from which both plaintexts can often be recovered. More critically, the GHASH key (`H = AES_K(0^128)`) is deterministic for a given key, and two ciphertexts with the same IV share the same `H`; an attacker can recover `H` from the two authentication tags and then forge valid authentication tags for arbitrary messages.

**Reasoning:** GCM's nonce reuse vulnerability is well-documented; the "GCM nonce misuse" attack allows both plaintext recovery and tag forgery with just two ciphertext pairs under the same nonce.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 142

---

**Q74. In `f05_verify_hash.py`, the module explains that `hash_pre` proves "original plaintext integrity" and that "any tampering (even 1 bit) changes the hash completely (avalanche effect)." Explain the avalanche effect mathematically: in SHA-256, approximately how many output bits are expected to change when 1 input bit is flipped?**

**Answer:** The avalanche effect in SHA-256 means that each output bit depends on every input bit through multiple rounds of mixing operations. Flipping a single input bit propagates through the compression function's 64 rounds of ARX (addition, rotation, XOR) operations, and by the final round, each output bit has approximately a 50% probability of having flipped. For a 256-bit output, this means approximately 128 out of 256 output bits change (50%), making the hash of the modified input completely unrecognizable from the original — effectively a new random-looking 256-bit value.

**Reasoning:** The 50% expected bit-flip rate is a consequence of the diffusion and confusion properties built into SHA-256's compression function; this is the definition of a good avalanche effect.

**Reference:** `code1/f05_verify_hash.py` → module docstring ~line 32

---

**Q75. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function generates a `key_id` using `hashlib_sha256_sandwich(salt, iv)` when no `key_id` is supplied. This ID is only 16 hex characters (8 bytes). What is the probability of a collision among `N` keystores using the birthday paradox formula, and at what value of N does this probability exceed 1%?**

**Answer:** The birthday paradox collision probability for `N` items in a space of size `M = 2^64` is approximately `P ≈ N^2 / (2 * M) = N^2 / 2^65`. Setting `P = 0.01` (1%): `N^2 = 0.01 * 2^65 ≈ 3.69 × 10^17`, so `N ≈ √(3.69 × 10^17) ≈ 6.07 × 10^8` — approximately 607 million keystores. For any realistic deployment (even enterprise-scale with millions of users), the 1% collision threshold is far beyond the expected number of keystores, making 8-byte IDs practically sufficient.

**Reasoning:** The birthday bound at 64 bits gives roughly √(2^64) ≈ 4.3 billion for 50% collision probability; 1% is reached around 607 million, well above real deployment sizes.

**Reference:** `code1/f06_secure_key_storage.py` → `hashlib_sha256_sandwich()` ~line 203

---

**Q76. In `f03_decrypt_file.py`, the module docstring lists 10 steps in the "Decryption Process." Step 9 says "Compare hash_post with hash_pre (via verifyHash module)." In the actual implementation of `decryptFile()`, this comparison is NOT performed — it returns both hashes but leaves comparison to the caller. Is this an implementation bug or intentional design? Justify.**

**Answer:** This is intentional design. `decryptFile()` is a lower-level primitive that returns `hash_pre` and `hash_post` in its result dict and delegates the comparison to the caller (`sffs_core.py`), which can apply the appropriate response policy (raise, log, emergencyLock). If `decryptFile()` performed the comparison itself, it would conflate the cryptographic primitive with the policy decision — violating separation of concerns. The docstring step 9 describes the overall pipeline, not the single function; the comparison is performed at the `sffs_core.py` level using `verifyHash()`.

**Reasoning:** Primitive functions should not embed policy decisions; the caller is the appropriate place to decide what to do when `hash_pre != hash_post`.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 230

---

**Q77. In `f02_encrypt_file.py`, the comment on line 138 says "no token injection into plaintext." An earlier design injected the 32-byte token at a random `token_offset` inside the plaintext before encryption. What was the security rationale for that approach, and why was it changed to storing the token in the plaintext header?**

**Answer:** The earlier injection approach cryptographically bound the token to the ciphertext — an attacker could not separate the token from the encrypted content because it was inside the encrypted blob at an unknown offset. The design was changed to a plaintext header token so that provenance verification can happen before any decryption attempt: if the header token is not in the provenance table, the AES key is never used and no plaintext is ever produced. The loss of cryptographic binding is offset by the provenance table's secrecy and by GCM's authentication tag covering the ciphertext.

**Reasoning:** The "fail before decryption" requirement was deemed more important than the cryptographic binding of the earlier design; the provenance table serves as the security boundary instead.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 132

---

**Q78. In `f06_secure_key_storage.py`, the `KDF_ITERATIONS = 310_000` constant is declared at module level, but Argon2id parameters (`ARGON2_TIME_COST`, etc.) are also declared at module level. Why is it important that these constants match between `secureKeyStorage()` and `retrieveKey()`, and what would happen if a developer changed `ARGON2_MEMORY_COST` in a deployed system?**

**Answer:** The KDF parameters used during key storage are the parameters used to derive the AES wrap key from the master password. During retrieval, the same parameters must reproduce the same derived key. `retrieveKey()` reads the parameters stored in the keystore JSON (`argon2_memory_cost`, etc.) rather than the module-level constants, so changing a constant in the code does not break existing keystores — new keystores will use the new value while old keystores will use their stored values. However, if the stored JSON field were absent (legacy keystore), retrieval would fall back to the module-level constant — so changing the constant would cause legacy keystores to use the wrong memory cost and fail decryption.

**Reasoning:** The JSON-stored parameters (`keystore_data.get("argon2_memory_cost", ARGON2_MEMORY_COST)`) provide per-keystore parameter persistence; the module constant is only the fallback for keystores that predate parameter storage.

**Reference:** `code1/f06_secure_key_storage.py` → `retrieveKey()` ~line 240

---

**Q79. In `f01_generate_key_pairs.py`, `from cryptography.hazmat.primitives.asymmetric import rsa` is imported from the `cryptography` library, while `f06_secure_key_storage.py` uses `from Crypto.PublicKey import RSA` from PyCryptodome. Why do two different RSA libraries coexist in the same project? What compatibility issue could arise if both libraries are used on the same key bytes?**

**Answer:** The `cryptography` library is used in f01 for key generation (it has a cleaner modern API and is the recommended choice for new code), while PyCryptodome is used in f06 for RSA-OAEP key wrapping and PBKDF2 (PyCryptodome's `PKCS1_OAEP` and `PBKDF2` APIs are more mature for these use cases). The potential compatibility issue is format handling: `cryptography` exports private keys in PKCS#1 PEM (`BEGIN RSA PRIVATE KEY`) using `TraditionalOpenSSL` format, and PyCryptodome's `RSA.import_key()` can import this format — in practice both handle standard PEM well, but subtle differences in optional fields or encoding could cause `import_key()` to fail on edge cases.

**Reasoning:** PyCryptodome and `cryptography` both support PKCS#1 PEM; the coexistence is a pragmatic choice based on available API quality rather than a technical necessity.

**Reference:** `code1/f01_generate_key_pairs.py` ~line 41; `code1/f06_secure_key_storage.py` ~line 58

---

**Q80. In `f04_generate_hash.py`, the `CHUNK_SIZE = 8 * 1024 * 1024` constant is set to 8 MB. The module says "8MB chunks balance memory usage and I/O performance." How would you empirically determine the optimal chunk size for the target hardware, and what metrics would you measure?**

**Answer:** Empirically, you would benchmark `generateHash()` on a representative large file (e.g., 1 GB) while varying `CHUNK_SIZE` from 1 MB to 128 MB in powers of two, measuring: (1) wall-clock time for the full hash, (2) peak resident memory usage (via `tracemalloc` or `/proc/self/status`), and (3) CPU utilisation and I/O wait percentage. The optimal chunk size is where throughput plateaus (adding more does not improve speed) while keeping peak memory well below the system's available RAM. On USB 3.0 hardware with sequential read speeds of ~100 MB/s, chunk sizes between 4–16 MB typically saturate the storage bandwidth without excessive memory overhead.

**Reasoning:** The tradeoff is I/O batch size vs. memory consumption; empirical measurement on representative hardware gives the actual knee of the curve rather than a theoretical estimate.

**Reference:** `code1/f04_generate_hash.py` → `generateHash()` ~line 100

---

**Q81. In `f02_encrypt_file.py`, the header assembles fields with `struct.pack("Q", original_size)` using little-endian byte order (the "Q" format). Why is little-endian chosen, and what interoperability issue would arise if the `decryptFile()` function (or a third-party implementation) assumed big-endian byte order?**

**Answer:** Python's `struct` module uses native format by default; `"Q"` without a prefix uses the native byte order of the running platform (x86/x64 platforms are little-endian), which is the most common target for SFFS. If a third-party implementation assumed big-endian `">Q"`, the 8-byte `original_size` value would be byte-reversed: a 1024-byte file (stored as `\x00\x04\x00\x00\x00\x00\x00\x00` in little-endian) would be read as 1,125,899,906,842,624 bytes in big-endian, causing an immediate `MAX_FILE_BYTES` rejection or a massive memory allocation attempt.

**Reasoning:** Byte-order mismatches in binary protocols produce silently wrong numerical values; the `original_size` field is the most dangerous because it drives memory allocation in the decryptor.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 167

---

**Q82. In `f06_secure_key_storage.py`, both `PKCS1_OAEP` (from PyCryptodome) and `SHA256` are imported for use in RSA key wrapping. The `PKCS1_OAEP.new(public_key, hashAlgo=SHA256)` specifies SHA-256 as the hash algorithm for OAEP. Why is the hash algorithm choice in OAEP significant for security, and what minimum hash output size is recommended?**

**Answer:** In OAEP, the hash function is used in the mask-generation function (MGF1) and for the label hash — its output size determines the maximum plaintext size that can be padded: `max_plaintext = key_size_bytes - 2*hash_size - 2`. More critically, the hash must be collision-resistant to prevent forged OAEP plaintexts; using MD5 or SHA-1 (which have practical collisions) would weaken OAEP. The recommended minimum is SHA-256 (32-byte output), which also allows encrypting up to `256 - 2*32 - 2 = 190 bytes` under a 2048-bit key — sufficient for a 32-byte AES key.

**Reasoning:** SHA-256 in OAEP is the current industry recommendation (RFC 3447, NIST); it provides 128-bit collision resistance and fits a 32-byte AES key comfortably within the OAEP padding constraints.

**Reference:** `code1/f06_secure_key_storage.py` → `wrapAESKey()` ~line 322

---

**Q83. In `f05_verify_hash.py`, the `verifyFileIntegrity()` function reads the SFFS V3 header but does not skip the provenance token field (32 bytes) before reading the ciphertext. The code reads only `magic(4) + version(1) + IV(12)` then `hash_pre(32)`. Why is the function able to correctly extract `hash_pre` for both V2 and V3 files given that `hash_pre` comes before the version-specific fields?**

**Answer:** The V3 format was deliberately designed to keep `hash_pre` at the same fixed offset (bytes 17–49) as in V2, placing all new version-specific fields (extension length, extension bytes, and provenance token) after `hash_pre` in the header. Since `verifyFileIntegrity()` only needs `hash_pre` and stops reading the header after byte 49, it never encounters the version-specific fields at all — the function is correct for both V2 and V3 by design of the format layout.

**Reasoning:** Backward-compatible format evolution requires that fields consumed by older parsers remain at stable offsets; `hash_pre` was intentionally kept at bytes 17–49 across versions.

**Reference:** `code1/f05_verify_hash.py` → `verifyFileIntegrity()` ~line 109

---

**Q84. In `f03_decrypt_file.py`, after decryption, the function writes the plaintext to `output_path.write_bytes(decrypted)`. The variable `decrypted` is a `bytes` object. What memory security concern does this raise, and how does this differ from the approach taken in `f06_secure_key_storage.py` with `bytearray`?**

**Answer:** `decrypted` is an immutable `bytes` object — its memory cannot be explicitly zeroed after the call to `write_bytes()`. The object will persist in CPython's memory until the garbage collector decides to reclaim it, which may not happen before a memory dump or cold-boot attack could capture it. In contrast, `f06_secure_key_storage.py` copies the private key into a `bytearray`, explicitly zeros every byte with a loop, and then sets the reference to `None` — ensuring the sensitive data is overwritten in memory at a deterministic point rather than being left to GC timing.

**Reasoning:** For highest-sensitivity data (private keys), the `bytearray`-zeroing pattern is preferred; for decrypted plaintext (which is also sensitive), the same technique could be applied but is more complex when integrated with file I/O.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 227

---

**Q85. In `f06_secure_key_storage.py`, `_hmac.new(aes_key, _h.digest(), hashlib.sha256).hexdigest()` is used to create the `bound_file_mac`. The `_hmac` module is imported as `import hmac as _hmac`. Why is the module imported with an alias (`_hmac`), and what naming conflict would occur without the alias?**

**Answer:** Without the `_hmac` alias, the name `hmac` would conflict with the local variable `HMAC` imported from PyCryptodome earlier (`from Crypto.Hash import SHA256, HMAC`). Specifically, the PyCryptodome `HMAC` class and the stdlib `hmac` module would both be in the same namespace, making it ambiguous which `HMAC`/`hmac` a subsequent reference means. The underscore prefix (`_hmac`) also signals that this is an internal module-level reference, following Python convention for private names.

**Reasoning:** The import alias avoids the namespace collision between `from Crypto.Hash import HMAC` (PyCryptodome class) and the stdlib `import hmac` (module); without it, the last assignment would win and the earlier one would be shadowed.

**Reference:** `code1/f06_secure_key_storage.py` ~line 64

---

**Q86. In `f02_encrypt_file.py`, the `output_path` defaults to `input_path.with_suffix(".sffs")`. This means encrypting `document.pdf` produces `document.sffs` in the same directory. What is the risk if the user then accidentally deletes the original `document.pdf` before verifying that decryption works correctly?**

**Answer:** If the original `document.pdf` is deleted before the user verifies that `document.sffs` decrypts correctly, the data becomes inaccessible if: (1) the SFFS keystore is lost or the master password is forgotten, (2) the AES key wrap is corrupted, (3) the `.sffs` file is truncated or its GCM tag is invalid due to storage errors. There is no redundancy — the encrypted file is the only copy. The user should verify decryption to a sandbox before deleting the original, but the current SFFS design does not enforce this verification step.

**Reasoning:** Irreversible single-copy encryption without a verified-decryption step creates a data-loss risk; a safer design would require explicit user confirmation after a test decryption before allowing original deletion.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 180

---

**Q87. In `f06_secure_key_storage.py`, the keystore JSON is written with `json.dumps(keystore, indent=2)`. The `indent=2` makes the file human-readable. What attack surface does this create compared to compact JSON, and under what conditions could an attacker exploit a readable keystore file?**

**Answer:** Human-readable JSON with indentation exposes the KDF type, iteration count, memory cost, salt length, and IV length to any attacker with filesystem read access. Knowing these parameters lets an attacker optimally configure their brute-force tool without having to guess the KDF or parameters. The attack condition is filesystem access (e.g., an attacker reads the USB drive, a malware process scans the filesystem, or the keystore is inadvertently committed to a repository). Compact JSON would marginally obscure these values from a casual viewer but would not prevent a determined attacker from parsing it.

**Reasoning:** The real protection is AES-GCM encryption of the private key; the readable JSON metadata reduces the time to set up an attack but does not enable the attack itself without the password.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 191

---

**Q88. In `f03_decrypt_file.py`, the guard `if len(ciphertext) < 16` checks that there are at least 16 bytes of ciphertext. Why is 16 bytes the minimum: what does it correspond to, and what error would occur without this check if the file were truncated?**

**Answer:** 16 bytes corresponds to the GCM authentication tag length (128 bits). AES-GCM appends a 16-byte auth tag to the ciphertext; a valid ciphertext must be at least 16 bytes to contain the tag even if the original plaintext was empty. Without this check, `aesgcm.decrypt(iv, b"", None)` would raise an exception from the `cryptography` library (likely `ValueError: Invalid data`) with a potentially confusing error message rather than the user-friendly "SFFS file too small — possibly corrupted" message raised by the guard.

**Reasoning:** The 16-byte minimum is a format invariant: zero-byte plaintext produces exactly a 16-byte ciphertext (the GCM tag alone); anything shorter is definitionally malformed.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 192

---

**Q89. In `f01_generate_key_pairs.py`, the module uses `from cryptography.hazmat.primitives.serialization import (PrivateFormat, NoEncryption, PublicFormat)`. The `hazmat` prefix stands for "Hazardous Materials." What does this naming convention signal to developers about using these primitives?**

**Answer:** The `hazmat` ("Hazardous Materials") namespace in the `cryptography` library signals that these are low-level cryptographic primitives that are easy to misuse — they expose raw RSA operations, key serialisation formats, and cipher modes without automatic safety guards. Developers using `hazmat` APIs are expected to understand the underlying cryptography well enough to use them safely; mistakes (wrong padding, reused nonces, improper key handling) will not be caught by the library itself. The naming is an explicit warning that higher-level APIs (like `cryptography.fernet`) should be preferred when possible.

**Reasoning:** The `hazmat` convention is an API design choice by the `cryptography` library authors to signal expert-only usage; the SFFS code uses it knowingly to access the specific serialisation formats needed.

**Reference:** `code1/f01_generate_key_pairs.py` ~line 35

---

**Q90. In `f06_secure_key_storage.py`, the `unwrapAESKey()` function first tries to detect a JSON envelope by checking `blob.startswith(b"{")`. If the input is raw RSA-encrypted bytes that happen to start with `{` (ASCII 123), this check could incorrectly try to parse them as JSON. What defense does the code have against this ambiguity, and is it sufficient?**

**Answer:** The defense is the `json.loads()` call itself — if the bytes are random RSA ciphertext that happens to start with `{`, the JSON parser will almost certainly fail with `json.JSONDecodeError`, and the code will fall through to treat the input as raw RSA bytes. However, the exception from `json.loads()` is not caught in the detection logic (`blob.startswith(b"{")` branch directly calls `env = json.loads(...)`), so a `json.JSONDecodeError` would propagate up and crash `unwrapAESKey()` unexpectedly. A more robust check would wrap the `json.loads` in a `try/except json.JSONDecodeError` and fall back to raw bytes handling.

**Reasoning:** The `startswith(b"{")` heuristic combined with uncaught `JSONDecodeError` is not fully sufficient; a random RSA byte starting with `{` would cause an unhandled exception rather than graceful fallback.

**Reference:** `code1/f06_secure_key_storage.py` → `unwrapAESKey()` ~line 376

---

**Q91. In `f04_generate_hash.py`, the `generateFileHash()` function always returns `"algorithm": "sha256"` regardless of which hash function was used. Is this accurate in all cases, and what downstream bug could this hardcoded string cause?**

**Answer:** `generateFileHash()` calls `generateHash(path)` without an algorithm argument, which defaults to `"sha256"`, so the hardcoded `"algorithm": "sha256"` string is always accurate for this specific function. However, the function's `"Note: Always uses SHA-256"` comment means it cannot be used to generate BLAKE2b or SHA-512 hashes — the hardcoded string would be correct but the caller has no way to request a different algorithm. A downstream bug would occur if a caller compared the output of `generateFileHash()` against a hash stored in an `.sffs` file that was originally hashed with SHA-512 or BLAKE2b — the `"algorithm"` field would misleadingly say `"sha256"` but the comparison would always fail.

**Reasoning:** The hardcoded string is technically accurate for the current implementation but makes the function misleading if someone later adds an algorithm parameter without updating the return dict.

**Reference:** `code1/f04_generate_hash.py` → `generateFileHash()` ~line 134

---

**Q92. In `f05_verify_hash.py`, the module imports `from f04_generate_hash import generateHash` using a relative module name without a package prefix. What Python path requirements does this impose, and how might this import fail in certain deployment scenarios?**

**Answer:** This import requires that `code1/` is on `sys.path` at runtime — either the working directory is `code1/`, or `code1/` has been explicitly added to `sys.path`, or the modules are run as top-level scripts from within `code1/`. It would fail if `f05_verify_hash` is imported from the project root as `import code1.f05_verify_hash`, because then `from f04_generate_hash import` would look in the root-level `sys.path` and not find `f04_generate_hash` as a bare module. In the pytest test suite run from the project root, this import pattern requires a `conftest.py` or `pytest.ini` that adds `code1/` to `sys.path`.

**Reasoning:** Bare module imports without package prefixes are path-dependent; the SFFS `run_student1.py` and test infrastructure must explicitly manage `sys.path` to make these work.

**Reference:** `code1/f05_verify_hash.py` ~line 47

---

**Q93. In `f06_secure_key_storage.py`, the `secureKeyStorage()` function accepts a `kdf` parameter defaulting to `"ARGON2ID"`. A caller could pass `kdf="PBKDF2-SHA256"` to explicitly use the weaker KDF. Should this be protected with access controls or warnings, and what principle from secure API design is relevant here?**

**Answer:** The relevant principle is "secure by default" (or "fail safe defaults"): the API already implements this by defaulting to the stronger Argon2id. However, the weaker PBKDF2 option should emit a `warnings.warn()` deprecation/security warning when chosen, making the security implication visible to callers and future maintainers. Access control (preventing PBKDF2 selection entirely) would be more secure but breaks backward compatibility for legacy keystores. At minimum, callers should not be able to accidentally choose PBKDF2 without a visible indication that they are using a weaker option.

**Reasoning:** "Secure by default" means the safe option requires no action; unsafe options should require explicit, visible effort (not just a parameter change) to engage.

**Reference:** `code1/f06_secure_key_storage.py` → `secureKeyStorage()` ~line 129

---

**Q94. In `f02_encrypt_file.py` and `f03_decrypt_file.py`, the constants `SFFS_MAGIC = b"SFFS"` and `SFFS_VERSION = 0x03` are redefined in each module independently rather than being imported from a shared constants file. What software engineering problem does this duplication create, and what security bug could result if the constants diverge between the two files?**

**Answer:** This duplication creates a DRY (Don't Repeat Yourself) violation: if someone updates `SFFS_VERSION` in f02 to `0x04` but forgets to update f03, the encryption module writes version `0x04` but the decryption module only accepts `0x02` and `0x03`, causing all newly encrypted files to be unreadable with a "Unsupported SFFS version" error. The reverse — updating f03 to accept `0x04` without updating f02 — would not cause immediate errors but would silently leave all files at the old version, defeating the purpose of the upgrade. A shared `sffs_constants.py` module would eliminate both failure modes.

**Reasoning:** Duplicated constants in separate files are a maintenance anti-pattern; for security-critical format constants, divergence can silently break the encrypt-decrypt round trip.

**Reference:** `code1/f02_encrypt_file.py` ~line 66; `code1/f03_decrypt_file.py` ~line 63

---

**Q95. In `f01_generate_key_pairs.py`, the `generated_at` timestamp is included in the returned dict but is NOT stored inside the public key PEM file or the keystore. Where is this metadata expected to be stored, and what auditing gap exists if it is not persisted?**

**Answer:** The `generated_at` timestamp is returned to the caller (`sffs_core.py`) but is not written to the keystore JSON (which stores `created_at` for the keystore itself, not for the key pair). It is expected to be logged to the audit log by the caller, but if `secureKeyStorage()` or `encryptFileOperation()` does not explicitly log the key generation event with the timestamp, that metadata is lost. The auditing gap is that there is no persistent record of when a specific key pair was generated — an investigator cannot determine the key's age, whether it was generated before or after a suspected compromise event, or how long it has been in use.

**Reasoning:** Key generation timestamps are critical audit metadata for incident response; losing them makes it impossible to answer "was this key generated before or after the breach?"

**Reference:** `code1/f01_generate_key_pairs.py` → `generateKeyPairs()` ~line 120

---

**Q96. In `f06_secure_key_storage.py`, the `wrapAESKey()` function streams the `.sffs` file in 8 MB chunks when computing the `bound_file_mac`. Why must the same streaming approach be used in `unwrapAESKey()` when recomputing the hash for verification, and what would happen if `unwrapAESKey()` used `read_bytes()` on a large file?**

**Answer:** The streaming approach in `wrapAESKey()` computes `SHA256` over the same byte sequence as `unwrapAESKey()`'s streaming computation — both produce the same 32-byte digest for any file size. If `unwrapAESKey()` used `read_bytes()` on a 3 GB `.sffs` file (hypothetically, since f03 limits to 2 GB), it would allocate 3 GB of RAM during key verification alone, likely triggering OOM. More practically, for any file near or above available RAM, `read_bytes()` would cause memory pressure, swap usage, or a `MemoryError`, preventing successful key unwrapping and thus blocking decryption.

**Reasoning:** `unwrapAESKey()` already uses the same streaming pattern (lines 405-408 with `8 * 1024 * 1024` chunks), ensuring consistency; switching to `read_bytes()` would introduce an asymmetric memory requirement not present during wrapping.

**Reference:** `code1/f06_secure_key_storage.py` → `unwrapAESKey()` ~line 405

---

**Q97. In `f03_decrypt_file.py`, the function takes a keyword-only argument `expected_token: bytes | None = None` (after the `*` in the signature). What Python syntax makes this argument keyword-only, and why is it semantically important to enforce keyword-only usage for a security-sensitive parameter like `expected_token`?**

**Answer:** The bare `*` in the function signature (`def decryptFile(sffs_path, aes_key, output_dir=None, *, expected_token=None)`) makes all arguments after the `*` keyword-only — they cannot be passed positionally. This is semantically important because positional argument passing relies on argument order, and it is easy to accidentally pass the wrong value (e.g., pass a `bytes` output_dir argument that silently ends up in `expected_token` position in a positional call). Requiring `expected_token=<value>` makes the caller explicitly name this security-sensitive parameter, reducing the chance of accidental bypass.

**Reasoning:** Keyword-only enforcement is a defensive API design technique for security-critical parameters where accidental positional passing could silently skip or misuse the check.

**Reference:** `code1/f03_decrypt_file.py` → `decryptFile()` ~line 72

---

**Q98. In `f02_encrypt_file.py`, `secrets.token_bytes(32)` generates the `file_token`. The `secrets` module's documentation guarantees cryptographic randomness. If an attacker can predict the token (e.g., on a system with a compromised RNG), what specific attack does this enable given that the provenance table is the security mechanism?**

**Answer:** If the attacker can predict the 32-byte token for a given file, they can register it themselves in a forged provenance table (or present a file to the decryption pipeline with the predicted token as the header value). More critically, a predictable token means the attacker can enumerate all possible tokens for all files encrypted in a session, find which tokens are registered in the provenance table, and thereby construct files that pass provenance verification without actually being encrypted by the legitimate SFFS instance. The entire "token in provenance table = authentic source" guarantee collapses.

**Reasoning:** Provenance security depends entirely on the token being unpredictable to an attacker; if the token is predictable, the provenance table provides no security benefit.

**Reference:** `code1/f02_encrypt_file.py` → `encryptFile()` ~line 121

---

**Q99. In `f06_secure_key_storage.py`, the full module-level import `import hashlib` appears twice: once at the top of the file (line 68) and once again just before `hashlib_sha256_sandwich()` (line 200). What does this duplicate import reveal about the history of the code, and what Python behavior makes this harmless (rather than re-executing the module)?**

**Answer:** The duplicate `import hashlib` at line 200 reveals that `hashlib_sha256_sandwich()` was likely added later as a patch — the developer inserted it near the function definition rather than checking the existing module-level imports. Python's import system caches loaded modules in `sys.modules`; a second `import hashlib` simply looks up the existing cached module object and rebinds the name in the local namespace — it does not re-execute `hashlib`'s module code, so there is no performance cost, no side effect, and no error. The duplicate is purely a code-cleanliness issue, not a functional or security problem.

**Reasoning:** Python's module caching (`sys.modules`) makes duplicate imports a no-op after the first import; this is well-documented behavior and explains why the code works correctly despite the redundancy.

**Reference:** `code1/f06_secure_key_storage.py` ~line 68 and ~line 200

---

**Q100. In `f06_secure_key_storage.py`, the `ARGON2_TIME_COST = 3`, `ARGON2_MEMORY_COST = 65536`, `ARGON2_PARALLELISM = 4` match the OWASP 2023 recommendations from `f09_authenticate_user.py`. Why is it significant that both Student 1 (key storage) and Student 2 (user authentication) use the same Argon2id parameters, and what consistency risk exists if they are independently tuned in the future?**

**Answer:** Using the same parameters ensures that the security cost of authenticating a user equals the security cost of wrapping their key — an attacker who brute-forces the authentication password faces the same computational barrier as one who attacks the key storage directly, preventing the weaker of the two from becoming the preferred attack vector. The consistency risk is that if Student 1 tunes `ARGON2_MEMORY_COST` to 32768 KiB for performance while Student 2 keeps it at 65536 KiB, the key storage becomes the weak link (2x easier to brute-force) — an attacker would target f06 keystores instead of f09 authentication. Independent tuning without a shared constants module or policy document will inevitably cause this divergence over time.

**Reasoning:** Security parameters across authentication and key storage must be co-designed; divergence creates an asymmetric attack surface where the weaker system is targeted first.

**Reference:** `code1/f06_secure_key_storage.py` ~line 76; `code2/f09_authenticate_user.py` (Argon2id parameters)

---
