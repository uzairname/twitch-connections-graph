import functools
import azure.functions as func
import logging
import os
import sentry_sdk
from sentry_sdk import capture_event


sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    traces_sample_rate=1.0
)


def function(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):

        try:
            result = f(*args, **kwargs)
            capture_event({
                "message": "function executed successfully",
                "level": "info",
                "extra": {
                    "function_name": f.__name__,
                }
            })
            return result
        except Exception as e:
            logging.exception(e)
            return func.HttpResponse(f"Exception: {e}")
        

    return wrapper
