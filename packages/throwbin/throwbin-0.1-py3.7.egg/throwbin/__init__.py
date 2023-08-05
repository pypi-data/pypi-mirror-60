from .constants import AVAILABLE_SYNTAXES
from .exceptions import ThrowBinException
from .PasteModel import PasteModel

import requests


class ThrowBin:
    def __init__(self):
        self.url = "https://api.throwbin.io/v1"
        self.session = requests.session()

    def post(self, title, text, syntax) -> PasteModel:
        if syntax not in AVAILABLE_SYNTAXES:
            raise ThrowBinException(f"Unknown syntax: '{syntax}'")

        response = self.session.put(
            f"{self.url}/store",
            data={"title": title, "id": None, "paste": text, "syntax": syntax},
        ).json()

        return PasteModel(response["status"], response["id"])
