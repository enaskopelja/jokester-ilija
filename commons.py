import os
from typing import Union

from slack import WebClient


def with_prefix_and_suffix(prefix: str, suffix: str):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return f"{prefix}{fun(*args, **kwargs)}{suffix}"

        return wrapper

    return decorator


def send_text(
    bot: str,
    text: str,
):
    slack_client = WebClient(token=os.environ[f"SLACK_{bot.upper()}_TOKEN"])
    response = slack_client.chat_postMessage(
        channel=f"#{os.environ['CHANNEL']}", text=text
    )
    assert response["ok"]


def send_image(bot: str, content: bytes, comment: str = ""):
    slack_client = WebClient(token=os.environ[f"SLACK_{bot.upper()}_TOKEN"])

    slack_client.files_upload(
        channels=f"#{os.environ['CHANNEL']}",
        initial_comment=comment,
        content=content,
    )


# pylint: disable = consider-alternative-union-syntax
def send(message: Union[str, dict], bot: str):
    if isinstance(message, str):
        send_text(
            bot=bot,
            text=message,
        )
        return

    try:
        send_image(
            bot=bot,
            **message,
        )
    except TypeError as error:
        raise TypeError(f"Unsupported message type {type(message)}") from error
