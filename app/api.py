"""Main API file"""

import requests
from litestar import Litestar, get, Request, Response
from litestar.config.cors import CORSConfig
from litestar.middleware.rate_limit import RateLimitConfig
from app.config import PROVIDER_GOGO, SCRAPPER


@get("/", cache=3600)
async def index() -> str:
    """Return just an str

    Returns:
        str: The message to show when the API is running.
    """
    return """API is running"""


@get("/search/", cache=3600)
async def search_anime(q: str, provider: int = 1, max_res: int = 5) -> list:
    """Searches for anime based on query"""
    print(q, provider)
    return await SCRAPPER(PROVIDER_GOGO[provider]).search(q, max_res)


@get("/anime/", cache=3600)
async def get_anime_info(anime_id: str, provider: int = 1) -> dict:
    """Gets anime information based on anime_id"""
    return await SCRAPPER(PROVIDER_GOGO[provider]).get_anime_metadata(anime_id)


@get("/streaming-links/", cache=3600)
async def get_streaming(anime_id: str, episode_no: str, provider: int = 1) -> dict:
    """Gets streaming links based on anime_id and episode_no"""
    return await SCRAPPER(PROVIDER_GOGO[provider]).get_stream(anime_id, episode_no)


@get("/list_providers/", cache=True)
async def list_providers() -> list:
    """Lists all available providers but hides the actual URL
    Example: https://*****.com"""
    return [
        "https://" + "*" * 5 + url.split("https://")[1].split(".")[-1]
        for url in PROVIDER_GOGO
    ]


@get("/health/", cache=3600)
async def health(provider: int = 1) -> bool:
    """Health check"""

    return requests.get(PROVIDER_GOGO[provider], timeout=2).status_code == 200


func_to_expose = [
    search_anime,
    get_anime_info,
    get_streaming,
    list_providers,
    health,
    index,
]
cors_config = CORSConfig(allow_origins=["*"])
rate_limit_config = RateLimitConfig(rate_limit=("minute", 20))


def value_error_handler(request: Request, exc: ValueError) -> Response:
    """Value Error Handler"""
    print(request)
    return Response(
        media_type="application/json",
        status_code=404,
        content={"error": str(exc)},
    )


app = Litestar(
    func_to_expose,
    cors_config=cors_config,
    middleware=[rate_limit_config.middleware],
    exception_handlers={ValueError: value_error_handler},
)
