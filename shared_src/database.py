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

    # get all documents in twitch_raids collection
    faunadb_max_page_length = 100000

    all_raids = fauna_client.query(
        q.map_(
            lambda x: q.select(["data"], q.get(x)),
            q.paginate(q.documents(q.collection("twitch_raids")), size=faunadb_max_page_length),
        )
    )["data"]

    logging.info(len(all_raids))

    df = pd.DataFrame(all_raids)
    df["message_timestamp"] = pd.to_datetime(df["message_timestamp"], utc=True)
    df = df.sort_values("message_timestamp")
    df = df[abs(df['message_timestamp'].shift(1) - df['message_timestamp']) > timedelta(seconds=1)]

    return df



def get_raids_graph(level: int = 1) -> bytes:

    data = get_raids_df()

    graph = {}
    groups = {} # {name: [group, time discovered, path]}


    def add_edge(from_, to, group_number, timestamp):
        from_known = from_ in groups
        to_known = to in groups

        if not from_known and not to_known:
            groups[from_] = [chr(group_number+97), timestamp, f"{to} <- **{from_}**"]
            groups[to] = [chr(group_number+97), timestamp, f"{from_} -> **{to}**"]
            group_number += 1
        elif not to_known:
            groups[to] = [groups[from_][0], timestamp, f"{groups[from_][2]} -> **{to}**"]
        elif not from_known:
            groups[from_] = [groups[to][0], timestamp, f"{groups[to][2]} <- **{from_}**"]

        try:
            graph[from_][to] += 1
            # from and to exist
        except KeyError:
            try:
                graph[from_][to] = 1
                # from exists, to doesn't
            except KeyError:
                graph[from_] = {to: 1}
                # from doesn't exist

        return group_number


    group_number = 0
    for _, row in data.iterrows():
        from_name = row["raid_name"].split(' ')[0]
        to_name = row["raid_name"].split(' ')[-1]
        group_number = add_edge(from_name, to_name, group_number, row["message_timestamp"])


    buffer = io.BytesIO()
    with tempfile.TemporaryDirectory(dir=tempfile.gettempdir()) as tempdir:
        for user, info in groups.items():
            with open(os.path.join(tempdir, f"{user}.md"), "w") as f:
                txt = "\n"
                txt += f"#{info[0]}\n"
                txt += f"{info[2]}\n\n"

                if to_users := graph.get(user):
                    for to_user, weight in to_users.items():
                        if (weight >= level):
                            txt += f"[[{to_user}]] ({weight})\n"
                txt += f"\nDiscovered at {info[1]}\n"
                f.write(txt)
        
        
        with open(os.path.join(tempdir, "0 METADATA.md"), "w") as f:
            txt = f"Graph of raids with weight >= {level},\nCreated on {str(datetime.now().date())} {str(datetime.now().time())}\n\n"
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




def number_to_multiplicative(num):
    if num == 1:
        return "once"
    elif num == 2:
        return "twice"
    elif num == 3:
        return "thrice"
    else:
        return f"{num} times"



__all__ = [
    "get_users_ids_names",
    "add_user",
    "get_raids_df",
    "get_raids_graph",
]