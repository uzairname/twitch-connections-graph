import functools
import os
import logging
import requests
from dotenv import load_dotenv
import azure.functions as func

from shared_src import add_raid_subscription, return_exception, get_app_access_token



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

    added = add_raid_subscription(token, "valorant")
    
    if added:
        return func.HttpResponse(f"finished")
    else:
        return func.HttpResponse(f"already subscribed")




