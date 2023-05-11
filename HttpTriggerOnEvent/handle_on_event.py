import logging
import azure.functions as func

import os
from dotenv import load_dotenv
import functools
import hmac
import hashlib

from faunadb import query as q
from faunadb.client import FaunaClient


def return_exception(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return func.HttpResponse(f"Exception: {e}")
    return wrapper






@return_exception
def handle(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('On event function processed a request.')

    # load_dotenv()
    # client = FaunaClient(secret=os.environ["FAUNADB_SECRET"])
    # indexes = client.query(q.paginate(q.indexes()))


    # verify the event message
    secret = "tempsecret"

    message_id = req.headers.get("Twitch-Eventsub-Message-Id")
    timestamp = req.headers.get("Twitch-Eventsub-Message-Timestamp")
    signature = req.headers.get("Twitch-Eventsub-Message-Signature")

    message = message_id.encode() + timestamp.encode() + req.get_body()
    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode(), message, hashlib.sha256
        ).hexdigest()
    )

    match = hmac.compare_digest(signature, expected_signature)

    if not match:
        logging.info('signature INVALUD')
        return func.HttpResponse(
            "Message signature does not match expected signature",
            status_code=403,
        )

    logging.info('signature valid')

    logging.info('got event {}'.format(req.get_json()))

    return func.HttpResponse(f"On event response")


