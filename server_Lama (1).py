import socket, json

HOST, PORT = "127.0.0.1", 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server menunggu klien...")
    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(4096).decode()
            if not data:
                continue
            for line in data.strip().split("\n"):
                rec = json.loads(line)
                with open("server_db.jsonl", "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print("Diterima:", rec)
            conn.sendall(b"ACK")