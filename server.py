import socket
import os
import threading
import json

client_activities = {}
activities_lock = threading.Lock()
users = {}

def receive_file(connection, filename, username):
    with open(filename, 'wb') as file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
    with activities_lock:
        client_activities[username] = client_activities.get(username, {"upload": 0, "download": 0})
        client_activities[username]["upload"] += 1

def send_file(connection, filename, username):
    if os.path.isfile(filename):
        with open(filename, 'rb') as file:
                data = file.read(1024)
                while data:
                    connection.send(data)
                    data = file.read(1024)
        connection.send(b"File terkirim")
        print(f"{filename} berhasil diunduh oleh {username}")

        with activities_lock:
            client_activities[username] = client_activities.get(username, {"upload": 0, "download": 0})
            client_activities[username]["download"] += 1
    else:
        connection.send("File tidak ditemukan".encode('utf-8'))

def most_active_client(connection):
    with activities_lock:
        sorted_clients = sorted(client_activities.items(), key=lambda x: x[1]["upload"] + x[1]["download"], reverse=True)
        active_clients = [{"username": username, "activity": {"upload": data["upload"], "download": data["download"]}} for username, data in sorted_clients[:5]]
    connection.send(json.dumps(active_clients).encode('utf-8'))
    

def handle_client(connection, address):
    print(f"Terhubung dengan {address}")

    # Menerima perintah dari client
    username = connection.recv(1024).decode('utf-8')
    print(f"Menerima username {username} dari {address}")


    # Menerima perintah dari client setelah mendapatkan username
    command = connection.recv(1024).decode('utf-8')
    print(f"Command dari {username} ({address}): {command}")

    if command == "UPLOAD":
        # Menerima nama file dari client
        filename = connection.recv(1024).decode('utf-8')
        print(f"Menerima file {filename}...")
        receive_file(connection, filename, username)
        print(f"{filename} berhasil diunggah oleh {username}")        
    elif command == "DOWNLOAD":
        # Menerima nama file dari client
        filename = connection.recv(1024).decode('utf-8')
        print(f"Mengirim file {filename}...")
        send_file(connection, filename, username)
        print(f"{filename} berhasil diunduh oleh {username}")
    elif command == "GET_ACTIVE_CLIENTS":
        most_active_client(connection)
    else:
        print("Perintah tidak valid")

    connection.close()

def start_server():
    host = "127.0.0.2"
    port = 2121

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"FTP Server berjalan di {host}:{port}")

    while True:
        connection, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(connection, address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
