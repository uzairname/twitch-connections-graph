import logging
import azure.functions as func

import requests
from ..HttpTriggerPost.handle_post import get_current_subscriptions


def handle(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get endpoint function processed a request.')

    subscriptions = get_current_subscriptions()

    return func.HttpResponse(f"All subscriptions: {subscriptions}")