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


def _parse_nethr_redirect(content: requests.Response.content) -> str:
    main_page = BeautifulSoup(content, 'html.parser')
    return main_page.find('a', href=True, class_="cardInner")['href']


def _parse_nethr_article(page: BeautifulSoup) -> str:
    article = page.find('article', class_="article-body css-w9qdue")
    return '\n'.join(itm.getText() for itm in article.childGenerator() if itm.name == 'p')


@with_prefix_and_suffix(":rocket: ", "\n:joy:")
def _boomer_joke() -> str:
    with requests.Session() as s:
        source = "https://net.hr"
        request_ = s.get(f"{source}/webcafe/vic-dana")
        assert request_.ok

        joke_page = BeautifulSoup(
            s.get(f"{source}{_parse_nethr_redirect(request_.content)}").content,
            'html.parser'
        )

        return _parse_nethr_article(joke_page)


@with_prefix_and_suffix(
    prefix="> :mega: _*DISCLAIMER:*_ :mega:\n"
           "> _Boomer Ilija je na servisu do daljnjega,_ \n"
           "> _u meduvremenu uzivajte u dnevnom horoskopu. :crystal_ball:_ \n"
           "> _Ovo je horoskop bas za vas, nema diskriminacije po datumu rodenja._\n",
    suffix=""
)
def _horoscope() -> str:
    with requests.Session() as s:
        source = "https://net.hr"
        sign = random.choice(
            ['ovan', 'lav', 'strijelac', 'jarac', 'djevica', 'bik', 'blizanci', 'vodenjak', 'vaga', 'ribe', 'škorpion',
             'rak'])

        request_ = s.get(f"{source}/webcafe/dnevni-horoskop/{sign}")
        assert request_.ok

        horoscope_page = BeautifulSoup(
            s.get(f"{source}{_parse_nethr_redirect(request_.content)}").content,
            'html.parser'
        )

        text = _parse_nethr_article(horoscope_page)
        return text.replace(
            'Ljubav', '*Ljubav* :man-heart-man:\n'
        ).replace(
            'Posao', '*Posao* :briefcase:\n'
        ).replace(
            'Zdravlje',
            '*Zdravlje :pill: *\n'
        )


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


def main():
    # send(_boomer_joke(), 'boomer')
    send(_horoscope(), 'boomer')
    send(_amer_joke(), 'amer')


if __name__ == '__main__':
    main()

