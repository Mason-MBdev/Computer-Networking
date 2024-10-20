import socket
import threading
from datetime import datetime
import json
import os
import struct

# Global client cache (in-memory)
client_cache = {}
MAX_CLIENTS = 3
client_count = 0  # Tracks active clients
client_id_counter = 0  # Assigns unique client IDs dynamically

def handle_client(client_socket, client_name, client_addr):
    global client_count
    client_socket.send("CONNECTED".encode())
    # Store client connection time
    connected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_cache[client_name] = {'address': client_addr, 'connected_at': connected_at, 'disconnected_at': None}
    
    while True:
        try:
            # Receive message from the client
            message = client_socket.recv(1024).decode()
            
            if message == "exit":
                # Disconnect the client
                print(f"{client_name}{client_addr} has disconnected.")
                disconnected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                client_cache[client_name]['disconnected_at'] = disconnected_at
                client_socket.close()
                break
            elif message == "status":
                # Send the current client cache in JSON format back to the client
                status_json = json.dumps(client_cache, indent=4)
                print(f"JSON sent to {client_name}{client_addr}")
                client_socket.send(status_json.encode())
            elif message == "list":
                # Get the list of files but not directories
                files = []
                for file in os.listdir():
                    if os.path.isfile(file):
                        files.append(file)
                #format the files so it looks like a list
                response = f"['{"', '".join(files)}']"
                print(f"{response} sent to {client_name}{client_addr}")
                client_socket.send(response.encode())
            elif "fetch " in message:
                filename = message.split(" ")[1]

                #check if file exists
                if os.path.isfile(filename):
                    #send confirmation of a file being sent to the client
                    client_socket.send("FILE".encode())

                    file = open(filename, "rb")
                    data = file.read(1024)

                    #send the file size to the client
                    filesize = os.path.getsize(filename)
                    client_socket.send(struct.pack(">Q", filesize))

                    #send file data to client
                    sent = 0
                    packetnum = 0
                    while data:
                        sent += len(data)
                        packetnum += 1
                        print(f"#{packetnum}: {sent} bytes sent to {client_name}{client_addr}")
                        client_socket.send(data)
                        data = file.read(1024)
                    file.close()
                    print(f"File '{filename} sent to {client_name}{client_addr}")
                else:
                    print(f"File '{filename}' requested by {client_name}{client_addr} does not exist")
                    client_socket.send(f"File '{filename}' does not exist".encode())
            else:
                # Echo the message back with "ACK" appended
                print(f"{client_name}{client_addr}: {message}")
                response = f"{message} ACK"
                client_socket.send(response.encode())
        except:
            print(f"Connection with {client_name}{client_addr} was interrupted.")
            disconnected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            client_cache[client_name]['disconnected_at'] = disconnected_at
            client_socket.close()
            break

    # Clean up after the client disconnects
    # client_cache.pop(client_name, None) uncomment to remove client from cache upon disconnection
    client_count -= 1
    print(f"Client count is now: {client_count}")

def start_server():
    global client_count, client_id_counter
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(MAX_CLIENTS)
    print("Server is listening...")

    while True:
        client_socket, client_addr = server_socket.accept()

        if client_count >= MAX_CLIENTS:
            # Send rejection message if the client limit is exceeded
            client_socket.send("SERVER FULL".encode())
            client_socket.close()
            print(f"Connection from {client_addr} refused. Maximum clients reached.")
        else:
            # Accept new client
            client_id_counter += 1
            client_name = f"Client{client_id_counter:02d}"
            client_count += 1
            print(f"{client_name} connected from {client_addr}. Active clients: {client_count}")

            # Start a new thread for each client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_name, client_addr))
            client_thread.start()

if __name__ == '__main__':
    start_server()
