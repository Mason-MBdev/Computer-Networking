import socket


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 12345))  # Connect to the server
    except ConnectionRefusedError:
        print("Unable to connect to the server. It might be full or offline.")
        return

    while True:
        message = input("Enter message: ")
        client_socket.send(message.encode())

        if message == "exit":
            break

        # Receive and print server's response
        response = client_socket.recv(1024).decode()
        print(f"Server response: {response}")

    client_socket.close()


if __name__ == '__main__':
    start_client()
