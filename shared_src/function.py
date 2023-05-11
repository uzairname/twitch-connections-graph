import functools
import azure.functions as func
import logging
import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk import capture_event, capture_exception


load_dotenv()

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    traces_sample_rate=1.0
)


def function(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):

        try:
            http_response = f(*args, **kwargs)
            capture_event({
                "message": f"{f.__name__} executed successfully",
                "level": "info",
                "extra": {
                    "function_name": f.__name__,
                }
            })
            return http_response
        except Exception as e:
            capture_exception(e)
            return func.HttpResponse(f"Exception: {e}")
        

    return wrapper


__all__ = ["function"]