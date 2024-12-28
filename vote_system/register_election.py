import argparse
from utils import send_leader_msg
from constants import *

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Register an election")
    parser.add_argument('--id', type=str, required=True, help='Your unique hash')
    parser.add_argument('--candidates', type=str, nargs='+', required=True, help='List of candidates you want to vote for')
    parser.add_argument('--authorized_users', type=str, nargs='+', required=True, help='List of users authorized to vote')
    return parser.parse_args()

def register_election(election_id, candidates, authorized_users):
    """Prepare and send election registration data."""
    message = {
        'type': 'election',
        'id': election_id,
        'candidates': candidates,
        'authorized_users': authorized_users,
    }
    send_leader_msg(message)

def main():
    """Main function to handle election registration."""
    # Parse the command-line arguments
    args = parse_arguments()

    # Register the election
    register_election(args.id, args.candidates, args.authorized_users)

if __name__ == '__main__':
    main()
