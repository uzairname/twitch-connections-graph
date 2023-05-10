import logging
import os
import functools

import azure.functions as func



def log_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            raise
    return wrapper



@log_exception
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('on event endpoint')


    return func.HttpResponse(f"On event response")


