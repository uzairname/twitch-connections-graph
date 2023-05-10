import logging
import os
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HttpTriggerPost processed a request.')

    val = os.environ.get('TEST_VAR')
    logging.info(f"TEST_VAR: {val}")

    return func.HttpResponse(f"Post function response (TEST_VAR: {val})")

