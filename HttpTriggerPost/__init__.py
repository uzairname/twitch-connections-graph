import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HttpTriggerPost processed a request.')

    return func.HttpResponse(f"Post function response (2)")


