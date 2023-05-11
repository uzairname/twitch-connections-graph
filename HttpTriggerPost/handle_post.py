import functools
import os
import logging
import requests
from dotenv import load_dotenv
import azure.functions as func


def log_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            raise
    return wrapper


@log_exception
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
    
    # logging.info("user id: {}".format(userid))

    eventsuburl = os.environ["BASE_URL"] + "/api/eventsub"

    logging.info(f"eventsub url: {eventsuburl}")

    # create subscription
    response = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
            "Content-Type": "application/json"
        },
        json={
            "type": "channel.raid",
            "version": "1",
            "condition": {
                "from_broadcaster_user_id": userid
            },
            "transport": {
                "method": "webhook",
                "callback": eventsuburl,
                "secret": "tempsecret"
            }
        },
    )


    logging.info(f"Created eventsub subscription: {response.json()}")

    return func.HttpResponse(f"finished")



def get_app_access_token():
    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": os.environ["TWITCH_CLIENT_ID"],
            "client_secret": os.environ["TWITCH_CLIENT_SECRET"],
            "grant_type": "client_credentials",
        },
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get app access token: {response.status_code} {response.text}")


    logging.info("got app access token")
    logging.info(f"access token: {response.json()}")

    return response.json()["access_token"]
