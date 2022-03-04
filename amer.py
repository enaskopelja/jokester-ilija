import praw

from commons import with_prefix_and_suffix


def _fetch_censored_joke(top):
    top_post = next(top)

    # pylint: disable = while-used
    while top_post.over_18 or len(top_post.selftext) > 80:
        top_post = next(top)

    return top_post


def _construct_response(post):
    return f"{post.title}\n{post.selftext}"


@with_prefix_and_suffix(prefix=":football: ", suffix="\n:joy:")
def fetch_joke(censor: bool = True) -> str:
    reddit_client = praw.Reddit(
        client_id="zq5AGccUdiIiQWe2-PfNUA",
        client_secret="ns0ySf60Hhvj5SfiLM-e1fo_IBwzcQ",
        user_agent="amerilija",
    )
    sub = reddit_client.subreddit("jokes")
    top = sub.top(time_filter="day")

    if censor:
        return _construct_response(_fetch_censored_joke(top))

    return _construct_response(next(top))
