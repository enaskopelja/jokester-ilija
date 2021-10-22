import os

import requests as requests
from bs4 import BeautifulSoup
from slack import WebClient
import praw


def with_emojis(prefix: str, suffix: str):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return f"{prefix}{fun(*args, **kwargs)}{suffix}"

        return wrapper

    return decorator


@with_emojis(":rocket: ", "\n:joy:")
def _boomer_joke():
    with requests.Session() as s:
        source = "https://net.hr"
        request_ = s.get(f"{source}/webcafe/vic-dana")
        assert request_.ok

        main_page = BeautifulSoup(request_.content, 'html.parser')
        redirect = main_page.find('a', href=True, class_="cardInner")['href']
        joke_page = BeautifulSoup(s.get(f"{source}{redirect}").content, 'html.parser')

        joke = joke_page.find('article', class_="article-body css-w9qdue")
        return '\n'.join(itm.getText() for itm in joke.childGenerator() if itm.name == 'p')


@with_emojis(":football: ", "\n:joy:")
def _amer_joke():
    r = praw.Reddit(
        client_id='zq5AGccUdiIiQWe2-PfNUA',
        client_secret='ns0ySf60Hhvj5SfiLM-e1fo_IBwzcQ',
        user_agent='amerilija'
    )
    sub = r.subreddit('jokes')
    top = sub.top(time_filter="day")
    top_post = next(top)
    while top_post.over_18:
        top_post = next(top)

    return f"{top_post.title}\n{top_post.selftext}"


def _send_joke(client, joke):
    response = client.chat_postMessage(
        channel=f"#{os.environ['CHANNEL']}",
        text=joke)
    assert response["ok"]


def send(
        type_,
):
    app = WebClient(token=os.environ[f'SLACK_{type_.upper()}_TOKEN'])
    joke = globals()[f'_{type_}_joke']()
    _send_joke(app, joke)


if __name__ == '__main__':
    send('boomer')
    send('amer')
