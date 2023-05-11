import functools
import os
import logging
import requests
from dotenv import load_dotenv
import azure.functions as func

from shared_src import get_current_subscriptions, return_exception, get_app_access_token





@return_exception
def handle(req: func.HttpRequest) -> func.HttpResponse:
    load_dotenv()

    
    logging.info('Eventsub endpoint')

    # get an app access token
    token = get_app_access_token()

    # Get Twitch EventSub Subscriptions
    response = requests.get(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )

    logging.info(f"Got eventsub subscriptions: {response.json()}")

    # get someone's user id
    response = requests.get(
        "https://api.twitch.tv/helix/users?login=valorant",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    userid = response.json()["data"][0]["id"]
    

    subscriptions = get_current_subscriptions(token)

    existing_subscriptions = []

    for subscription in subscriptions:
        subscription_data = {
            "type": subscription["type"],
            "version": subscription["version"],
            "condition": subscription["condition"],
        }

        if subscription["status"] != "enabled":
            delete_subscription(token, subscription["id"])
        elif subscription_data in existing_subscriptions:
            delete_subscription(token, subscription["id"])
        else:
            existing_subscriptions.append(subscription_data)

    logging.info(f"existing subscriptons: {existing_subscriptions}")


    new_subcription = {
        "type": "channel.raid",
        "version": "1",
        "condition": {
            "from_broadcaster_user_id": userid,
            "to_broadcaster_user_id": ""
        },
    }

    if new_subcription in existing_subscriptions:
        logging.info("already subscribed")
        return func.HttpResponse(f"already subscribed")


    eventsuburl = os.environ["BASE_URL"] + "/api/eventsub"
    # create subscription
    response = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
            "Content-Type": "application/json"
        },
        json={
            "type": new_subcription["type"],
            "version": new_subcription["version"],
            "condition": new_subcription["condition"],
            "transport": {
                "method": "webhook",
                "callback": eventsuburl,
                "secret": "tempsecret"
            }
        },
    )


    logging.info(f"Created eventsub subscription: {response.json()}")

    return func.HttpResponse(f"finished")



def delete_subscription(token, subscription_id):

    response = requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    logging.info(f"Deleted subscription response: {response}")
