import requests
import os
import logging



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




def add_raid_subscription(token, name):
    """returns whether subscription was added"""

    # get someone's user id
    response = requests.get(
        f"https://api.twitch.tv/helix/users?login={name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    try:
        userid = response.json()["data"][0]["id"]
    except KeyError:
        logging.info(f"failed to get userid for {name}")
        return False
    

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
        return False
        


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

    return True





def delete_subscription(token, subscription_id):

    response = requests.delete(
        f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Client-Id": os.environ["TWITCH_CLIENT_ID"],
        },
    )
    logging.info(f"Deleted subscription response: {response}")






__all__ = [
    "get_current_subscriptions",
    "get_app_access_token",
    "add_raid_subscription",
]