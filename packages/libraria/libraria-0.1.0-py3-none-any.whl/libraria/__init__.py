

import json
import logging
import pathlib
from functools import lru_cache
import re
from typing import Generator, NamedTuple, List

import daiquiri
import requests
from bs4 import BeautifulSoup

__version__ = '0.1.0'

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger("libraria") 

_dir = pathlib.Path(__file__).parent.absolute()
cached_search_page = _dir / pathlib.Path("searchpage.html")
SMPL_SEARCH_URL = "https://smplibrary.bibliocommons.com/search"

class Result(NamedTuple):
    """A search result"""

    id: str
    title: str
    format: str
    isbns: list
    raw: dict

    @classmethod
    def from_page(cls, html: str) -> List["Result"]:
        """Given an HTML page, extract all search results"""
        jsonblob = BeautifulSoup(html, "html.parser").find_all("script", type="application/json")[0]
        d = json.loads(jsonblob.text)
        bibs = d["entities"]["bibs"]
        return [cls.from_blob(bibs[eid]) for eid in bibs]
        
    @classmethod
    def from_blob(cls, blob: dict) -> "Result":
        """Given a json blob defining a result on an HTML page, return a result"""
        info = blob["briefInfo"]
        return cls(
            id=info["id"],
            title=info.get("title"),
            format=info["format"],
            isbns=info["isbns"],
            raw=blob)

    def __str__(self) -> str:
        return ",".join([self.id, self.title, self.format, str(self.isbns)])


class SearchClient:
    """A client used for searching bay area public libraries"""

    def __init__(self, url="https://smplibrary.bibliocommons.com/v2/search"):
        self.url = url

    def search(self, keyword="", language=None, held_at_location=None,
        available_at_location=None, audience=None, content=None) -> Generator[Result, None, None]:
        """
        Search the Bay Area public library system for a resource.
        TODO: support more complicated keyword searches
        """
        d = dict(anywhere=f"({keyword})++")
        if language:
            d["isolanguage"] = language
        if held_at_location:
            d["branch"] = held_at_location
        if available_at_location:
            d["available"] = available_at_location
        if content:
            d["contentclass"] = content
        if audience:
            d["audience"] = audience

        q = dict(searchType="bl", suppress="true", custom_edit="false",
                pagination_page="1")
        q["query"] = "+".join([f'{k}:"{v}"' for k,v in d.items()])
        return self.search_results(q)

    def get_page(self, params: dict) -> requests.Response:
        """Return a http response for the search page given a search query"""
        resp = requests.get(self.url, params=params)
        resp.raise_for_status()
        return resp


    def search_results(self, params: dict) -> Generator[Result, None, None]:
        """Return a generator of search results given search params"""
        resp = self.get_page(params)
        for result in Result.from_page(resp.text):
            yield result

        b = BeautifulSoup(resp.text, "html.parser").find_all(class_="pagination-text")
        if len(b) == 0:
            logger.info("No pagination element. Zero results.")
            return 

        text = b[0].text
        m = re.match(r"^(\d+) to (\d+) of (.*) results$", text)
        if not m:
            logger.warning(f"Unable to extract number of search results from {text}")
            return

        i, j = int(m.group(1)), int(m.group(2))
        total = int(m.group(3).replace(",", ""))
        logger.info(f"Start is {i}, end is {j}, total is {total}")
        if j == total:
            logger.info("Reached end of iterator")
            return

        for h in range(2, total // 10 - 1):
            if h % 10 == 0:
                logger.info(f"On page {h}")
            params["pagination_page"] = int(params["pagination_page"]) + 1
            resp = self.get_page(params)
            for result in Result.from_page(resp.text):
                yield result
        

def remote_search_page() -> str:
    resp = requests.get(SMPL_SEARCH_URL)
    resp.raise_for_status()
    return resp.text

@lru_cache()
def search_page() -> str:
    """Return the HTML of the San Mateo public library search page"""
    with open(cached_search_page, "r") as f:
        return f.read()


def items(testid: str) -> List[str]:
    """
    Retrieve all search options for a San Mateo Public Library search page
    """
    langs = BeautifulSoup(search_page(), "html.parser").find_all(testid=testid)
    return [el.get("value") for el in langs[0].find_all("option")]


@lru_cache()
def languages() -> list:
    return items("select_languages")


@lru_cache()
def held_at_locations() -> list:
    return items("select_branchopts")


@lru_cache()
def available_at_locations() -> list:
    return items("select_availabl_branchopts")


@lru_cache()
def audiences() -> list:
    return items("select_audience")


@lru_cache()
def contents() -> list:
    return items("select_contents")


def limit(gen, threshold: int = 100) -> Generator:
    """Return a generator that returns at most threshold elements"""
    for i, item in enumerate(gen):
        if i == threshold:
            return
        yield item
