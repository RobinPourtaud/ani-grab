"""Generic scrapper package for scraping data from websites.

This package provides a generic interface for scraping data from websites.
New parsers can be added by creating a new file of type `Scrapper` in this directory.

Classes:
    Scrapper: Generic scrapper class for scraping data from websites.

Everything is static in order for the API to be stateless.
"""

from typing import Dict, List


class Scrapper:
    """Generic scrapper class for scraping data from websites.

    This class provides a generic interface for scraping data from websites.

    Attributes:
        provider (str): The provider to scrape data from.

    Everything is static in order for the API to be stateless.
    """

    def __init__(self, provider: str):
        """Initialize the Scrapper class.

        Args:
            provider (url): The provider to scrape data from. (example: "https://example.com")

        """
        self.provider = provider

    async def get_anime_metadata(self, anime_id: str) -> Dict[str, str]:
        """Get anime details.

        Args:
            anime_id (str): The ID of the anime.

        Returns:
            Dict[str, str]: The details of the anime.

        """
        raise NotImplementedError

    async def search(self, query: str) -> List[Dict[str, str]]:
        """Search for anime.

        Args:
            query (str): The search query.

        Returns:
            List[Dict[str, str]]: The list of anime matching the search query.

        """
        raise NotImplementedError

    async def get_stream(self, anime_id: str, episode_no: str) -> Dict[str, str]:
        """Get the streaming link of the anime episode.

        Args:
            anime_id (str): The ID of the anime.
            episode_no (str): The episode number.

        Returns:
            Dict[str, str]: The last episode and the streaming link.

        """
        raise NotImplementedError
