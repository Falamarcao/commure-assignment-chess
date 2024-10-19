from httpx import Client

class Lichess:
    """A Lichess client implementation to interact with the REST API."""
    
    def __init__(self):
         self.base_url = "https://lichess.org"
         self.client = Client()
    
    def get_one_leaderboard(self, nb: int, perfType: str):
        """Get the leaderboard for a single speed or variant (a.k.a. perfType).

        Args:
            nb (int): How many users to fetch.
            perfType (str): The speed or variant.
        """
        
        url = f"{self.base_url}/api/player/top/{nb}/{perfType}"
        response = self.client.get(url)

        response.raise_for_status()

        return response.json()
    
    def get_rating_history_of_a_user(self, username: str):
        """Read rating history of a user, for all perf types. 
        There is at most one entry per day.
        Format of an entry is [year, month, day, rating].
        month starts at zero (January).

        Args:
            username (str): The username.
        """
        
        url = f"{self.base_url}/api/user/{username}/rating-history"
        response = self.client.get(url)

        response.raise_for_status()

        return response.json()
    
    def close(self):
        """Closes the client connection."""
        self.client.close()
