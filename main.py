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
                key = command_parts[1]
                value = command_parts[2]
                if len(command_parts) > 3:
                    expiry_ms = int(command_parts[4])
                    expires_at = time.time() + (expiry_ms / 1000.0)
                    data_store[key] = {"type": "string", "value": value, "expires_at": expires_at}
                    client_socket.sendall(b"+OK\r\n")
                else:
                    data_store[key] = {"type": "string", "value": command_parts[2], "expires_at": None}
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
            elif command == "RPUSH":
                key = command_parts[1]
                values = command_parts[2:]
                if key not in data_store:
                    data_store[key] = {"type": "list", "value": [], "expires_at": None}
                if data_store[key]["type"] != "list":
                    client_socket.sendall(b"-WRONGTYPE Operation against a key holding the wrong kind of value\r\n")
                    continue
                data_store[key]["value"].extend(values)
                client_socket.sendall(f":{len(data_store[key]["value"])}\r\n".encode())
            elif command == "LRANGE":
                key = command_parts[1]
                start = int(command_parts[2])
                stop = int(command_parts[3])
                if key not in data_store:
                    client_socket.sendall(b"*0\r\n")
                    continue
                if data_store[key]["type"] != "list":
                    client_socket.sendall(b"-WRONGTYPE Operation against a key holding the wrong kind of value\r\n")
                    continue
                if start < 0:
                    start = len(data_store[key]["value"]) + start
                if stop < 0:
                    stop = len(data_store[key]["value"]) + stop
                if start > stop:
                    client_socket.sendall(b"*0\r\n")
                    continue
                items = data_store[key]["value"][start:stop+1]
                if items:
                    response = f"*{len(items)}\r\n"
                    for item in items:
                        response += f"${len(item)}\r\n{item}\r\n"
                    client_socket.sendall(response.encode())
                else:
                    client_socket.sendall(b"*0\r\n")
    finally:
        client_socket.close()

while True:
    server_socket.settimeout(1.0)
    try:
        client_socket, client_address = server_socket.accept()
    except TimeoutError:
        # 1 second passed with no client - loop repeats, allowing Python to catch Ctrl+C!
        continue
    except KeyboardInterrupt:
        print("\nShutting down server...")
        break
    print("Connected from", client_address)
    thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
    thread.start()
