import logging
import os
import requests

import azure.functions as func



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Eventsub endpoint')


    # get an app access token
    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": os.environ["TWITCH_CLIENT_ID"],
            "client_secret": os.environ["TWITCH_CLIENT_SECRET"],
            "grant_type": "client_credentials",
        },
    )

    if response.status_code != 200:
        return func.HttpResponse(
            "Failed to get app access token",
            status_code=response.status_code,
        )

    token = response.json()["access_token"]


    # Get Twitch EventSub Subscriptions
    response = requests.get(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )

    logging.info(f"Got eventsub subscriptions: {response.json()}")


    return func.HttpResponse(f"Got eventsub subscriptions: {response.json()}")

