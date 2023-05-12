import functools
import os
import logging
import requests
from dotenv import load_dotenv
import azure.functions as func

from shared_src import add_raid_subscription, function, get_app_access_token, get_current_subscriptions, delete_subscription



@function
def handle_post(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('post subscription endpoint')


    if req.params.get("delete") == "yes" and req.params.get("userid"):
        token = get_app_access_token()
        for i in get_current_subscriptions(token):
            if i["condition"]["from_broadcaster_user_id"] == req.params.get("userid") or i["condition"]["to_broadcaster_user_id"] == req.params.get("userid"):
                delete_subscription(token, i["id"])
                logging.info("deleted subscription {}".format(i["id"]))

        return func.HttpResponse("Deleted subscriptions for userid {}".format(req.params.get("userid")))


    username = req.params.get('name')
    if not username:
        return func.HttpResponse(
            "no name in query string",
            status_code=400
        )

    token = get_app_access_token()

    # get an app access token



        
    added = add_raid_subscription(token, username)
    
    if added:
        return func.HttpResponse(f"subscribed to {username}")
    else:
        return func.HttpResponse(f"didn't subscribe to {username}")




