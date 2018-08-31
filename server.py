import socket
import sys
import os

server_address = './snap.socket'
CHUNK_SIZE = 8 * 1024

response_json = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n'
response_bin = 'HTTP/1.1 200 OK\nContent-Type: application/octet-stream\n\n'

vscode = response_json + open('./files/vscode').read()
core = response_json + open('./files/ubuntu-core').read()
b8 = open('./files/b8X2psL1ryVrPt5WEmpYiqfr5emixTd7_1797.snap', 'rb')
xp = open('./files/XPQdduIwHiDCZvPHRrmsqV7Nr6nQRuqM_52.snap', 'rb')

conn_end = str.encode('Connection ended')

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print (sys.stderr, 'starting up on %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

def send(data, connection):
    connection.send(str.encode(response_bin))
    chunk = data.read(CHUNK_SIZE)
    while (chunk):
        connection.send(chunk)
        chunk = data.read(CHUNK_SIZE)
    return

while True:
    # Wait for a connection
    print (sys.stderr, 'waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print (sys.stderr, 'connection from', client_address)

        stop = False
        while not stop:
            data = connection.recv(CHUNK_SIZE).decode()
            print (sys.stderr, 'received "%s"' % data)
            if '/api/v1/snaps/details/vscode' in data:
                connection.sendall(str.encode(vscode))
            elif '/api/v1/snaps/details/ubuntu-core' in data:
                connection.sendall(str.encode(core))
            elif '/api/v1/snaps/download/XPQdduIwHiDCZvPHRrmsqV7Nr6nQRuqM_52.snap' in data:
                send(xp, connection)
            elif '/api/v1/snaps/download/b8X2psL1ryVrPt5WEmpYiqfr5emixTd7_1797.snap' in data:
                send(b8, connection)
            else:
                connection.sendall(conn_end)
            stop = True
            
    finally:
        # Clean up the connection
        connection.close()
        