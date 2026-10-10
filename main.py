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
                data_store[command_parts[1]] = command_parts[2]
                client_socket.sendall(b"+OK\r\n")
                if len(command_parts) > 3:
                    expiry_seconds = int(command_parts[4]) / 1000.0
                    data_store[command_parts[1] + "_deadline"] = time.time() + expiry_seconds
                                        
            elif command == "GET":
                if command_parts[1] in data_store:
                    client_socket.sendall(f"${len(data_store[command_parts[1]])}\r\n{data_store[command_parts[1]]}\r\n".encode())
                else:
                    client_socket.sendall(b"$-1\r\n")

                    
    finally:
        client_socket.close()

while True:
    client_socket, client_address = server_socket.accept()
    print("Connected from", client_address)
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()

