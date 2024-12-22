import socket
import json

# Function to send any message to a specified host and port
def send_msg(host, port, msg):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the server
        sock.connect((host, port))

        # Send the message to the server
        sock.sendall(json.dumps(msg).encode())

        # Receive the server's response
        data = sock.recv(1024)
        msg = data.decode()
        print(f"Received: {msg}")
    return msg