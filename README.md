# Web Security & Networking Lab (Python / Termux)

Hands-on security engineering repository built from scratch in Python (standard library) to understand web vulnerabilities, exploitation mechanics, and defense-in-depth remediation from first principles.

## Architecture & Tools

| File | Category | Purpose |
| :--- | :--- | :--- |
| `server.py` | Vulnerable & Patched HTTP Server | Custom HTTP server hardened against OWASP Top 10 flaws |
| `raw_client.py` | Networking | Raw TCP socket client for manual HTTP request crafting |
| `port_scanner.py` | Reconnaissance | TCP port scanner for service discovery |
| `banner_grabber.py` | Reconnaissance | Service banner grabbing and version fingerprinting |
| `dir_scanner.py` | Web Recon | Wordlist-based directory and endpoint enumerator (`wordlist.txt`) |
| `hash_lab.py` | Cryptography | Comparison of plain SHA-256 vs. Salted PBKDF2-HMAC-SHA256 |

## Security Controls Implemented in `server.py`

* **Reflected XSS:** Neutralized via output encoding (`html.escape()`) and Content Security Policy (CSP) headers.
* **SQL Injection (SQLi):** Remediated using parameterized queries (`?` placeholders + tuples) for strict code vs. data separation.
* **OS Command Injection (RCE):** Mitigated via defense-in-depth — Layer 1 Regex allowlisting (`re.fullmatch`) + Layer 2 `subprocess` argument lists with `shell=False`.
* **Cryptographic Storage:** Replaced plaintext passwords with per-user random salts (`os.urandom(16)`), PBKDF2-HMAC-SHA256 key stretching (`100,000` iterations), and constant-time verification (`hmac.compare_digest`).
* **Path Traversal / LFI:** Prevented using path canonicalization (`os.path.realpath`) and strict directory sandboxing (`os.path.commonpath`) confined to `public/`.

## Usage

```bash
python server.py

```
