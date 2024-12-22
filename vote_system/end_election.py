import argparse
from utils import send_msg
from constants import *

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="End an ongoing election")
    parser.add_argument('--id', type=str, required=True, help='Election id')
    return parser.parse_args()

def end_election(host, port, unique_id):
    message = {
        'type': 'end_election',
        'id': unique_id,
    }
    send_msg(host, port, message)

def main():
    """Main function to handle voting process."""
    # Parse the command-line arguments
    args = parse_arguments()

    # Send the vote message
    end_election(LEADER_HOST, LEADER_PORT, args.id)

if __name__ == '__main__':
    main()
