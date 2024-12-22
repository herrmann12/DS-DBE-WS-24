import argparse
from utils import send_msg
from constants import *

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Vote in an election")
    parser.add_argument('--id', type=str, required=True, help='Your unique hash')
    parser.add_argument('--candidate', type=str, required=True, help='Candidate you want to vote for')
    parser.add_argument('--election_id', type=str, required=True, help='ID of election to vote in')
    return parser.parse_args()

def vote(host, port, unique_id, candidate, election_id):
    """Prepare and send a vote message to the server."""
    message = {
        'type': 'vote',
        'id': unique_id,
        'candidate': candidate,
        'election_id': election_id,
    }
    send_msg(host, port, message)

def main():
    """Main function to handle voting process."""
    # Parse the command-line arguments
    args = parse_arguments()

    # Send the vote message
    vote(LEADER_HOST, LEADER_PORT, args.id, args.candidate, args.election_id)

if __name__ == '__main__':
    main()
