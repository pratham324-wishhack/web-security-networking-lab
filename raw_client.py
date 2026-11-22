import socket

# AF_INET = IPv4 address, SOCK_STREAM = TCP protocol
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8000))

# Query parameters ke saath raw HTTP GET request
request = b"GET /?name=hacker&city=jubbal HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
s.sendall(request)

# Poora TCP stream receive karne ke liye loop
response = b""
while True:
    chunk = s.recv(1024)
    if not chunk:  # Jab server connection band karega toh empty bytes b"" aayenge
        break
    response += chunk

s.close()
print(response.decode("utf-8"))

