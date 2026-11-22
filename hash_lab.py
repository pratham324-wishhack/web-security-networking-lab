import hashlib
import os

password = "SuperSecret@2026"

# 1. Plain SHA-256 (Deterministic — same password ALWAYS gives same hash)
sha1 = hashlib.sha256(password.encode()).hexdigest()
sha2 = hashlib.sha256(password.encode()).hexdigest()

print("--- 1. Plain SHA-256 (Vulnerable to Rainbow Tables) ---")
print(f"User A Hash: {sha1}")
print(f"User B Hash: {sha2}")
print(f"Are hashes identical? {sha1 == sha2}\n")

# 2. Salted PBKDF2-HMAC-SHA256 (Unique random salt + 100,000 iterations)
salt_a = os.urandom(16)
salt_b = os.urandom(16)

pbkdf2_a = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_a, 100000).hex()
pbkdf2_b = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_b, 100000).hex()

print("--- 2. Salted PBKDF2 (100,000 iterations) ---")
print(f"User A Salt: {salt_a.hex()}")
print(f"User A Hash: {pbkdf2_a}")
print(f"User B Salt: {salt_b.hex()}")
print(f"User B Hash: {pbkdf2_b}")
print(f"Are hashes identical? {pbkdf2_a == pbkdf2_b}")
