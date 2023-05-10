import logging
import os
import requests

import azure.functions as func



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


    # get someone's user id
    response = requests.get(
        "https://api.twitch.tv/helix/users?login=valorant",
        headers={
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    
    logging.info(f"user id: {response.json()}")


    eventsuburl = os.eniron["BASE_URL"] + "/api/eventsub"

    # create subscription
    response = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        json= {
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
        }
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
    return response.json()["access_token"]
