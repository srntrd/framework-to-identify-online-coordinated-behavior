import os
import sys
import time
import pickle
import dateutil.parser as dp
import pytz
import jsonlines
import random
import itertools
import numpy as np
from functools import reduce
import operator
import pandas as pd
import networkx as nx
import csv
import json
import community.community_louvain as community_louvain

random.seed(42)



def my_print(message):
    """
    Print log messages in a convenient form.
    :param message: (str) the message to print
    :return: None
    """
    ts = time.strftime('[%d %b %Y - %H:%M:%S]')
    script = "({0})".format(os.path.basename(os.path.basename(sys.argv[0])))
    print("{0} {1} {2}".format(ts, script, message))


def date_string_to_UTC(datestring):
    """
    Convert generic timezone-aware datestring to UTC datetime.
    :param datestring: (str) generic timezone-unaware datestring
    :return: (str) time-aware datetime
    """
    dt = dp.parse(datestring)
    return dt.astimezone(pytz.utc)


def UTC_to_timestamp(utc):
    """
    Convert UTC datetime to timestamp.
    :param utc: (datetime) time-aware datetime
    :return: (float) timestamp in seconds
    """
    return utc.timestamp()


def load_pickle(pickle_path):
    """
    Load a pickle serialized object.
    :param pickle_path: (string) the path to the pickle file.
    :return: the loaded object.
    """
    # my_print("Loading {0} ...".format(pickle_path))
    with open(pickle_path, 'rb') as handle:
        return pickle.load(handle)


def save_pickle(object_to_save, pickle_path):
    """
    Save an object in a serialized pickle file.
    :param object_to_save: (a python object) the object to save
    :param pickle_path: (string) the saving path
    :return: None
    """
    # my_print("Saving {0} to {1} ...".format(type(object_to_save), pickle_path))
    with open(pickle_path, 'wb') as handle:
        pickle.dump(object_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)


def save_df_to_jsonl(df, jsonl_path):

    d = df.to_dict(orient="records")
    with jsonlines.open(jsonl_path, mode="w") as handle:
        handle.write_all(d)
    my_print("Dataframe saved as JSONlines to {}.".format(jsonl_path))


def flatten_iterable(iterable):
    return itertools.chain.from_iterable(iterable)



def nested_get_value(dictionary, keys):
    try:
        return reduce(operator.getitem, keys, dictionary)
    except KeyError:
        return []





def load_graph_from_csvs(node_csv_path, edge_csv_path):
    my_print(f"Loading graph...")
    df_node = pd.read_csv(node_csv_path, dtype = {
        "user_id": str
    })
    df_node = df_node.set_index("user_id")
    dict_node = df_node.to_dict('index')
    dict_node = [(n, attr) for n, attr in dict_node.items()] #[(4, {"color": "red"}),(5,{"color": "green"})]
    df_edge = pd.read_csv(edge_csv_path, dtype = {
        "source": str,
        "target": str
    })
    df_edge = df_edge.set_index(['source', 'target'])
    dict_edge = df_edge.to_dict('index')
    dict_edge = [(s, t, attr) for (s, t), attr in dict_edge.items()] # [(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})]
    G = nx.Graph()
    G.add_nodes_from(dict_node)
    G.add_edges_from(dict_edge)

    return G


def compute_tfidf_tagclouds(ids_to_consider, ids, corpus, dictionary, model):
    indices = []
    ids_skipped = 0
    for id_to_consider in ids_to_consider:
        try:
            indices.append(ids.index(id_to_consider))
        except:
            ids_skipped += 1

    vector = np.zeros(len(dictionary))

    for i in indices:
        try: # if user has used hashtags
            j, v = zip(*model[corpus[i]])  # apply model to the i-th corpus document
            vector[tuple([j])] += v
        except:
            None


    vector /= len(indices)

    return {dictionary[k]: tfidf for k, tfidf in enumerate(vector)}

def compute_seed_comm(node_csv_path, edge_csv_path, louvain_resolution, output_node_csv_path):
    """ Extracts the communities with the input louvain_resolution parameter.
        For each user, we save the community of belonging under the column called "modularity_class", in the node_list.csv.
        Here, we extract the communities using networkx and louvain, but one could alternatively extract community using viz softwares (e.g., gephi) that allow to visually see the communities and play with the louvain parameters, and export a csv with the header: user_id, modularity_class.
    """
    G = load_graph_from_csvs(node_csv_path, edge_csv_path)
    my_print("Extracting louvain communities...")
    user_comm_dict = community_louvain.best_partition(G, resolution = louvain_resolution, randomize=False, random_state=0)
    nx.set_node_attributes(G, values = user_comm_dict, name = 'modularity_class')
    # Create csv file node_csv_path to save node list with community (modularity_class) info
    with open(output_node_csv_path, "w") as handle:
        writer = csv.writer(handle, quotechar = '"', quoting = csv.QUOTE_NONNUMERIC)
        writer.writerow(["user_id", "modularity_class"])
        for v in G.nodes(data = True):
            writer.writerow([v[0], v[1]['modularity_class']])
    my_print(f"Extracted louvain communities with resolution {louvain_resolution} saved to (modularity class) in {output_node_csv_path}")

    return output_node_csv_path


def parse_seed_comm(node_csv_path, output_path):
    """ Renames the communities such that the name (i.e., number) of the communities is correlated to their size (i.e., number of users).
        For instance, we want the community "0" to be the largest community, and so on.
        This renaming step is needed because, when extracting the communities, the algorithm assigns a name (i.e., number) to different communities depending on the order in which the nodes are considered.
        We save the new name under the column "modularity_def" in the same file.
    """
    my_print("Loading seed partition from {}.".format(node_csv_path))
    df = pd.read_csv(node_csv_path, dtype={"user_id": str})
    df_count = df.groupby("modularity_class").size().sort_values(ascending=False).reset_index(name='count')

    my_print("Parsing...")
    seed_mod_dict = dict()

    df["modularity_def"] = -1

    for i, row in df_count.iterrows():
        seed_mod_dict.setdefault(i, df.loc[df["modularity_class"]==row["modularity_class"], "user_id"].to_list())
        df.loc[df["modularity_class"]==row["modularity_class"], "modularity_def"] = i

    df[["user_id","modularity_def"]].to_csv(node_csv_path, index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)

    my_print("Nodes file saved to {}".format(node_csv_path))

    with open(output_path, "w") as handle:
        json.dump(seed_mod_dict, handle)

    my_print("Formatted seed partition saved to {}".format(output_path))

    return output_path

