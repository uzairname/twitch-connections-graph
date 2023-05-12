import functools
import azure.functions as func
import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk import capture_event, capture_exception, add_breadcrumb, capture_message
from faunadb.client import FaunaClient


load_dotenv()

fauna_client = FaunaClient(secret=os.environ["FAUNADB_SECRET"])

requestnum = 0


def function(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            global requestnum
            requestnum += 1
            sentry_sdk.init(
                dsn=os.environ["SENTRY_DSN"],
                traces_sample_rate=1.0
            )
            add_breadcrumb(category="function", message=f"Request #{requestnum}. Executing {f.__name__}")
            http_response = f(*args, **kwargs)
            capture_message({
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


__all__ = ["function", "fauna_client"]