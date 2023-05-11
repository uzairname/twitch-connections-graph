import azure.functions as func
from .handle_on_event import eventsub_callback


def main(req: func.HttpRequest) -> func.HttpResponse:
    return eventsub_callback(req)

