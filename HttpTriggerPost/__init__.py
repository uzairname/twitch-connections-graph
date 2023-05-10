import logging
import os
import requests
import functools

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
def main(req: func.HttpRequest) -> func.HttpResponse:
    
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
    
    logging.info("user id: {}".format(response.json()["data"][0]["id"]))

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
            "type": "channel.raid",
            "version": "1",
            "condition": {
                "broadcaster_user_id": "123456789"
            },
            "transport": {
                "method": "webhook",
                "callback": eventsuburl,
                "secret": os.environ["EVENTSUB_SECRET"]
            }
        },
    )


    logging.info(f"Got eventsub subscriptions: {response.json()}")

    return func.HttpResponse(f"Got eventsub subscriptions: {response.json()}")





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

    logging.info(f"Got app access token: {response.json()['access_token']}")

    return response.json()["access_token"]
