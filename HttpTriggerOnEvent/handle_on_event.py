import azure.functions as func
from shared_src import function

import logging
import os

import hmac
import hashlib

from faunadb.client import FaunaClient
from faunadb import query as q




@function
def eventsub_callback(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('On event function processed a request.')


    # verify the event message
    secret = "tempsecret"

    message_id = req.headers.get("Twitch-Eventsub-Message-Id")
    timestamp = req.headers.get("Twitch-Eventsub-Message-Timestamp")
    signature = req.headers.get("Twitch-Eventsub-Message-Signature")

    message = message_id.encode() + timestamp.encode() + req.get_body()
    expected_signature = ("sha256=" + 
                          hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    )

    match = hmac.compare_digest(signature, expected_signature)

    if not match:
        logging.info('signature INVALUD')
        return func.HttpResponse(
            "Message signature does not match expected signature",
            status_code=403,
        )
    
    logging.info('signature valid')
    if req.headers.get("Twitch-Eventsub-Message-Type") == "notification":

        process_notification(req.get_json())

        return func.HttpResponse(
            "Processed event",
            status_code=200,
        )
    
    elif req.headers.get("Twitch-Eventsub-Message-Type") == "webhook_callback_verification":
        res = func.HttpResponse(
            req.get_json().get("challenge"),
            status_code=200,
        )
        logging.info(f'responding to a webhook_callback_verification{req.get_body()}\n\n{res}')

        return res
    
    elif req.headers.get("Twitch-Eventsub-Message-Type") == "revocation":
        logging.info(f"subscription revoked: {req.get_body()}")
        return func.HttpResponse(
            "revoked",
            status_code=200,
        )




def process_notification(body):

    client = FaunaClient(secret=os.environ["FAUNADB_SECRET"])

    result = client.query(
        q.create(
            q.collection("notifications"), 
            { 
                "data": body["event"]
            }
        )
    )
