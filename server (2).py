import socket, json

HOST, PORT = "127.0.0.1", 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Server menunggu klien...")
    while True:
        conn, addr = s.accept()
        with conn:
            chunks = []
            while True:
                part = conn.recv(4096)
                if not part:
                    break
                chunks.append(part)
            data = b"".join(chunks).decode()
            jumlah = 0
            for line in data.strip().split("\n"):
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    print("Baris rusak dilewati")
                    continue
                with open("server_db.jsonl", "a") as f:
                    f.write(json.dumps(rec) + "\n")
                jumlah += 1
            print("Diterima:", jumlah, "catatan")
            conn.sendall(b"ACK")