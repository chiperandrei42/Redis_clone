import socket
import time

s1 = socket.create_connection(('127.0.0.1', 6379))
s2 = socket.create_connection(('127.0.0.1', 6379))

s1.sendall(b"*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n")
print('Client 1 got:', s1.recv(1024))
s2.sendall(b"*1\r\n$4\r\nPING\r\n")
print('Client 2 got:', s2.recv(1024))

s1.sendall(b"*5\r\n$3\r\nSET\r\n$3\r\nkey\r\n$4\r\ntest\r\n$2\r\nPX\r\n$3\r\n200\r\n")
print('Client 1 got:', s1.recv(1024))
s1.sendall(b"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n")
print('Client 1 got:', s1.recv(1024))
time.sleep(0.3)
s1.sendall(b"*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n")
print('Client 1 got:', s1.recv(1024))

