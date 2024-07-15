"""A scrapper for data from GogoAnime.

This module provides a scrapper for data from GogoAnime.
Get the url yourself.

Classes:
    GogoAnime: A scrapper for data from GogoAnime.

"""

import json
import re
from urllib.parse import parse_qsl, urlencode
import base64
from selectolax.parser import HTMLParser
import aiohttp
import requests
from Crypto.Cipher import AES
from . import Scrapper


class GogoAnime(Scrapper):
    """A scrapper for data from GogoAnime.

    This class provides a scrapper for data from GogoAnime.

    Attributes:
        provider (str): The provider to scrape data from (url). Heritage from Scrapper.
    """

    async def get_anime_metadata(self, anime_id: str) -> dict:
        """Get anime details.

        Args:
            anime_id (str): The ID of the anime.

        Returns:
            dict: The details of the anime.

        """
        url = f"{self.provider}/category/{anime_id}"
        parser = await self._parser(url)

        img_url = parser.css_first(".anime_info_body_bg img").attributes["src"]
        img_url = self._correct_img_url(img_url)
        about = parser.css_first(".anime_info_body_bg p:nth-of-type(3)").text()
        name = parser.css_first("div.anime_info_body_bg h1").text()
        last_ep = int(
            parser.css_first("#episode_page li:last-child a").attributes["ep_end"]
        )
        episodes = list(range(1, last_ep + 1))
        return {"name": name, "img_url": img_url, "about": about, "episodes": episodes}

    async def search(
        self, query: str, results: int = 5, filter_dub: bool = True
    ) -> list:
        """Search for anime.

        Args:
            query (str): The search query.
            results (int): The number of results to return.

        Returns:
            list: The list of anime matching the search query.

        """
        url = f"{self.provider}/search.html?keyword={query}"
        parser = await self._parser(url)

        anime_list = []

        for element in parser.css("div.last_episodes ul.items li"):
            name = element.css_first("p a").attributes["title"]
            if (
                not name
            ):  # name attribute can be stupid and contains a " symbol that messes up the search
                name = element.css_first("p").text()
            if "(dub)" in name.lower() and filter_dub:
                continue

            img = element.css_first("div a img").attributes["src"]
            img_url = self._correct_img_url(img)
            id_ = element.css_first("div a").attributes["href"].split("/")[-1]

            anime = {
                "name": name,
                "img_url": img_url,
                "id": id_,
            }
            anime_list.append(anime)
        return anime_list[:results]

    async def get_stream(self, anime_id: str, episode_no: str) -> None:
        """Get the stream link from the embed link of the anime episode.

        Args:
            embed_url (str, optional): The embed link of the anime episode. Defaults to None.
            quality (str, optional): The quality of the stream. Defaults to "best".

        Returns:
            Dict[str, str]: The last episode and the streaming link.
        """
        url_provider = f"{self.provider}/{anime_id}-episode-{episode_no}"

        parser = await self._parser(url_provider)

        if "not found" in parser.css_first("title").text():
            url_provider_ep_1 = f"{self.provider}/{anime_id}-episode-1"
            parser_ep_1 = await self._parser(url_provider_ep_1)
            if "not found" in parser_ep_1.css_first("title").text():
                raise ValueError("Anime not found")
            raise ValueError("Episode not found")

        last_ep = parser.css_first("#episode_page li:last-child a").attributes["ep_end"]
        embeded_url = parser.css_first("div.play-video iframe").attributes["src"]

        url_domain = "/".join(embeded_url.split("/")[:3])
        id_embed = embeded_url.split("id=")[1].split("&")[0]
        session = requests.Session()
        r = session.get(embeded_url)
        key, iv, second_key = re.findall(r"(?:container|videocontent)-(\d+)", r.text)

        parser = HTMLParser(r.text)
        script_html_episode = parser.css_first("script[data-name=episode]")
        crypted_data = script_html_episode.attributes["data-value"]

        data = {
            "id": aes_encrypt(id_embed, key.encode(), iv.encode()).decode(),
            **dict(
                parse_qsl(aes_decrypt(crypted_data, key.encode(), iv.encode()).decode())
            ),
        }

        r = session.post(
            url_domain + "/encrypt-ajax.php?" + urlencode(data) + f"&alias={id_embed}",
            headers={
                "x-requested-with": "XMLHttpRequest",
                "referer": embeded_url,
            },
        )

        link = json.loads(
            aes_decrypt(r.json().get("data"), second_key.encode(), iv.encode())
        )["source"][0]["file"]

        # I does not make sense to return last_ep but it is useful for my frontend
        return {
            "last_ep": last_ep,
            "streaming_link": link,
        }

    async def _parser(self, url: str) -> HTMLParser:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("Status:", response.status)
                return HTMLParser(await response.text())

    def _correct_img_url(self, url: str) -> str:
        if url.startswith("/"):  # Some images are relative paths
            return self.provider + url
        return url


def aes_encrypt(data: str, key: str, iv: str) -> str:
    """Encrypt data with AES-128-CBC.

    Args:
        data (str): The data to encrypt.
        key (str): The key to encrypt the data.
        iv (str): The initialization vector.

    Returns:
        str: The encrypted data.

    """
    padded_data = data + chr(len(data) % 16) * (16 - len(data) % 16)
    return base64.b64encode(
        AES.new(key, AES.MODE_CBC, iv=iv).encrypt(padded_data.encode())
    )


def aes_decrypt(data: str, key: str, iv: str) -> str:
    """Decrypt data with AES-128-CBC.

    Args:
        data (str): The data to decrypt.
        key (str): The key to decrypt the data.
        iv (str): The initialization vector.

    Returns:
        str: The decrypted data.

    """
    return (
        AES.new(key, AES.MODE_CBC, iv=iv)
        .decrypt(base64.b64decode(data))
        .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
    )
