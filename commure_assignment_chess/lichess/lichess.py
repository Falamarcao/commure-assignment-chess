import asyncio

from httpx import AsyncClient


class Lichess:
    """A Lichess client implementation to interact with the REST API."""

    def __init__(self):
        self.base_url = "https://lichess.org"
        self.client = AsyncClient()
        self.MAX_CONCURRENT_REQUESTS = 1
        self.semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_REQUESTS)
        self.REQUEST_INTERVAL = 5

    async def _get(self, url: str):
        """Helper method to perform a GET request with rate limiting.

        Args:
            url (str): The URL to retrieve
        """
        async with self.semaphore:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()

    async def get_one_leaderboard(self, nb: int, perfType: str):
        """Get the leaderboard for a single speed or variant (a.k.a. perfType).

        Args:
            nb (int): How many users to fetch.
            perfType (str): The speed or variant.
        """

        url = f"{self.base_url}/api/player/top/{nb}/{perfType}"

        json_response = await self._get(url)

        await asyncio.sleep(self.REQUEST_INTERVAL)

        return json_response

    async def get_rating_history_of_a_user(self, username: str):
        """Read rating history of a user, for all perf types.
        There is at most one entry per day.
        Format of an entry is [year, month, day, rating].
        month starts at zero (January).

        Args:
            username (str): The username.
        """

        url = f"{self.base_url}/api/user/{username}/rating-history"
        json_response = await self._get(url)

        await asyncio.sleep(self.REQUEST_INTERVAL)

        return json_response
