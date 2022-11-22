import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from include.backbone import disparity_filter
import networkx as nx
import csv
from include.lib import my_print
import pandas as pd
from pathlib import Path


def add_multiscale_backbone_to_edgelist(node_csv_path, edge_csv_path):
    """
        Compute backbone data

        :param node_csv_path: the path of the csv containing the nodes (header: user_id)
            - (e.g., "output/example_output/network_raw/similarity_node_list.csv")
        :param edge_csv_path: the path of the csv containing the edges (header: target, source, weight)
            - (e.g., "output/example_output/network_raw/similarity_edge_list.csv")
        :return: updates the csv of the edges with with a significance score (alpha) assigned to each edge (new header: target, source, weight, alpha) and returns the path of csv
            - (e.g., "output/example_output/network_raw/similarity_edge_list.csv")
    """
    my_print("Loading graph...")

    df_node = pd.read_csv(node_csv_path,  dtype={"user_id": str})
    list_node = df_node['user_id'].tolist()
    df_edge = pd.read_csv(edge_csv_path,  dtype={"source": str,"target": str})
    df_edge = df_edge.set_index(['source', 'target'])
    dict_edge = df_edge.to_dict('index')
    dict_edge = [(s, t, attr) for (s, t), attr in dict_edge.items()]

    G = nx.Graph()
    G.add_nodes_from(list_node)
    G.add_edges_from(dict_edge)

    my_print("Applying multiscale backbone analysis...")
    G = disparity_filter(G)

    my_print(f"Saving results to {edge_csv_path}...")
    with open(edge_csv_path, "w") as handle:
        writer = csv.writer(handle, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["source","target","weight","alpha"])
        for source, target, data in G.edges(data=True):
            writer.writerow([source.replace('"', ''), target.replace('"', ''), data["weight"], data["alpha"]])

    my_print("Finished!")
    my_print(f"Saved user similarity edge list with bacbone info in {edge_csv_path}")

    return edge_csv_path


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_raw/similarity_node_list.csv")
    edge_csv_path = Path("../output/example_output/network_raw/similarity_edge_list.csv")
    # Function call
    edge_csv_path = add_multiscale_backbone_to_edgelist(node_csv_path, edge_csv_path)
    # Output example
    print(edge_csv_path)  # "../output/example_output/network_raw/similarity_edge_list.csv"
