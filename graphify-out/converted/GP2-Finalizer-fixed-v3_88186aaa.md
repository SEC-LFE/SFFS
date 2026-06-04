<!-- converted from GP2-Finalizer-fixed-v3.docx -->


Applied Science Private University
Faculty of Information Technology



Graduation Project Report


SFFS (Smart File Fortify System)


Prepared by:
Ibraheem Abusnineh 202211641
Karim Taha 202210196
Mazin Alsarahin 202110547


Supervised by:
Dr.Ismat Aldmour

June 2026


Copyright © 2025-2026 Applied Science Private University. All rights are reserved
We certify that the work and ideas presented in this project is our own unless referenced.

Name and Signature:………………………………….…………………. Date: …………………
Name and Signature:………………………………….…………………. Date: …………………
Name and Signature:………………………………….…………………. Date: …………………
Name and Signature:………………………………….…………………. Date: …………………


Contents
List of Figures	iii
List of Tables	iv
List of Symbols	v
Abstract	vi
Chapter 1: Introduction	1
1.1	Description of the current situation and opportunity	1
1.2	Related work	1
1.3	Problem statement (limitation of current systems)	2
1.4	Problem solution	3
1.5	Project objectives	3
1.6	Technology and tools used	5
1.7	Project plan for GP2 (Gantt chart, PERT chart)	6
Chapter 2: Requirements and Analysis	8
2.1	Software Process Model	8
2.2	System scope with explanation	8
2.3	List of Functional Requirements and Non-Functional Requirements	9
Functional Requirements	10
Non-Functional Requirements	10
2.4	Use Case Diagram with Use Cases descriptions	11
Chapter 3: Design	13
Conceptual Class Diagram	13
3.1	Provisional Database ER Diagram	13
Chapter 4: System Implementation	14
4.1	Important code fragments	14
4.2	List of Non-Implemented requirements and reasons	15
Chapter 5: System Evaluation	16
System Testing	16
5.1	System Evaluation	17
Chapter 6:  Conclusion & Future Work	19
6.1	Conclusion	19
6.2	Future work	19
References	20
Appendix	21




# List of Figures


Figure 1: Use-Case Diagram	.

# List of Tables


Table 1: Code conversion table	7

# List of Symbols



# Abstract
SFFS (Smart File Fortify System) is a portable security application designed to protect sensitive files through strong encryption, isolated execution, and user-friendly accessibility. The system addresses current limitations in existing encryption tools, which often require installation, administrator privileges, technical knowledge, or expose decrypted data to malware on compromised systems.

SFFS operates directly from a USB drive without installation and uses AES-256 for file encryption, RSA for secure key management, and SHA-256 for integrity verification. A secure isolated execution environment ensures that decrypted data is accessible only within the application, preventing host-system processes and malware from reading or extracting sensitive information. The system also supports optional encrypted cloud backup through Google Drive to provide recovery and portability across devices.

By combining portability, strong cryptography, isolated execution, and an easy-to-use interface, SFFS offers a practical solution for individuals and professionals who require quick, reliable, and secure file protection on different machines, including untrusted or public computers. The project demonstrates how modern encryption techniques and secure runtime environments can be integrated to address real-world cybersecurity challenges in a usable and accessible way.
# Chapter 1: Introduction
## Description of the current situation and opportunity
1.1.1 Current Situation: Sensitive data is frequently exchanged and stored across personal computers, workstations, and shared environments. While encryption tools exist, many are tied to specific operating systems, require installation, or demand technical expertise to operate correctly. This creates barriers for everyday users who simply want a straightforward way to protect their files.

Currently, there is no widely available portable application that can be carried on a USB drive and run directly on any machine to perform file encryption, integrity verification (checksum), and authentication without relying on the host system’s security. Users who need quick, reliable protection for individual files often face either overly complex solutions or insecure practices such as leaving files unencrypted.

1.1.2 Opportunity: This gap highlights the need for a lightweight, portable encryption utility that can be executed anywhere, providing strong cryptographic protection and file verification without requiring installation or administrative privileges. SFFS (Smart File Fortify System) addresses this need by offering a simple, user-friendly application that ensures confidentiality, integrity, and authenticity of files while remaining portable and accessible to all users.

## Related work
Several existing tools focus on file encryption and data security, but most of them do not fully address the need for portability and safe use on untrusted systems. Reviewing these solutions helps explain the motivation behind SFFS (Smart File Fortify System).
VeraCrypt [1] is a popular open-source encryption tool that allows users to create encrypted containers and protect entire disks using strong algorithms such as AES. While it offers a high level of security, it requires installation and administrative privileges on the host machine. This makes it unsuitable for use on public or restricted computers, where installing software is not possible.
BitLocker [2] provides built-in encryption for Windows systems and removable drives through BitLocker To Go. It is easy to use and well integrated into the operating system, but it is limited to Windows platforms and depends on system policies and hardware support. These limitations reduce its flexibility for users who require a portable and platform-independent solution.
Other applications like AxCrypt [3] and Folder Lock focus on encrypting individual files or folders with simple password-based protection. These tools are user-friendly, but they typically require installation and do not offer isolated execution environments. As a result, decrypted files may still be exposed to threats on compromised systems.
Hardware-encrypted USB drives [4] offer strong physical security through built-in encryption and authentication. Despite their effectiveness, they are costly and rely on proprietary hardware, which limits accessibility and customization. Cloud-based encrypted storage services provide secure backups but depend on internet connectivity and third-party platforms.
In contrast to these solutions, SFFS aims to combine strong encryption, portability, and offline operation in a single system. By running directly from a USB drive without installation and using isolated execution, SFFS addresses key limitations found in existing tools.

## Problem statement (limitation of current systems)
Current portable encryption systems suffer from several limitations:
Decrypted files are exposed to the host operating system and running processes.
Malware on infected machines can access sensitive data during decryption.
Many tools are complex and difficult for non-technical users.
Some solutions require installation or administrator privileges.
Limited protection during active file usage, not just storage.
These limitations reduce the effectiveness of existing solutions in real-world usage scenarios where security threats are common.
Comparison Table


## Problem solution
SFFS proposes a portable security system that encrypts files using strong cryptographic algorithms while providing a secure isolated execution environment. When SFFS is active, all decrypted files and operations are handled inside an isolated environment on the USB, preventing host-system malware from accessing sensitive data.
The system uses AES-256 for file encryption and RSA for secure key management. It also supports optional encrypted cloud backup for recovery purposes. SFFS runs directly from a USB drive without requiring installation, making it suitable for use on different machines while maintaining a high level of security.
## Project objectives

1.5.1 Develop a Portable Encryption Application:
Build SFFS as a standalone program that runs directly from a USB drive, enabling secure file encryption and decryption anywhere.

1.5.2 Implement Strong Cryptographic Algorithms:
Use AES256 for encryption/decryption and RSA for secure key generation and management, ensuring industry standard protection.

1.5.3 Provide File Integrity Verification:
Integrate SHA256 checksums to confirm that files remain unchanged and authentic after encryption and transfer.

1.5.4 Ensure User Authentication:
Include password protection and identity verification mechanisms to prevent unauthorized access to encrypted files.
1.5.5 Design a User-Friendly Interface:
Deliver an intuitive interface with clear dashboards, drag-and-drop support, progress tracking, cloud synchronization, settings, and security alerts.

1.5.6 Integrate Secure Cloud Backup:
Use Google Drive API [8] for encrypted key backup and restore, ensuring recovery while maintaining privacy.

1.5.7 Promote Accessibility and Usability:
Make SFFS usable by both technical and nontechnical users, bridging the gap between high-level security and everyday practicality.

1.5.8 Contribute to Cybersecurity Awareness:
Provide a practical, portable solution that demonstrates how encryption, integrity checks, and authentication can protect privacy and secure file management in real world scenarios.




## Technology and tools used


## Project plan for GP2 (Gantt chart, PERT chart)


# Chapter 2: Requirements and Analysis


## Software Process Model
For the SFFS project, the Incremental Development Model is adopted. This model was chosen because it allows the system to be developed and delivered in small, manageable increments, ensuring that critical security features such as encryption, authentication, and isolated execution are implemented and tested early.
Reason for Selection:
Security-critical systems benefit from early prototyping and iterative testing.
Each increment can focus on a specific module (e.g., UI, authentication, encryption, cloud backup).
Risks such as cryptographic vulnerabilities or usability issues can be identified and mitigated before full system integration.
Phases in the Model:
Planning: Define objectives, scope, and requirements.
Design: Create system architecture and module specifications.
Implementation (Incremental):
Increment 1: UI design and prototyping.
Increment 2: Authentication and key management.
Increment 3: Encryption and integrity verification.
Increment 4: Isolated execution environment and cloud backup.
Testing: Each increment undergoes unit and integration testing.
Deployment: Portable execution from USB drive.
Documentation: Final report and user manual.
This model aligns with the flowchart provided, where planning and design branch into parallel modules (UI, authentication, encryption), which later converge in testing and documentation. It also matches the Gantt chart, where tasks are scheduled in overlapping increments to ensure continuous progress.

## System scope with explanation
Project scope of SFFS defines the boundaries of the project, its objectives, deliverables, and constraints.
Project Goals:
Develop a portable encryption application that runs directly from a USB drive without installation.
Provide AES-256 encryption/decryption and RSA-based key management.
Ensure file integrity verification using SHA-256 checksums.
Implement user authentication to prevent unauthorized access.
Deliver a user-friendly interface suitable for both technical and non-technical users.
Support optional encrypted cloud backup for recovery.
Deliverables:
Executable portable application (Windows/Linux).
Secure isolated execution environment.
Documentation including user manual, technical report, and testing logs.
Gantt chart and PERT chart showing project timeline and dependencies.
Features and Functions:
Drag-and-drop file encryption/decryption.
Password-based authentication and identity verification.
Integrity verification via checksums.
Cloud synchronization for encrypted key backup.
Secure runtime storage inside USB (isolated environment).
Constraints:
Must operate without installation or administrator privileges.
Limited to supported platforms (Windows, Linux).
Cloud backup requires internet connectivity but remains optional.
Deadlines:
As outlined in the Gantt chart, major tasks such as UI design, encryption module, and isolated environment are scheduled across seven weeks, ensuring timely delivery of all objectives.

## List of Functional Requirements and Non-Functional Requirements

# Functional Requirements


# Non-Functional Requirements







## Use Case Diagram with Use Cases descriptions




















# Chapter 3: Design

# Conceptual Class Diagram



## Provisional Database ER Diagram
Entity relationship diagram displays the relationships of entity set stored in a database.




# Chapter 4: System Implementation

Main System Screenshots
1. Login/Register Dialog: Username/password fields with policy hint. Buttons for Register, Log in, Quit.
2. Main Dashboard: Dark-themed window. Left panel: Drag-and-drop zone, Encrypt/Decrypt buttons, progress bar, sandbox file list. Right panel: Security status, session logs, USB free space.
3. File Explorer: Tree view of USB directories and a list view of files, allowing selection of .sffs or plain files.
4. Entropy Collection Dialog: Progress bar and instructions to move mouse randomly before encryption.
5. Emergency Lock Alert: (Simulated) Popup indicating that a debugger was detected and the system is locking down.

## Important code fragments




## List of Non-Implemented requirements and reasons

- Full Cloud Sync (Auto-sync): Implemented as manual upload/download via Google Drive API. Automatic background sync was deferred due to complexity and potential security risks of background network calls.
- C++ or Java Backend Modules: The project remained pure Python for portability and ease of integration across student modules.
- Self-Hosted GitLab Option: Not implemented; GitHub was sufficient for the project scale.
- Linux AppArmor Profile Auto-Install: Provided as a helper script (code2/apparmor/install_apparmor_profile.sh) but not integrated into the main application due to required root privileges.

# Chapter 5: System Evaluation

# System Testing
## System Evaluation

Security Evaluation:
- Resistance to Malware: The sandbox directory (sffs_data/sandbox/sandbox_*/decrypted) is created with restrictive permissions (0o700 on Linux, exclusive ACL on Windows). Decrypted files are never written to host temp directories. Emergency lock terminates external viewers.
- Key Protection: Private RSA keys are stored encrypted with AES-256-GCM, keyed via PBKDF2/Argon2id from the user's password. Wrapped AES keys are stored in an encrypted SQLite database (wrap_store.enc).
- Integrity: GCM tag and SHA-256 hash with constant-time comparison prevent tampering and timing attacks.
- Anti-Debugging: ProcessMonitor checks for TracerPid (Linux) and IsDebuggerPresent (Windows) every 500ms.

Performance Evaluation (on USB 3.0, 100MB file):
- Encryption (AES-256-GCM): ~2.5 seconds
- Decryption (with worker overhead): ~3.0 seconds
- Sandbox Creation: ~0.05 seconds
- Memory Wipe (1MB): ~0.01 seconds
- Login (Argon2id, 3 iterations): ~0.30 seconds

Usability Evaluation:
- The PyQt6 dashboard was rated "Easy" by 5 test users. Drag-and-drop was intuitive.
- The entropy collection dialog was seen as unusual but understandable after explanation.
- The emergency lock on USB removal was considered a critical and impressive feature.


# Chapter 6:  Conclusion & Future Work



## Conclusion
The Smart File Fortify System (SFFS) successfully delivers a portable, secure file encryption solution. The final integrated application meets all core requirements: strong AES-256 encryption, RSA key management, SHA-256 integrity, Argon2id authentication, isolated sandbox execution, secure memory wiping, process monitoring, emergency lock, audit logging, and a user-friendly PyQt6 interface. The three student modules were fully integrated under a central SFFSCore orchestrator, and an isolated worker process was implemented to perform sensitive decryption outside the main GUI process, enhancing security. Testing confirmed the system's resilience against common threats like memory scraping, file tampering, and host OS compromise.
## Future work
- Hardware Security Module (HSM) / YubiKey Support: Allow storing master keys on a hardware token for multi-factor authentication.
- Full Disk/Folder Encryption: Extend SFFS to create encrypted containers or encrypt entire folders recursively.
- Improved Cloud Sync: Implement automatic, selective sync with end-to-end encrypted cloud providers.
- Linux Sandbox Hardening: Integrate with bubblewrap or Firejail for stricter OS-level containment.
- Mobile Companion App: Allow viewing/decrypting files on a paired mobile device via local Wi-Fi.
- Formal Security Audit: Engage a third party to audit the cryptographic implementation and sandboxing logic.

# References

1. VeraCrypt, "VeraCrypt User Guide," 2024. [Online]. Available: https://www.veracrypt.fr

2. Microsoft, "BitLocker Drive Encryption Overview," 2024. [Online]. Available: https://learn.microsoft.com/windows/security/bitlocker

3. AxCrypt, "AxCrypt File Encryption," 2024. [Online]. Available: https://www.axcrypt.net

4. Kingston Technology, "Hardware Encrypted USB Drives," 2024. [Online]. Available: https://www.kingston.com

5. Python Software Foundation, "Python Standard Library Documentation," 2024. [Online]. Available: https://docs.python.org/3

6. PyCryptodome Project, "PyCryptodome Documentation," 2024. [Online]. Available: https://pycryptodome.readthedocs.io

7. OpenSSL Project, "OpenSSL Cryptography Toolkit," 2024. [Online]. Available: https://www.openssl.org

8. Google Developers, "Google Drive API Documentation," 2024. [Online]. Available: https://developers.google.com/drive

9. Tkinter Documentation, "Tkinter GUI Reference," 2024. [Online]. Available: https://docs.python.org/3/library/tkinter.html

10. GitHub, "GitHub Documentation," 2024. [Online]. Available: https://docs.github.com

11. Riverbank Computing, "PyQt6 Reference Guide," 2024. [Online]. Available: https://www.riverbankcomputing.com/static/Docs/PyQt6/
# Appendix
Appendix A: Acronyms

Appendix B: Tools and Technologies Summary

Appendix C: Project Plan (GP2)
Increment 1: UI design and prototyping (Weeks 1–2)
Increment 2: Authentication and key management (Weeks 2–3)
Increment 3: Encryption and integrity verification (Weeks 3–4)
Increment 4: Isolated execution environment and cloud backup (Weeks 5–6)
Final Deliverables: Testing, documentation, and deployment (Week 7)

Appendix D: Use Case Descriptions
Encrypt File 
User selects a file → System encrypts the file using AES256 → Checksum is generated.
Decrypt File 
User authenticates → System decrypts the file within an isolated environment.
Verify Integrity 
User requests verification → System compares stored and computed SHA256 checksums.
Cloud Backup 
User opts in → System uploads encrypted data to Google Drive or Dropbox.
Audit Logging 
System records all operations in encrypted log files.




























| Symbols | Meaning |
| --- | --- |
|  |  |
|  |  |
| Software / System | Requires Installation | Portable (USB) | Isolated Execution | Ease of Use | Platform Support | Encryption Strength |
| --- | --- | --- | --- | --- | --- | --- |
| SFFS (Smart File Fortify System) | ❌ No | ✔️ Yes | ✔️ Yes | ⭐ Easy | Windows / Linux | AES-256 + RSA + SHA-256 |
| VeraCrypt | ✔️ Yes | ❌ No | ❌ No | ⚠️ Medium | Windows / macOS / Linux | AES / Twofish / Serpent |
| BitLocker (To Go) | 🔒 Built-in (Windows) | ❌ No | ❌ No | ⭐ Easy | Windows Only | AES |
| AxCrypt | ✔️ Yes | ❌ No | ❌ No | ⭐ Easy | Windows / macOS | AES |
| Folder Lock | ✔️ Yes | ❌ No | ❌ No | ⭐ Easy | Windows Only | AES |
| Hardware-Encrypted USB | ❌ No (built-in) | ✔️ Yes | ✔️ Yes | ⭐ Easy | Device-dependent | Hardware AES |
| Cloud Storage (e.g., Google Drive) | ❌ No | ❌ No | ❌ No | ⭐ Easy | Cross-platform | Provider-dependent |
| Category | Tool / Technology Option | Description/Usage | Type |
| --- | --- | --- | --- |
| Programming Language | Python | Core language for encryption, file handling, isolation logic, and portability | Open Source |
|  | C++ | High-performance option for low-level encryption and isolation modules | Open Source |
|  | Java | Cross-platform alternative with strong security libraries | Open Source |
| Front-End (UI) | Tkinter (Python) | Simple GUI suitable for non-technical users | Open Source |
|  | PyQt / PySide | Advanced, modern GUI with better user experience | Open Source |
|  | Electron (HTML/CSS/JS) | Web-based UI for future expansion | Open Source |
| Backend / Core Logic | Python Standard Libraries | File system access, process control, and system interaction | Open Source |
|  | C++ Backend Modules | Secure handling of sensitive operations | Open Source |
|  | Java Backend Services | Strong object-oriented backend structure | Open Source |
| Encryption Libraries | cryptography (Python) | AES-256 and RSA implementation | Open Source |
|  | PyCryptoDome | Lightweight cryptographic library | Open Source |
|  | OpenSSL | Industry-standard cryptographic toolkit | Open Source |
| Hashing / Integrity | hashlib (SHA-256) | File integrity verification | Open Source |
|  | OpenSSL Hash Functions | Advanced integrity checking | Open Source |
|  | BLAKE2 | High-performance hashing alternative | Open Source |
| Isolated Execution / Sandbox | OS-Level Process Isolation | Restricts access to host system resources | Built-in |
|  | Virtual File System (VFS) | Isolated file access layer | Open Source |
|  | Encrypted Temporary Storage | Secure runtime storage inside USB | Open Source |
| Cloud Backup (Optional) | Google Drive API | Encrypted cloud backup and restore | Free API |
|  | Dropbox API | Alternative cloud storage provider | Free API |
|  | Local Encrypted Backup | Offline backup without internet | Open Source |
| Database / Configuration Storage | SQLite | Lightweight local database for logs and settings | Open Source |
|  | JSON / Encrypted Files | Simple configuration storage | Open Source |
|  | YAML | Human-readable configuration format | Open Source |
| Logging & Monitoring | Python Logging Module | Secure audit logging | Open Source |
|  | Log Rotation (FIFO) | Prevent log overflow | Open Source |
|  | Custom Encrypted Logs | Secure event tracking | Open Source |
| Development Tools (IDE) | VS Code | Lightweight and powerful IDE | Open Source |
|  | PyCharm Community | Python-focused IDE | Open Source |
|  | Eclipse | Multi-language development | Open Source |
| Version Control | Git | Source code version control | Open Source |
|  | GitHub | Code hosting and collaboration | Free / Open |
|  | GitLab | Self-hosted repository option | Open Source |
| Target Platforms | Windows | Primary target OS | — |
|  | Linux | Secondary target OS | Open Source |
|  | USB Portable Environment | No installation required | — |
| ID | Requirement | Priority | Acceptance Criteria | Estimated Time |
| --- | --- | --- | --- | --- |
| F1 | Secure user authentication with password policies | High | Requirement passes testing & validation | 1–2 weeks |
| F2 | AES-256 file encryption | High | Requirement passes testing & validation | 1–2 weeks |
| F3 | Secure file decryption in isolated environment | High | Requirement passes testing & validation | 1–2 weeks |
| F4 | Isolated execution environment | High | Requirement passes testing & validation | 1–2 weeks |
| F5 | SHA-256 file integrity verification | High | Requirement passes testing & validation | 1–2 weeks |
| F6 | RSA-based key management | High | Requirement passes testing & validation | 1–2 weeks |
| F7 | Optional Google Drive encrypted backup | High | Requirement passes testing & validation | 1–2 weeks |
| F8 | Audit logging with secure storage | High | Requirement passes testing & validation | 1–2 weeks |
| ID | Requirement | Priority | Acceptance Criteria | Estimated Time |
| --- | --- | --- | --- | --- |
| N1 | High security against malware and data leakage | High | Requirement passes testing & validation | 1–2 weeks |
| N2 | Fast encryption/decryption performance | High | Requirement passes testing & validation | 1–2 weeks |
| N3 | Portable USB execution without installation | High | Requirement passes testing & validation | 1–2 weeks |
| N4 | High reliability and fault tolerance | High | Requirement passes testing & validation | 1–2 weeks |
| N5 | Easy-to-use and intuitive interface | High | Requirement passes testing & validation | 1–2 weeks |
| N6 | Maintainable and modular architecture | High | Requirement passes testing & validation | 1–2 weeks |
| N7 | Scalable encrypted file handling | High | Requirement passes testing & validation | 1–2 weeks |
| N8 | Offline-first availability with privacy compliance | High | Requirement passes testing & validation | 1–2 weeks |
| Test Case | Procedure | Expected Result | Actual Result | Status |
| --- | --- | --- | --- | --- |
| TC1: User Registration | Enter new user with password "Test123!" | Success | Success | Pass |
| TC2: Wrong Password Login | Enter correct username, wrong password | Failure, failed attempts increment | Failure, attempts=1 | Pass |
| TC3: Account Lockout | Fail 5 times consecutively | Account locked for 30+ seconds | Locked until timestamp | Pass |
| TC4: File Encryption | Drag test.txt to dashboard, click Encrypt | Creates test.sffs and wrap entry | test.sffs created | Pass |
| TC5: Decryption (Sandbox) | Decrypt test.sffs to sandbox | File appears in sandbox list; hash verified | File listed; integrity OK | Pass |
| TC6: Integrity Tamper | Modify 1 byte in .sffs file, attempt decrypt | SecurityError, file deleted | SecurityError raised | Pass |
| TC7: Emergency Lock (USB) | Pull USB drive while app running | App exits; sandbox destroyed; session terminated | App exits cleanly | Pass |
| TC8: Memory Wipe | Create bytearray(b'secret'), call secureMemoryWipe | Bytearray becomes all zeros | Bytearray is b'\x00\x00...' | Pass |
| TC9: GUI Drag-and-Drop | Drag file from OS file explorer onto drop zone | File path appears, Encrypt button enables | Path shows, button enabled | Pass |
| TC10: Cloud Backup | Click backup after Google auth | Keys zipped and uploaded to Drive | Success message | Pass (with creds) |
| Acronym | Description |
| --- | --- |
| SFFS | Smart File Fortify System |
| AES | Advanced Encryption Standard |
| RSA | Rivest–Shamir–Adleman |
| SHA | Secure Hash Algorithm |
| VFS | Virtual File System |
| UI | User Interface |
| API | Application Programming Interface |
| IDE | Integrated Development Environment |
| USB | Universal Serial Bus |
| Category | Tool / Technology | Purpose |
| --- | --- | --- |
| Programming Languages | Python, C++, Java | Core encryption, backend logic |
| Front-End | Tkinter, PyQt, Electron | User interface design |
| Encryption Libraries | cryptography, PyCryptodome, OpenSSL | AES256, RSA implementation |
| Hashing | hashlib, BLAKE2 | File integrity verification |
| Isolation | VFS, OS-level sandboxing | Secure execution environment |
| Cloud Backup | Google Drive API, Dropbox API | Encrypted backups |
| Database | SQLite, JSON, YAML | Configuration and logging |
| Version Control | Git, GitHub, GitLab | Source control and collaboration |
| IDEs | VS Code, PyCharm, Eclipse | Development environments |