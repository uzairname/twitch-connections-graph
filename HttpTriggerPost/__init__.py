import azure.functions as func
from .handle_post import handle


def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle(req)

