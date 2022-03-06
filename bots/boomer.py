import requests
from bs4 import BeautifulSoup

from .commons import with_prefix_and_suffix


def _parse_boomer_redirect(content: bytes) -> str:
    main_page = BeautifulSoup(content, "html.parser")
    for a_tag in main_page.findAll("a", href=True):
        if a_tag.get("title", "").startswith("[VIC DANA]"):
            return a_tag["href"]

    raise ValueError("No joke found")


def _parse_boomer_article(page: BeautifulSoup) -> str:
    article = page.find("div", class_="td-post-content")
    return "\n".join(
        itm.getText() for itm in article.childGenerator() if itm.name == "p"
    )


@with_prefix_and_suffix(
    prefix="> :confetti_ball: "
    "_*Živila e-Podravina i radio Banovina "
    ":wine_glass:*_ :confetti_ball:\n",
    suffix="\n:joy::joy::joy: ",
)
def fetch_joke() -> str:
    with requests.Session() as session:
        source = "https://epodravina.hr"
        request_ = session.get(f"{source}/vic-dana")
        assert request_.ok

        joke_page = BeautifulSoup(
            session.get(f"{_parse_boomer_redirect(request_.content)}").content,
            "html.parser",
        )

    return _parse_boomer_article(joke_page)
