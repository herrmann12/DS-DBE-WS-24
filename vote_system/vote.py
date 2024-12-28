import argparse
from utils import send_leader_msg
from constants import *

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Vote in an election")
    parser.add_argument('--id', type=str, required=True, help='Your unique hash')
    parser.add_argument('--candidate', type=str, required=True, help='Candidate you want to vote for')
    parser.add_argument('--election_id', type=str, required=True, help='ID of election to vote in')
    return parser.parse_args()

def vote(unique_id, candidate, election_id):
    """Prepare and send a vote message to the server."""
    message = {
        'type': 'vote',
        'id': unique_id,
        'candidate': candidate,
        'election_id': election_id,
    }
    send_leader_msg(message)

def main():
    """Main function to handle voting process."""
    # Parse the command-line arguments
    args = parse_arguments()

    # Send the vote message
    vote(args.id, args.candidate, args.election_id)

if __name__ == '__main__':
    main()
