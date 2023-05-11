import logging
import os
import azure.functions as func

from faunadb import query as q
from faunadb.client import FaunaClient
from shared_src import get_current_subscriptions, function, get_app_access_token


@function
def handle_get(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')


    client = FaunaClient(secret=os.environ["FAUNADB_SECRET"])
    indexes = client.query(q.paginate(q.indexes()))

    # result = client.query(
    #     q.create_collection({"name": "notifications"})
    # )
    

    result = client.query(
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
