import azure.functions as func
from .handle_post import handle_post


def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle_post(req)

