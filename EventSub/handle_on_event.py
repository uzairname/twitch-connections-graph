import azure.functions as func
from shared_src import function

import logging
import os

import hmac
import hashlib

from shared_src import fauna_client, add_raid_subscription, get_app_access_token
from faunadb import query as q





@function
def eventsub_callback(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('On event function processed a request.')



    # verify the event message
    secret = os.environ["EVENTSUB_SECRET"]

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
        logging.info('received notification')
        # process_notification(req)

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




def process_notification(req):

    # check for duplicate message

    if fauna_client.query(q.exists(q.match(q.index("twitch_raids_by_message_id"), req.headers.get("Twitch-Eventsub-Message-Id")))):
        logging.info("duplicate message")
        return
    
    event = req.get_json().get("event")

    from_id = event.get("from_broadcaster_user_id")
    from_name = event.get("from_broadcaster_user_name")
    to_id = event.get("to_broadcaster_user_id")
    to_name = event.get("to_broadcaster_user_name")

    logging.info(f"Got raid. from: {from_name} ({from_id}), to: {to_name} ({to_id})")
    
    data = {
        "message_id": req.headers.get("Twitch-Eventsub-Message-Id"),
        "message_timestamp": req.headers.get("Twitch-Eventsub-Message-Timestamp"),
        "raid_name": f"{from_name} raided {to_name}",
        "from": from_id,
        "to": to_id,
        "viewers": event.get("viewers"),
    }

    result = fauna_client.query(
        q.create(
            q.collection("twitch_raids"), 
            { "data": data }
        )
    )


    token = get_app_access_token()


    added = add_raid_subscription(token, userid=from_id)
    logging.info(f"By raid subscribed to {from_name}: {added}")
    added = add_raid_subscription(token, userid=to_id, ignore_pending=from_id)
    logging.info(f"By raid subscribed to {to_name}: {added}")



