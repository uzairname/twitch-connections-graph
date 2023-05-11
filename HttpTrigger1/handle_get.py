import logging
import azure.functions as func


import requests
from shared_src import get_current_subscriptions, return_exception, get_app_access_token



@return_exception
def handle(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')

    token = get_app_access_token()
    subscriptions = get_current_subscriptions(token)

    return func.HttpResponse(f"All subscriptions: {subscriptions}")
