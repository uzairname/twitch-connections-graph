import functools
import azure.functions as func
import logging

def return_exception(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return func.HttpResponse(f"Exception: {e}")
    return wrapper
