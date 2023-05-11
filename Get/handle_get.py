import logging
import os
import azure.functions as func

from faunadb import query as q
from shared_src import get_current_subscriptions, function, get_app_access_token, fauna_client


@function
def handle_get(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')



    result = fauna_client.query(
        q.create(
            q.collection("notifications"), 
            { 
                "data": {"name": "test"}
            }
        )
    )

    logging.info(result)

    token = get_app_access_token()
    subscriptions = get_current_subscriptions(token)

    return func.HttpResponse(f"All subscriptions: {subscriptions}")
