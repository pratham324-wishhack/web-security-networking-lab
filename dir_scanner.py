import urllib.request
import urllib.error

target = "http://127.0.0.1:8000"
print(f"Starting Directory Scan on {target}...\n")

with open("wordlist.txt", "r") as file:
    for line in file:
        word = line.strip()  # Extra spaces aur newline (\n) hatane ke liye
        url = f"{target}/{word}"
        
        try:
            response = urllib.request.urlopen(url)
            print(f"[+] FOUND (200 OK)        : /{word}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"[!] RESTRICTED (403)      : /{word}")
            # 404 Not Found ko ignore karenge taaki output clean rahe

