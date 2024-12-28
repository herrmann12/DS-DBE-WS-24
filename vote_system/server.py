import socket
import select
import json
import threading
import time
import argparse
import random
from election import Election
from constants import *

# Argument parser setup
def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Election server setup")
    parser.add_argument('--host', type=str, required=True, help='Host to bind to')
    parser.add_argument('--port', type=int, required=True, help='Port to bind to')
    return parser.parse_args()


class Server:
    """Server class to handle election processes, including leader election, voting, and broadcast management."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.id = random.randint(1, int(1e9))

        # Initialize sockets
        self.broadcast_sock = self.create_broadcast_socket()
        self.server_socket = self.create_server_socket()

        # Internal states
        self.is_leader = False
        self.lcr_ongoing = False
        self.running = False
        self.threads = []
        self.elections = {}
        self.ring_last_seen = {}
        self.last_leader_time = time.time()
        self.neighbor = None

    def create_broadcast_socket(self):
        """Create and configure the broadcast socket."""
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast_sock.bind(('', BROADCAST_PORT))
        broadcast_sock.settimeout(1.0)
        return broadcast_sock

    def create_server_socket(self):
        """Create and configure the server socket."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)  # Increase listen queue for handling multiple connections
        return server_socket

    def add_election(self, election):
        """Add a new election to the server."""
        if not self.running:
            return "Server is not running"
        if election.id in self.elections:
            return f"Election id {election.id} already exists"
        self.elections[election.id] = election
        return f"Election {election.id} added successfully."

    def remove_election(self, election_id):
        """Remove an election from the server."""
        if election_id not in self.elections:
            return f"Election id {election_id} not found"
        del self.elections[election_id]
        return f"Election {election_id} removed."

    def elections_to_json(self):
        """Convert all elections to a JSON format."""
        return [election.to_json() for election in self.elections.values()]

    def load_elections_from_json(self, elections_json):
        """Load elections from a JSON string, clearing any existing elections."""
        self.elections.clear()
        try:
            for election_data in elections_json:
                election = Election.from_json(election_data)
                self.add_election(election)
            return "Elections loaded successfully."
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
        except Exception as e:
            return f"Error loading elections: {e}"

    def run(self):
        """Start the server and its background threads."""
        print("Server starting...")
        self.running = True
        functions = [
            self.handle_server_msgs, self.check_shutdown, self.broadcast_address,
            self.handle_broadcast_msgs, self.check_leader, self.update_ring,
            self.send_leader, self.listen_leader
        ]
        for func in functions:
            thread = threading.Thread(target=func)
            self.threads.append(thread)
            thread.start()
        print("Server running")

    def stop(self):
        """Stop the server and wait for threads to finish."""
        print("Server stopping...")
        self.running = False
        for thread in self.threads:
            thread.join()

    def send_leader(self):
        """Broadcast leader information and all election details."""
        while self.running:
            if self.is_leader:
                msg = {
                    'type': 'leader',
                    'host': self.host,
                    'port': self.port,
                    'elections': self.elections_to_json()
                }
                self.broadcast_message(msg)
            time.sleep(1)
    
    def broadcast_address(self):
        """Check if a leader needs to be elected."""
        while self.running:
            msg = {
                'type': 'ring',
                'host': self.host,
                'port': self.port,
            }
            self.broadcast_message(msg)
            time.sleep(.5)

    def broadcast_message(self, msg):
        """Helper function to broadcast messages."""
        try:
            self.broadcast_sock.sendto(json.dumps(msg).encode(), (BROADCAST_HOST, BROADCAST_PORT))
        except socket.error as e:
            print(f"Error broadcasting message: {e}")

    def listen_leader(self):
        """Listen for leader messages from other servers."""
        while self.running:
            if self.is_leader:
                self.listen_for_leader_connections()

    def listen_for_leader_connections(self):
        """Listen and process leader connections."""
        leader_sock = self.create_leader_socket()
        while self.running and self.is_leader:
            try:
                ready_to_read, _, _ = select.select([leader_sock], [], [], 1)
                if ready_to_read:
                    client_sock, _ = leader_sock.accept()
                    self.process_client_request(client_sock)
            except socket.error as e:
                print(f"Error handling leader connections: {e}")

    def create_leader_socket(self):
        """Create the leader socket to accept connections."""
        leader_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        leader_sock.bind((LEADER_HOST, LEADER_PORT))
        leader_sock.listen(5)
        return leader_sock

    def process_client_request(self, client_sock):
        """Process incoming client requests."""
        def send_client(msg):
            client_sock.sendall(msg.encode())

        try:
            msg = json.loads(client_sock.recv(1024).decode())
            if msg['type'] == 'vote':
                resp = self.handle_vote(msg)
                send_client(resp)
            elif msg['type'] == 'election':
                resp = self.handle_election(msg)
                send_client(resp)
            elif msg['type'] == 'end_election':
                resp = self.handle_election_end(msg)
                send_client(resp)
        finally:
            client_sock.close()

    def handle_election(self, msg):
        """Handle incoming election requests."""
        election_id = msg['id']
        if election_id in self.elections:
            return f"Election id {election_id} already exists"
        
        election = Election(election_id, msg['candidates'], msg['authorized_users'])
        return self.add_election(election)

    def handle_election_end(self, msg):
        """Handle election end and calculate results."""
        election_id = msg['id']
        if election_id not in self.elections:
            return f"Election id {election_id} not found"
        
        election = self.elections[election_id]
        winner = max(election.get_votes(), key=election.get_votes().get)

        result_msg = f"Election {election_id} ended. The winner is {winner}."
        self.remove_election(election_id)
        return result_msg

    def handle_vote(self, msg):
        """Handle incoming vote messages."""
        election_id = msg['election_id']
        if election_id not in self.elections:
            return f"Error: Election id {election_id} unknown"
        
        election = self.elections[election_id]
        return election.register_vote(msg['id'], msg['candidate'])

    def check_leader(self):
        """Check if a leader needs to be elected."""
        while self.running:
            if not self.is_leader and not self.lcr_ongoing and time.time() - self.last_leader_time > 5:
                self.find_new_leader()

    def send_neighbor(self, msg):
        """Send a message to the next neighbor in the ring."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(self.neighbor)
                sock.sendall(msg.encode())
            except socket.error as e:
                print(f"Error sending message to neighbor: {e}")

    def find_new_leader(self):
        """Find and declare a new leader."""
        self.lcr_ongoing = True
        if self.neighbor == (self.host, self.port):
            self.declare_leader()
        else:
            self.send_neighbor(json.dumps({'id': self.id, 'type': 'lcr'}))

    def declare_leader(self):
        """Declare the current server as the leader."""
        print("I am the new leader")
        self.is_leader = True
        self.lcr_ongoing = False

    def check_shutdown(self):
        """Check for server shutdown signal."""
        try:
            while self.running:
                pass
        except KeyboardInterrupt:
            self.stop()

    def handle_server_msgs(self):
        """Handle incoming server messages."""
        while self.running:
            try:
                ready_to_read, _, _ = select.select([self.server_socket], [], [], 1)
                if ready_to_read:
                    client_socket, _ = self.server_socket.accept()
                    self.process_client_request(client_socket)
            except socket.error as e:
                print(f"Error handling server messages: {e}")

    def handle_ring_msg(self, msg):
        """Handle incoming ring messages."""
        self.ring_last_seen[(msg['host'], msg['port'])] = time.time()

    def handle_leader_msg(self, msg):
        """Handle leader message and load election information."""
        self.last_leader_time = time.time()
        self.lcr_ongoing = False
        if not self.is_leader:
            self.load_elections_from_json(msg['elections'])

    def handle_broadcast_msgs(self):
        """Handle incoming broadcast messages."""
        while self.running:
            try:
                msg, _ = self.broadcast_sock.recvfrom(1024)
                msg = json.loads(msg.decode())
                if msg['type'] == 'ring':
                    self.handle_ring_msg(msg)
                elif msg['type'] == 'leader':
                    self.handle_leader_msg(msg)
            except socket.timeout:
                pass
            except socket.error as e:
                print(f"Error handling broadcast messages: {e}")

    def update_ring(self):
        """Update the server's view of the ring."""
        while self.running:
            self.ring_last_seen[(self.host, self.port)] = time.time()
            for (h, p), t in self.ring_last_seen.copy().items():
                if time.time() - t > 2:
                    del self.ring_last_seen[(h, p)]
            ring_members = list(self.ring_last_seen.keys())
            i = ring_members.index((self.host, self.port))
            self.neighbor = ring_members[(i + 1) % len(ring_members)]


if __name__ == '__main__':
    args = parse_arguments()
    server = Server(host=args.host, port=args.port)
    server.run()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
