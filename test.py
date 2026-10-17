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

s1.sendall(b"*3\r\n$5\r\nRPUSH\r\n$6\r\nmylist\r\n$5\r\nfirst\r\n")
print('RPUSH 1 got:', s1.recv(1024))
s1.sendall(b"*4\r\n$5\r\nRPUSH\r\n$6\r\nmylist\r\n$4\r\nsecond\r\n$5\r\nthird\r\n")
print('RPUSH 2 got:', s1.recv(1024))

# Push 3 items: "a", "b", "c"
s1.sendall(b"*5\r\n$5\r\nRPUSH\r\n$6\r\nletters\r\n$1\r\na\r\n$1\r\nb\r\n$1\r\nc\r\n")
print("RPUSH got:", s1.recv(1024))

# LRANGE letters 0 1 -> should return ["a", "b"] (*2\r\n...)
s1.sendall(b"*4\r\n$6\r\nLRANGE\r\n$7\r\nletters\r\n$1\r\n0\r\n$2\r\n-1\r\n")
print("LRANGE 0 -1 got:", s1.recv(1024))

# LRANGE letters 1 2 -> should return ["b", "c"] (*2\r\n...)
s1.sendall(b"*4\r\n$6\r\nLRANGE\r\n$7\r\nletters\r\n$1\r\n1\r\n$1\r\n2\r\n")
print("LRANGE 1 2 got:", s1.recv(1024))

