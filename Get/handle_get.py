import logging
import os
import azure.functions as func

from faunadb import query as q
from shared_src import get_current_subscriptions, function, get_app_access_token, fauna_client, delete_subscription, get_users_ids_names
import pandas as pd

@function
def handle_get(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')


    token = get_app_access_token()
    subscriptions = get_current_subscriptions(token)

    action = req.params.get('action')
    # if action == "delete":
    #     for i in subscriptions:
    #         delete_subscription(token, i["id"])


    if action == "raids":
        # Downloads a csv file of all raids
        all_users = fauna_client.query(
            q.map_(
                lambda x: q.select(["data"], q.get(x)),
                q.paginate(q.documents(q.collection("twitch_raids"))),
            )
        )["data"]
        
        df = pd.DataFrame(all_users)
        csv_bytes = df.to_csv(index=False).encode()

        return func.HttpResponse(
            csv_bytes,
            status_code=200,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=raids.csv"
            }
        )
    
    if action == "users":
        
        users_ids = get_users_ids_names()
        csv_bytes = users_ids.to_csv(index=False).encode()

        return func.HttpResponse(
            csv_bytes,
            status_code=200,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=users.csv"
            }
        )


    else: 
        subscriptions_str = ""

        for i in subscriptions:
            subscriptions_str += f"{i}\n"

        return func.HttpResponse(f"All subscriptions:\n{subscriptions_str}")
