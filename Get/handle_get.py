import logging
import os
import azure.functions as func

from faunadb import query as q
from shared_src import get_current_subscriptions, function, get_app_access_token, fauna_client, delete_subscription, get_users_ids_names, get_raids_df, get_raids_graph
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
        df = get_raids_df()

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


    if action == "graph":
        
        try:
            level = int(req.params.get('level'))
        except:
            level = 1

        body = get_raids_graph(level)

        headers = {
            'Content-Disposition': f"attachment; filename=connections-graph.zip",
            'Content-Type': 'application/zip'
        }

        return func.HttpResponse(body, headers=headers, status_code=200)


        


    else: 
        subscriptions_str = ""

        for i in subscriptions:
            subscriptions_str += f"{i}\n"

        return func.HttpResponse(f"All subscriptions:\n{subscriptions_str}")
