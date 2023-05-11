import logging
import azure.functions as func

import requests
from shared_src.twitch import get_current_subscriptions


def handle(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')

    subscriptions = get_current_subscriptions()

    return func.HttpResponse(f"All subscriptions: {subscriptions}")
