import socket

target = "127.0.0.1"
print(f"Scanning target: {target}...\n")

for port in range(65500, 65535):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)  # Max 0.5 second wait karega
    
    result = s.connect_ex((target, port))
    if result == 0:
        print(f"[+] Port {port} : OPEN")
    else:
        print(f"[-] Port {port} : CLOSED")
        
    s.close()

