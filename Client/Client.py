import socket
import struct


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #set timeout for 10 seconds
    client_socket.settimeout(10)
    try:
        address = input("Server Address (leave blank for localhost): ")
        if not address:
            address = "localhost"
        client_socket.connect((address, 12345))  # Connect to the server
    except:
        print(f"Unable to connect to '{address}'. Make sure the server is online and you have the right ip address.")
        return
    response = client_socket.recv(1024).decode()
    if response == "SERVER FULL":
        print(f"Server '{address}' is full. Connection refused.")
        return
    elif response == "CONNECTED":
        print(f"Successfully connected to '{address}'")
    
    #if connection was successful set the timeout to None
    client_socket.settimeout(None)
    
    while True:
        message = input("Enter message: ")
        client_socket.send(message.encode())

        if message == "exit":
            break

        # Receive server's response
        response = client_socket.recv(1024).decode()

        if response == "FILE":
            filename = message.split(" ")[1]
            file = open(filename, "wb")
            
            #unpack the filesize
            filesize = struct.unpack(">Q", client_socket.recv(8))[0]

            recieved = 0
            packetnum = 0
            #recieve data until full filesize has been recieved
            while recieved < filesize:

                response = client_socket.recv(1024)
                recieved += len(response)
                packetnum += 1
                print(f"#{packetnum}: {recieved} bytes recieved")

                file.write(response)

            file.close()
            print("File downloaded successfully")
        else:
            #print server response
            print(f"Server response: {response}")

    client_socket.close()


if __name__ == '__main__':
    start_client()
