from sentry_sdk import add_breadcrumb


def log(message):

    add_breadcrumb(
        category="log",
        message=message,
        level="info",
    )


__all__ = ["log"]