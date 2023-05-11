import logging
import os
import azure.functions as func

from faunadb import query as q
from shared_src import get_current_subscriptions, function, get_app_access_token, fauna_client, delete_subscription, get_users_ids_names


@function
def handle_get(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')


    token = get_app_access_token()
    subscriptions = get_current_subscriptions(token)

    action = req.params.get('action')
    if action == "delete":
        for i in subscriptions:
            delete_subscription(token, i["id"])


    users_ids = get_users_ids_names()
    subscriptions_str = ""

    for i in subscriptions:
        subscriptions_str += f"{i}\n"

    subscriptions_str += f"\n\n{users_ids}"

    return func.HttpResponse(f"All subscriptions:\n{subscriptions_str}")
