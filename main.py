import socket
import threading
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(('127.0.0.1', 6379))
server_socket.listen()
print("Server listening on port 6379")

data_store = {}

def handle_client(client_socket):
    try:
        while True:
            try:
                data = client_socket.recv(1024)
            except ConnectionResetError:
                break
            if not data:
                break

            text = data.decode()
            splitted_text = text.split("\r\n")

            command_parts = []

            for i in range(len(splitted_text)):
                if splitted_text[i].startswith("$"):
                    command_parts.append(splitted_text[i + 1])
            
            if len(command_parts) < 1:
                client_socket.sendall(b"-Error: Not enough arguments\r\n")
                continue

            command = command_parts[0].upper()

            if command == "PING":
                client_socket.sendall(b"+PONG\r\n")
            elif command == "ECHO":
                client_socket.sendall(f"${len(command_parts[1])}\r\n{command_parts[1]}\r\n".encode())
            elif command == "SET":
                if len(command_parts) > 3:
                    expiry_ms = int(command_parts[4])
                    expires_at = time.time() + (expiry_ms / 1000.0)
                    data_store[command_parts[1]] = {"value": command_parts[2], "expires_at": expires_at}
                    client_socket.sendall(b"+OK\r\n")
                else:
                    data_store[command_parts[1]] = {"value": command_parts[2], "expires_at": None}
                    client_socket.sendall(b"+OK\r\n")
            elif command == "GET":
                key = command_parts[1]
                if key not in data_store:
                    client_socket.sendall(b"$-1\r\n")
                    continue
                entry = data_store[key]
                if entry["expires_at"] is not None and entry["expires_at"] < time.time():
                    del data_store[key]
                    client_socket.sendall(b"$-1\r\n")
                    continue
                client_socket.sendall(f"${len(entry["value"])}\r\n{entry["value"]}\r\n".encode())

    finally:
        client_socket.close()

while True:
    client_socket, client_address = server_socket.accept()
    print("Connected from", client_address)
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()

