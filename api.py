import requests
from flask import Flask, Response, jsonify

from bots import amer, boomer, inspirobot
from utils.slack import image_response, send, text_response

app = Flask(__name__)


def _get_image_bytes(uri: str) -> bytes:
    with requests.Session() as session:
        return session.get(uri).content


def _response_type_from_target(target: str) -> str:
    if target not in {"us", "me"}:
        raise ValueError(f"Unsupported target: {target}")

    return "in_channel" if target == "us" else "ephemeral"


@app.errorhandler(400)
def client_error(error):
    return jsonify(error=str(error)), 400


@app.route("/boomer-<string:target>", methods=["POST", "GET"])
def boomer_(target: str) -> tuple[Response, str]:
    return (
        text_response(
            response_type=_response_type_from_target(target),
            text=boomer.fetch_joke(),
        ),
        "200",
    )


@app.route("/amer-<string:target>", methods=["POST", "GET"])
def amer_(target: str) -> tuple[Response, str]:
    return (
        text_response(
            response_type=_response_type_from_target(target),
            text=amer.fetch_joke(censor=False),
        ),
        "200",
    )


@app.route("/inspire-<string:target>", methods=["POST", "GET"])
def inspire(target: str) -> tuple[Response, str]:
    return (
        image_response(
            response_type=_response_type_from_target(target),
            pretext="Inspiration incoming :train:...",
            fallback="Pure inspiration.",
            image_url=inspirobot.image_uri(),
        ),
        "200",
    )


@app.route("/daily", methods=["GET"])
def daily() -> str:
    send(
        bot="amer",
        message=amer.fetch_joke(),
    )

    send(
        bot="boomer",
        message=boomer.fetch_joke(),
    )

    image_uri = inspirobot.image_uri()
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
