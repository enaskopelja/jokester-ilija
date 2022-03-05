import requests
from flask import Flask, jsonify

from amer import fetch_joke as amer_joke
from boomer import fetch_joke as boomer_joke
from commons import send
from inspirobot import inspirobot_image_uri

app = Flask(__name__)


def _get_image_bytes(uri: str) -> bytes:
    with requests.Session() as session:
        return session.get(uri).content


@app.errorhandler(400)
def client_error(error):
    return jsonify(error=str(error)), 400


def image_response(
    response_type: str,
    pretext: str,
    fallback: str,
    image_url: str,
):
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
):
    return jsonify(
        {
            "response_type": response_type,
            "text": text,
        }
    )


@app.route("/boomer-me", methods=["POST", "GET"])
def boomer_me():
    return text_response(response_type="ephemeral", text=boomer_joke()), "200"


@app.route("/boomer-us", methods=["POST", "GET"])
def boomer_us():
    return text_response(response_type="in_channel", text=boomer_joke()), "200"


@app.route("/amer-me", methods=["POST", "GET"])
def amer_me():
    return text_response(response_type="ephemeral", text=amer_joke(censor=False)), "200"


@app.route("/amer-us", methods=["POST", "GET"])
def amer_us():
    return (
        text_response(response_type="in_channel", text=amer_joke(censor=False)),
        "200",
    )


@app.route("/inspire-me", methods=["POST", "GET"])
def inspire_me():
    return (
        image_response(
            response_type="ephemeral",
            pretext="Inspiration incoming :train:...",
            fallback="Pure inspiration.",
            image_url=inspirobot_image_uri(),
        ),
        "200",
    )


@app.route("/inspire-us", methods=["POST", "GET"])
def inspire_us():
    return (
        image_response(
            response_type="in_channel",
            pretext="Inspiration incoming :train:...",
            fallback="Pure inspiration.",
            image_url=inspirobot_image_uri(),
        ),
        "200",
    )


@app.route("/", methods=["POST"])
def daily():
    send(
        bot="amer",
        message=amer_joke(),
    )

    send(
        bot="boomer",
        message=boomer_joke(),
    )

    image_uri = inspirobot_image_uri()
    send(
        bot="inspirobot",
        message={
            "content": _get_image_bytes(image_uri),
            "comment": "Namaste :relieved:",
        },
    )

    return "200"


def main():
    app.run(host="0.0.0.0", port=80, debug=True)


if __name__ == "__main__":
    main()
