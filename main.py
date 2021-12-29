import os
import random

import requests as requests
from bs4 import BeautifulSoup
from slack import WebClient
import praw


def with_prefix_and_suffix(prefix: str, suffix: str):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return f"{prefix}{fun(*args, **kwargs)}{suffix}"

        return wrapper

    return decorator


def _parse_redirect(content: requests.Response.content) -> str:
    main_page = BeautifulSoup(content, 'html.parser')
    for a_tag in main_page.findAll('a', href=True):
        if a_tag.get('title', '').startswith('[VIC DANA]'):
            return a_tag['href']

    raise ValueError('No joke found')


def _parse_article(page: BeautifulSoup) -> str:
    article = page.find("div", class_="td-post-content")
    return '\n'.join(itm.getText() for itm in article.childGenerator() if itm.name == 'p')


@with_prefix_and_suffix(
    prefix="> :confetti_ball: _*Živila e-Podravina i radio Banovina :wine_glass:*_ :confetti_ball:\n",
    suffix="\n:joy::joy::joy: "
)
def _boomer_joke() -> str:
    with requests.Session() as s:
        source = "https://epodravina.hr"
        request_ = s.get(f"{source}/vic-dana")
        assert request_.ok

        joke_page = BeautifulSoup(
            s.get(f"{_parse_redirect(request_.content)}").content,
            'html.parser'
        )

    return _parse_article(joke_page)


@with_prefix_and_suffix(":football: ", "\n:joy:")
def _amer_joke() -> str:
    r = praw.Reddit(
        client_id='zq5AGccUdiIiQWe2-PfNUA',
        client_secret='ns0ySf60Hhvj5SfiLM-e1fo_IBwzcQ',
        user_agent='amerilija'
    )
    sub = r.subreddit('jokes')
    top = sub.top(time_filter="day")

    top_post = next(top)
    while top_post.over_18 or len(top_post.selftext) > 80:
        top_post = next(top)

    return f"{top_post.title}\n{top_post.selftext}"


def send(
        message: str,
        bot: str,
):
    slack_client = WebClient(token=os.environ[f'SLACK_{bot.upper()}_TOKEN'])
    response = slack_client.chat_postMessage(
        channel=f"#{os.environ['CHANNEL']}",
        text=message)
    assert response["ok"]


def main(*args, **kwargs):
    send(_boomer_joke(), 'boomer')
    send(_amer_joke(), 'amer')


if __name__ == '__main__':
    main()
