import logging
import os
import functools
import azure.functions as func



def return_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return func.HttpResponse(f"Exception: {e}")
    return wrapper



@return_exception
def handle(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('got event {}'.format(req.get_json()))

    return func.HttpResponse(f"On event response")


