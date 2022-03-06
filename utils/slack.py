import os
from typing import Union

from flask import Response, jsonify
from slack import WebClient


def _send_text(
    bot: str,
    text: str,
) -> None:
    slack_client = WebClient(token=os.environ[f"SLACK_{bot.upper()}_TOKEN"])
    response = slack_client.chat_postMessage(
        channel=f"#{os.environ['CHANNEL']}", text=text
    )
    assert response["ok"]


def _send_image(bot: str, content: bytes, comment: str = "") -> None:
    slack_client = WebClient(token=os.environ[f"SLACK_{bot.upper()}_TOKEN"])

    slack_client.files_upload(
        channels=f"#{os.environ['CHANNEL']}",
        initial_comment=comment,
        content=content,
    )


# pylint: disable = consider-alternative-union-syntax
def send(message: Union[str, dict], bot: str) -> None:
    if isinstance(message, str):
        _send_text(
            bot=bot,
            text=message,
        )
        return

    try:
        _send_image(
            bot=bot,
            **message,
        )
    except TypeError as error:
        raise TypeError(f"Unsupported message type {type(message)}") from error


def image_response(
    response_type: str,
    pretext: str,
    fallback: str,
    image_url: str,
) -> Response:
    return jsonify(
        {
            "response_type": response_type,
            "attachments": [
                {
                    "fallback": fallback,
                    "pretext": pretext,
                    "image_url": image_url,
                }
            ],
        }
    )


def text_response(
    response_type: str,
    text: str,
) -> Response:
    return jsonify(
        {
            "response_type": response_type,
            "text": text,
        }
    )
