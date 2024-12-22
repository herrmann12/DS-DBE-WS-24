import json

class Election:
    """Handles election logic, including managing candidates, authorized users, and voting."""
    
    def __init__(self, id: int, candidates: list, authorized_users: list):
        """
        Initializes an Election object.

        :param id: Election ID.
        :param candidates: List of candidates for the election.
        :param authorized_users: Set of users authorized to vote.
        """
        self.id = id
        self.candidates = list(candidates)  # Ensures candidates are unique
        self.authorized_users = list(authorized_users)  # Ensures authorized users are unique
        self.seen_users = list()  # Tracks users who have voted
        self.votes = {candidate: 0 for candidate in candidates}  # Initializes vote count
        
    def register_vote(self, user: str, candidate: str) -> str:
        """
        Registers a vote for a user.

        :param user: The user voting.
        :param candidate: The candidate the user is voting for.
        :return: Message indicating the result of the vote attempt.
        """
        # Check if the user is authorized
        if user not in self.authorized_users:
            return f"Error: User '{user}' is not authorized to vote."
        
        # Check if the candidate is valid
        if candidate not in self.candidates:
            return f"Error: Candidate '{candidate}' is not a valid candidate."
        
        # Check if the user has already voted
        if user in self.seen_users:
            return f"Error: User '{user}' has already voted."
        
        # Register the vote
        self.votes[candidate] += 1
        self.seen_users.append(user)
        return f"Vote for '{candidate}' by user '{user}' has been registered."

    def get_votes(self) -> dict:
        """
        Retrieves the current vote counts for each candidate.

        :return: A dictionary with candidates as keys and vote counts as values.
        """
        return self.votes.copy()
    

    def to_json(self):
        """Serialize the Election object to JSON."""
        return {
            'election_id': self.id,
            'candidates': self.candidates,
            'authorized_users': self.authorized_users,
            'votes': self.votes,
            'seen_users': self.seen_users,
        }

    @staticmethod
    def from_json(json_data):
        """Deserialize JSON data into an Election object."""
        election = Election(json_data['election_id'], json_data['candidates'], json_data['authorized_users'])
        election.votes = json_data['votes']  # Restoring the votes
        election.seen_users = json_data['seen_users']  # Restoring the votes
        return election
    