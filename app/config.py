"""Config file for the app
"""

import os
from app.scrapper.gogo import GogoAnime

if os.getenv("PROVIDER_GOGO"):
    PROVIDER_GOGO = os.getenv("PROVIDER_GOGO").split(",")
else:
    PROVIDER_GOGO = [
        "https://default.com",
        "https://default.com2",
    ]

if os.getenv("SCRAPPER"):
    SCRAPPER_NAME = os.getenv("SCRAPPER")
    SCRAPPER = globals()[SCRAPPER_NAME]
else:
    SCRAPPER = GogoAnime
