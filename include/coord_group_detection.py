from .lib import *
import networkx as nx
import numpy as np
import community as community_louvain
import jsonlines
import json
import pandas as pd

def compute_louvain_partitions(node_csv_path, edge_csv_path, louvain_resolution, partitions_path,
                       quantile_start=0, quantile_stop=1, quantile_steps=101, seed_mod_path=None):

    if seed_mod_path is not None:
        my_print("Loading seed partition...")
        with open(seed_mod_path, "r") as handle:
            seed_mod = json.load(handle)

        prev = {}
        for m, nodes in seed_mod.items():
            for node in nodes:
                prev.setdefault(str(node), int(m))
    else:
        prev = None
    df_edge = pd.read_csv(edge_csv_path, dtype = {
        "source": str,
        "target": str
    })
    my_print("Building network...")
    G = load_graph_from_csvs(node_csv_path, edge_csv_path)

    with jsonlines.open(partitions_path, mode="w") as handle:

        for i, quantile in enumerate(np.linspace(quantile_start, quantile_stop, num=quantile_steps)):

            my_print("Computing partition {0}/{1}.".format(i+1, quantile_steps))
            threshold = df_edge.weight.quantile(quantile)
            G_filtered = nx.Graph(((source, target, attr) for source, target, attr in G.edges(data=True) if attr['weight'] >= threshold))
            partition = community_louvain.best_partition(G_filtered, partition=prev, resolution=louvain_resolution, randomize=False, random_state=0)
            prev = partition
            reversed_partition = reverse_partition(partition)
            handle.write({"quantile": quantile, "threshold": threshold, "communities_raw": reversed_partition})

    return partitions_path

def reverse_partition(p):
    r = dict()
    for node, modularity in p.items():
        if modularity in r:
            r[modularity].append(node)
        else:
            r.setdefault(modularity, [node])
    return r


def find_coordinated_groups(partitions, min_cardinality, seed=None, already_found=None):

    temp = {}
    for modularity, node_ids in partitions.items():
        # if len(node_ids) >= min_cardinality:
        temp.setdefault(modularity, len(node_ids))

    temp_ordered = sorted(temp, key=temp.get, reverse=True)

    temp_coordinated = {}
    for i, m in enumerate(temp_ordered):
        temp_coordinated.setdefault(i, partitions[m])

    if seed is not None:
        correspondences = {}
        for m in temp_coordinated:
            intersection = 0
            correspondence = -1
            for m_seed in seed:
                if len(set(temp_coordinated[m]).intersection(seed[m_seed])) > intersection:
                    intersection = len(set(temp_coordinated[m]).intersection(seed[m_seed]))
                    correspondence = m_seed

            if correspondence >= 0:
                if m in correspondences:
                    if intersection > correspondences[m]["intersection"]:
                        correspondences[m]["to"] = [correspondence].extend(correspondences[m]["to"])
                        correspondences[m]["intersection"] = [intersection].extend(correspondences[m]["intersection"])
                    else:
                        correspondences[m]["to"].append(correspondence)
                        correspondences[m]["intersection"].append(intersection)
                else:
                    correspondences.setdefault(m, {"to": [correspondence], "intersection": [intersection]})

        not_found = 0
        coordinated = {}

        for m in temp_coordinated:
            if m in correspondences:
                coordinated.setdefault(correspondences[m]["to"][0], temp_coordinated[m])
            else:
                if len(temp_coordinated[m]) >= min_cardinality:
                    coordinated.setdefault(already_found + not_found, temp_coordinated[m])
                    not_found += 1
                    already_found += 1
    else:
        temp_coordinated = {k: v for k, v in temp_coordinated.items() if len(v) >= min_cardinality}
        coordinated = temp_coordinated
        correspondences = {k: {"to": [k], "intersection": [len(temp_coordinated[k])]} for k in temp_coordinated}
        already_found = len(coordinated)

    return coordinated, correspondences, already_found


def track_coordinated_groups(partitions_path, coordinated_groups_path, min_cardinality):

    with jsonlines.open(coordinated_groups_path, mode="w") as output_handle:
        with jsonlines.open(partitions_path, mode="r") as input_handle:

            seed = None
            already_found = None

            for i, partition in enumerate(input_handle):

                coordinated, correspondences, already_found = find_coordinated_groups(partition["communities_raw"], 
                                                                                      min_cardinality,
                                                                                      seed=seed,
                                                                                      already_found=already_found)
                partition.setdefault("coordinated_groups", coordinated)
                partition.setdefault("correspondences", correspondences)

                seed = coordinated

                output_handle.write(partition)

    my_print("Total groups found = {}".format(already_found))
    return coordinated_groups_path
