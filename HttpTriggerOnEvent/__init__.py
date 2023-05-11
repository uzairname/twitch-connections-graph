import azure.functions as func
from handle_on_event import handle


def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle(req)

