import requests
import os
import logging
from faunadb import query as q

from .function import fauna_client
from .database import add_user

def get_current_subscriptions(token):

    response = requests.get(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )

    return response.json()["data"]


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




def add_raid_subscription(token, login=None, userid=None, ignore_pending=None):
    """Subscribes to raids to and from the channel, if not already.
    returns whether subscription was added"""

    if login:
        userid, display_name = get_save_user_by_name(token, login)
    elif userid:
        userid, display_name = get_save_user_by_id(token, userid)
    else:
        raise Exception("no name or userid")

    if userid is None:
        return False



    existing_subscriptions = update_current_subscriptions(token, ignore_pending=ignore_pending)

    logging.info(f"existing subscriptons: {existing_subscriptions}")

    new_subscriptions = [{
        "type": "channel.raid",
        "version": "1",
        "condition": {
            "from_broadcaster_user_id": userid,
            "to_broadcaster_user_id": ""
        },
    }, {
        "type": "channel.raid",
        "version": "1",
        "condition": {
            "from_broadcaster_user_id": "",
            "to_broadcaster_user_id": userid
        },
    }]

    created = False
    for new_sub in new_subscriptions:
        if new_sub in existing_subscriptions:
            logging.info(f"already subscribed to {userid}")
        else:
            create_eventsub_subscription(token, new_sub)
            created = True

    return created





def update_current_subscriptions(token, ignore_pending=None):
    """deletes duplicate and failed verification subscriptions, returns all remaining subscriptions
    ignore_pending: id of a pending verification. Doesn't delete it.
    """

    subscriptions = get_current_subscriptions(token)

    existing_subscriptions = []

    for subscription in subscriptions:
        subscription_data = {
            "type": subscription["type"],
            "version": subscription["version"],
            "condition": subscription["condition"],
        }

        if subscription["id"] != ignore_pending and \
            subscription["status"] != "enabled" or subscription_data in existing_subscriptions:

            delete_subscription(token, subscription["id"])
        else:
            existing_subscriptions.append(subscription_data)

    return existing_subscriptions




def create_eventsub_subscription(token, new_subscription):

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
            "type": new_subscription["type"],
            "version": new_subscription["version"],
            "condition": new_subscription["condition"],
            "transport": {
                "method": "webhook",
                "callback": eventsuburl,
                "secret": os.environ["EVENTSUB_SECRET"]
            }
        },
    )

    if response.status_code != 202:
        raise Exception(f"Failed to create eventsub subscription: {response.status_code} {response.text}")

    logging.info(f"Created eventsub subscription: {response.json()}")





def delete_subscription(token, subscription_id):

    response = requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    logging.info(f"Deleted subscription response: {response}")



def get_save_user_by_name(token, name) -> tuple:

    response = requests.get(
        f"https://api.twitch.tv/helix/users?login={name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    try:
        userid = response.json()["data"][0]["id"]
        display_name = response.json()["data"][0]["display_name"]

        add_user(userid, display_name)

        return userid, display_name
    except (KeyError, IndexError):
        logging.info(f"failed to get user for name {name}")
        return None, None



def get_save_user_by_id(token, userid):

    response = requests.get(
        f"https://api.twitch.tv/helix/users?id={userid}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    try:
        userid = response.json()["data"][0]["id"]
        display_name = response.json()["data"][0]["display_name"]

        add_user(userid, display_name)

        return userid, display_name
    except (KeyError, IndexError):
        logging.info(f"failed to get user for id {userid}")
        return None, None











__all__ = [
    "get_current_subscriptions",
    "get_app_access_token",
    "add_raid_subscription",
    "delete_subscription"
]