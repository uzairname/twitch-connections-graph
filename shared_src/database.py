import logging
from faunadb import query as q

import pandas as pd
from datetime import timedelta, datetime
import os
import tempfile
import zipfile
import io

from .function import fauna_client


def get_users_ids_names():
    """returns a dataframe of usernames and user ids from the database"""

    all_users = fauna_client.query(
        q.map_(
            lambda x: q.select(["data"], q.get(x)),
            q.paginate(q.documents(q.collection("twitch_users"))),
        )
    )["data"]
    
    return pd.DataFrame(all_users)


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



def get_raids_df():
    all_raids = fauna_client.query(
            q.map_(
                lambda x: q.select(["data"], q.get(x)),
                q.paginate(q.documents(q.collection("twitch_raids"))),
            )
        )["data"]
    
    df = pd.DataFrame(all_raids)
    df["message_timestamp"] = pd.to_datetime(df["message_timestamp"], utc=True)
    df = df.sort_values("message_timestamp")
    df = df[abs(df['message_timestamp'].shift(1) - df['message_timestamp']) > timedelta(seconds=1)]

    return df



def get_raids_graph(level: int = 1) -> bytes:

    data = get_raids_df()

    graph = {}

    def add_edge(from_, to):
        try:
            graph[from_][to] += 1
        except KeyError:
            try:
                graph[from_][to] = 1
            except KeyError:
                graph[from_] = {to: 1}

    for i, row in data.iterrows():
        from_name = row["raid_name"].split(' ')[0]
        to_name = row["raid_name"].split(' ')[-1]
        add_edge(from_name, to_name)


    buffer = io.BytesIO()
    with tempfile.TemporaryDirectory(dir=tempfile.gettempdir()) as tempdir:
        for user, to in graph.items():
            with open(os.path.join(tempdir, f"{user}.md"), "w") as f:
                txt = ""
                for to_user, weight in to.items():
                    if (weight >= level):
                        txt += f"[[{to_user}]] ({weight})\n"
                f.write(txt)
        with open(os.path.join(tempdir, "0 METADATA.md"), "w") as f:
            txt = f"Graph of raids with weight >= {level}, created on {str(datetime.now().date())}"
            f.write(txt)

        # Create a zip file in memory from the temporary directory
        
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for root, dirs, files in os.walk(tempdir):
                for file in files:
                    zip_file.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), tempdir),
                    )    


    return buffer.getvalue()






__all__ = [
    "get_users_ids_names",
    "add_user",
    "get_raids_df",
    "get_raids_graph",
]