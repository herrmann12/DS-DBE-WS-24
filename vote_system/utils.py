import socket
import json
from constants import *

def send_leader_msg(msg):
    # Create a UDP socket to listen for the "leader" message
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener_sock:
        listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        listener_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener_sock.bind(('', BROADCAST_PORT))
        listener_sock.settimeout(5.0)
        
        print("Waiting for a message of type 'leader'...")

        while True:
            data, addr = listener_sock.recvfrom(1024)  # Receive message from any address
            received_msg = json.loads(data.decode())
            
            # Check if the message is of type "leader"
            if received_msg["type"] == "leader":
                leader_ip = received_msg["host"]
                leader_port = received_msg["port"]
                
                if leader_ip and leader_port:
                    print(f"Leader found! IP: {leader_ip}, Port: {leader_port}")
                    
                    # Send the given message to the leader's IP and port
                    return send_msg(leader_ip, leader_port, msg)

def send_msg(host, port, msg):
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the server (leader)
        sock.connect((host, port))

        # Send the message to the server
        sock.sendall(json.dumps(msg).encode())

        # Receive the server's response
        data = sock.recv(1024)
        msg = data.decode()
        print(f"Received: {msg}")
        
    return msg
