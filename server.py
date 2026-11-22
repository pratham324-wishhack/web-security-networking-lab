import html
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import subprocess
import re
import hashlib
import hmac
import os

# Initialize local SQLite database with Salted PBKDF2 hashed password
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("CREATE TABLE users (username TEXT, salt TEXT, password_hash TEXT)")

admin_salt = os.urandom(16)
admin_hash = hashlib.pbkdf2_hmac("sha256", b"SuperSecret@2026", admin_salt, 100000).hex()
cursor.execute(
    "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
    ("admin", admin_salt.hex(), admin_hash),
)
conn.commit()
conn.close()

class MyHandler(BaseHTTPRequestHandler):
    def version_string(self):
        return "SecureWebServer"

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        name = query.get("name", ["Guest"])[0]
        city = query.get("city", ["Unknown"])[0]
        print("CITY:", city)
        print("PATH:", path)
        print("QUERY:", query)
        if path == "/":
            raw_name = query.get("name", ["Guest"])[0]
            # Sanitize user input by escaping HTML special characters
            safe_name = html.escape(raw_name)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            response_html = f"<html><body><h1>Welcome, {safe_name}!</h1></body></html>"
            self.wfile.write(response_html.encode("utf-8"))
        elif path == "/about":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"This is the About Page")
        elif path == "/contact":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"This is the contact page")
        elif path == "/secret":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Secret Backup Key: LAB-9942")
        elif path == "/admin":
            self.send_response(403)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"403 - Access Denied: Admin Only")
        elif path == "/login":
            user = html.escape(query.get("user", ["Pratham"])[0])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            # Protect session cookie from JavaScript access (HttpOnly) and CSRF (SameSite)
            self.send_header("Set-Cookie", "session_id=TOKEN_PRATHAM_9012; Path=/; HttpOnly; SameSite=Strict")
            self.end_headers()
            msg = f"<html><body><h1>Logged in as {user}!</h1><p>Secure session cookie issued.</p></body></html>"
            self.wfile.write(msg.encode("utf-8"))
        elif path == "/dashboard":
            cookies = self.headers.get("Cookie", "")
            if "session_id=TOKEN_PRATHAM_9012" in cookies:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                msg = "<html><body><h1>Welcome to Your Private Dashboard</h1><p>Balance: Rs. 50,000</p></body></html>"
                self.wfile.write(msg.encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"401 Unauthorized - Valid session cookie required")
        elif path == "/search":
            # Intentionally unescaped input to demonstrate cookie theft via XSS
            term = query.get("q", [""])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            msg = f"<html><body><h1>Search results for: {term}</h1></body></html>"
            self.wfile.write(msg.encode("utf-8"))
        elif path == "/db-login":
            user = query.get("user", [""])[0]
            passwd = query.get("pass", [""])[0]

            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            sql_query = "SELECT username, salt, password_hash FROM users WHERE username = ?"

            try:
                cursor.execute(sql_query, (user,))
                account = cursor.fetchone()
            except sqlite3.Error as err:
                account = None
                print(f"[SQL ERROR] {err}")
            finally:
                conn.close()

            login_ok = False
            if account:
                stored_user, stored_salt_hex, stored_hash = account
                stored_salt = bytes.fromhex(stored_salt_hex)
                candidate_hash = hashlib.pbkdf2_hmac(
                    "sha256", passwd.encode("utf-8"), stored_salt, 100000
                ).hex()
                # Constant-time comparison prevents timing attacks
                login_ok = hmac.compare_digest(candidate_hash, stored_hash)

            if login_ok:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"200 OK - Secure Hashed Login Successful! Welcome, {stored_user}".encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"401 Unauthorized - Invalid username or password")
        elif path == "/ping":
            host = query.get("host", ["127.0.0.1"])[0]

            # LAYER 1 (Allowlisting): Only allow valid IP/hostname characters
            if not re.fullmatch(r"[a-zA-Z0-9.-]+", host):
                print(f"[SECURITY BLOCK] Rejected malicious host input: {host}")
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"400 Bad Request - Invalid host format")
                return

            # LAYER 2 (Code vs Data): Use argument list with shell=False
            cmd_list = ["ping", "-c", "1", host]
            print(f"[DEBUG CMD] Executing safely (shell=False): {cmd_list}")

            try:
                output = subprocess.check_output(cmd_list, shell=False, stderr=subprocess.STDOUT, timeout=5)
            except Exception as err:
                output = str(err).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(output)
        elif path == "/read":
            filename = query.get("file", ["welcome.txt"])[0]

            # LAYER 1 (Canonicalization): Resolve exact absolute paths
            base_dir = os.path.realpath("public")
            target_path = os.path.realpath(os.path.join(base_dir, filename))

            # LAYER 2 (Sandboxing): Ensure target_path stays strictly inside base_dir
            if os.path.commonpath([base_dir, target_path]) != base_dir:
                print(f"[SECURITY BLOCK] Path Traversal attempt blocked: {filename} -> {target_path}")
                self.send_response(403)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"403 Forbidden - Path Traversal blocked")
                return

            print(f"[DEBUG FILE] Safely reading inside sandbox: {target_path}")
            try:
                with open(target_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(content)
            except Exception as err:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"404 Not Found - {err}".encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 - Page Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        print("POST DATA:", post_data)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"POST received successfully")

server = HTTPServer(("127.0.0.1", 8000), MyHandler)

print("Server running at http://127.0.0.1:8000")

server.serve_forever()
