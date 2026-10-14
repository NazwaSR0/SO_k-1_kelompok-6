import socket, json, time, os
from multiprocessing import Process, Pipe

HOST, PORT = "127.0.0.1", 5000
ANTRIAN = "antrian_offline.jsonl"   # antrean offline (data tertahan saat server mati)

def muat_antrian():
    if not os.path.exists(ANTRIAN):
        return []
    with open(ANTRIAN) as f:
        return [json.loads(l) for l in f if l.strip()]

def simpan_antrian(data):
    with open(ANTRIAN, "w") as f:
        for x in data:
            f.write(json.dumps(x) + "\n")

# Proses 1: menghasilkan data, mengirim lewat PIPE
def penyimpan(conn):
    print("Penyimpan  pid =", os.getpid())
    for i in range(1, 6):
        conn.send({"id": i, "data": f"catatan-{i}", "waktu": time.time()})
    conn.send(None)  # tanda selesai

# Proses 2: menerima dari PIPE, mengirim ke server lewat SOCKET
def pengirim(conn):
    print("Pengirim   pid =", os.getpid())
    buffer = []
    while True:
        item = conn.recv()
        if item is None:
            break
        buffer.append(item)

    semua = muat_antrian() + buffer      # antrean lama + data baru
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as s:
            s.sendall(("\n".join(json.dumps(x) for x in semua) + "\n").encode())
            s.shutdown(socket.SHUT_WR)   # beri tahu server: data selesai (EOF)
            balasan = s.recv(1024).decode()
            print("Balasan server:", balasan)
        if balasan == "ACK":
            if os.path.exists(ANTRIAN):
                os.remove(ANTRIAN)       # sukses -> antrean dihapus
    except OSError as e:
        simpan_antrian(semua)            # gagal -> simpan ke antrean offline
        print("Gagal kirim, data disimpan ke antrian offline:", e)

if __name__ == "__main__":
    print("Induk      pid =", os.getpid())
    a, b = Pipe()
    p1 = Process(target=penyimpan, args=(a,))
    p2 = Process(target=pengirim, args=(b,))
    p1.start(); p2.start()
    p1.join(); p2.join()
