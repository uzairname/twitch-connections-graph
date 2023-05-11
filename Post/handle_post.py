import functools
import os
import logging
import requests
from dotenv import load_dotenv
import azure.functions as func

from shared_src import add_raid_subscription, function, get_app_access_token



@function
def handle_post(req: func.HttpRequest) -> func.HttpResponse:
    load_dotenv()

    username = req.params.get('name')
    if not username:
        return func.HttpResponse(
            "no name in query string",
            status_code=400
        )
    
    logging.info('post subscription endpoint')

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

        
    added = add_raid_subscription(token, username)
    
    if added:
        return func.HttpResponse(f"subscribed to {username}")
    else:
        return func.HttpResponse(f"didn't subscribe to {username}")




