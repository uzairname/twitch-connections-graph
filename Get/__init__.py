import azure.functions as func
from .handle_get import handle_get


def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle_get(req)
