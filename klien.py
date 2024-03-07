import socket
import os
import json

def upload_file(connection, filename, username):
    with open(filename, 'rb') as file:
        data = file.read(1024)
        while data:
            connection.send(data)
            data = file.read(1024)

def download_file(connection, filename, username):
        connection.send("DOWNLOAD".encode('utf-8'))
        connection.send(filename.encode('utf-8'))
        data = connection.recv(1024)
        if data == b"File tidak ditemukan":
            print(data.decode('utf-8'))
        else:
            with open(filename, 'wb') as file:
                while True:
                    if data == b"File terkirim":
                        print(f"{filename} berhasil diunduh dari server oleh {username}")
                        break
                    file.write(data)
                    data = connection.recv(1024)

            
def get_most_active_clients(connection):
    connection.send("GET_ACTIVE_CLIENTS".encode('utf-8'))
    data = connection.recv(4096).decode('utf-8')
    data = json.loads(data)
    for client_data in data:
        print(f"{client_data['username']}: {client_data['activity']['upload']} unggah, {client_data['activity']['download']} unduh")


def set_username(user, users):
    if user in users:
        print("Username sudah ada")
    else:
        users.append(user)
        print(f"Username {user} berhasil disimpan")

users = []
def main():
    username = input("Username: ")
    set_username(username, users)
    while True:
        # Inisialisasi client
        host = "127.0.0.2"
        port = 2121

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        client.send(username.encode('utf-8'))

        # Pilih opsi
        print("Menu:")
        print("1. Unggah file")
        print("2. Unduh file")
        print("3. Melihat klien paling aktif")
        print("4. Lihat user")
        print("5. Log out")
        print("6. Keluar")
        choice = input("Pilih menu (1/2/3/4/5/6): ")

        if choice == "1":
            client.send("UPLOAD".encode('utf-8'))
            filename = input("Masukkan nama file untuk diunggah: ")
            client.send(filename.encode('utf-8'))
            upload_file(client, filename, username)
            print(f"{filename} berhasil diunggah ke server")
        elif choice == "2":
            client.send("DOWNLOAD".encode('utf-8'))
            filename = input("Masukkan nama file untuk diunduh: ")
            client.send(filename.encode('utf-8'))
            download_file(client, filename, username)
        elif choice == "3":
            get_most_active_clients(client)
        elif choice == "4":
            print(users)
        elif choice == "5":
            main()
        elif choice == "6":
            client.close()
            break;
        else:
            print("Menu tidak valid")
            main()

    # Tutup koneksi
    client.close()

if __name__ == "__main__":
    main()