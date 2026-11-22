import socket

target = "127.0.0.1"

for port in range(7999, 8002):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    
    if s.connect_ex((target, port)) == 0:
        print(f"[+] Port {port} is OPEN -> Grabbing banner...")
        s.sendall(b"HEAD / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        response = s.recv(1024).decode("utf-8", errors="ignore")
        
        for line in response.splitlines():
            if line.startswith("Server:"):
                print(f"    [!] Banner Found: {line}")
    else:
        print(f"[-] Port {port} is CLOSED")
        
    s.close()

