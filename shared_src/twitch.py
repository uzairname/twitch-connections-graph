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




def add_raid_subscription(token, name=None, userid=None):
    """Subscribes to raids to and from the channel, if not already.
    returns whether subscription was added"""

    if userid is None:
        userid = get_save_userid(token, name)
        if userid is None:
            return False


    existing_subscriptions = update_current_subscriptions(token)

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





def update_current_subscriptions(token):
    """deletes duplicate and failed verification subscriptions, returns all remaining subscriptions"""

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



def get_save_userid(token, name):

    response = requests.get(
        f"https://api.twitch.tv/helix/users?login={name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    try:
        userid = response.json()["data"][0]["id"]
        name = response.json()["data"][0]["login"]

        add_user(userid, name)

        return userid
    except (KeyError, IndexError):
        logging.info(f"failed to get userid for {name}")
        return None











__all__ = [
    "get_current_subscriptions",
    "get_app_access_token",
    "add_raid_subscription",
    "delete_subscription"
]