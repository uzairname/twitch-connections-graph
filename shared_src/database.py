import logging
from faunadb import query as q
import pandas as pd

from .function import fauna_client


def get_users_ids_names():
    """returns a dataframe of usernames and user ids from the database"""

    all_users = fauna_client.query(
        q.map_(
            lambda x: q.select(["data"], q.get(x)),
            q.paginate(q.documents(q.collection("twitch_users"))),
        )
    )["data"]
    
    return pd.DataFrame(all_users).set_index("id")


def add_user(userid, login):

    # add if userid doesn't exist
    if fauna_client.query(q.exists(q.match(q.index("twitch_users_by_id"), userid))):
        logging.info(f"User {userid} already exists in database")
        return

    fauna_client.query(
        q.create(
            q.collection("twitch_users"),
            {"data": {"id": userid, "name": login}},
        )
    )


__all__ = [
    "get_users_ids_names",
    "add_user"
]