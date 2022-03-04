import json
import os
import logging

import requests as requests
from bs4 import BeautifulSoup
from slack import WebClient
from flask import Request, jsonify
import praw


def with_prefix_and_suffix(prefix: str, suffix: str):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return f"{prefix}{fun(*args, **kwargs)}{suffix}"

        return wrapper

    return decorator


def send_to_slack(message_type: str, bot: str):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            if message_type == "text":
                send_text(
                    bot=bot,
                    text=fun(*args, **kwargs),
                )

            if message_type == "image":
                content, comment = fun(*args, **kwargs)
                send_image(
                    bot=bot,
                    content=content,
                    comment=comment,
                )
            return

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


@send_to_slack(message_type="text", bot="boomer")
@with_prefix_and_suffix(
    prefix="> :confetti_ball: _*Živila e-Podravina i radio Banovina :wine_glass:*_ :confetti_ball:\n",
    suffix="\n:joy::joy::joy: ",
)
def boomer() -> str:
    with requests.Session() as s:
        source = "https://epodravina.hr"
        request_ = s.get(f"{source}/vic-dana")
        assert request_.ok

        joke_page = BeautifulSoup(
            s.get(f"{_parse_redirect(request_.content)}").content,
            'html.parser'
        )

    return _parse_article(joke_page)


@send_to_slack(message_type="text", bot="amer")
@with_prefix_and_suffix(prefix=":football: ", suffix="\n:joy:")
def amer() -> str:
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


def inspirobot_link() -> str:
    with requests.Session() as s:
        request_ = s.get("https://inspirobot.me/api?generate=true")
        return request_.text


@send_to_slack(message_type="image", bot="inspirobot")
def inspirobot() -> tuple[bytes, str]:
    with requests.Session() as s:
        return s.get(inspirobot_link(), stream=True).content, "Namaste :relieved:"


def send_text(
        bot: str,
        text: str,
):
    slack_client = WebClient(token=os.environ[f'SLACK_{bot.upper()}_TOKEN'])
    response = slack_client.chat_postMessage(
        channel=f"#{os.environ['CHANNEL']}",
        text=text
    )
    assert response["ok"]


def send_image(
        bot: str,
        content: bytes,
        comment: str = ""
):
    slack_client = WebClient(token=os.environ[f'SLACK_{bot.upper()}_TOKEN'])

    slack_client.files_upload(
        channels=f"#{os.environ['CHANNEL']}",
        initial_comment=comment,
        content=content,
    )


def main(request: Request):
    logging.info(request)
    request = request.get_data()
    logging.info(request)

    try:
        request_json = json.loads(request.decode())
        logging.info(request_json)
    except ValueError:
        return jsonify({
            "response_type": "ephemeral",
            "attachments": [
                {
                    "fallback": "Pure inspiration.",
                    "pretext": "Inspiration incoming :train:...",
                    "image_url": f"{inspirobot_link()}",
                }
            ]
        })

    for target in ["amer", "boomer", "inspirobot"]:
        globals()[target]()

    return "200"
