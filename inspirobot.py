import requests


def inspirobot_image_uri() -> str:
    with requests.Session() as session:
        request_ = session.get("https://inspirobot.me/api?generate=true")
        return request_.text
