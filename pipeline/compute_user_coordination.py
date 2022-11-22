import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import jsonlines
import pandas as pd
import itertools
from include.lib import my_print
import csv
from pathlib import Path


def compute_user_coordination(coordinated_groups_path, node_csv_path, outdir_coordination_aware):
    """ Computes for each user_id:
        - quantile: the last threshold the user survives. At greater threshold the user does not survive
        - threshold: similarity edge weight threshold corresponding to the quantile.
        - coordinated_group: the community the user belongs to the last time it survives the moving threshold.
        NB: users with null value for quantile,threshold,coordinated_group are either
        - users that do not even survive at quantile 0, therefore not coordinated: they do not belong to coordinated groups
        - or users that belong to communities with a smaller size than min_cardinality previously specified

        :param coordinated_groups_path: the path of the jsonl with the coordinated groups and their evolution at each threshold
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
        :param node_csv_path: the path of the csv with the nodes and communities
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/filtered_similarity_node_list_communities.csv")
        :param outdir_coordination_aware: the path of the directory where to save the output
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/")

        :return: the path of the csv with the nodes and coordinated groups (header: "user_id","modularity_def","quantile","threshold","coordinated_group")
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")

    """
    output_path = outdir_coordination_aware / Path("filtered_similarity_node_list_coordination.csv")

    my_print(f"Loading user dataframe from {node_csv_path}...")
    user_df = pd.read_csv(node_csv_path, dtype={"user_id": str})[["user_id", "modularity_def"]]
    user_df["quantile"] = None
    user_df["threshold"] = None
    user_df["coordinated_group"] = None
    my_print(f"Processing coordinated groups from {coordinated_groups_path}...")
    with jsonlines.open(coordinated_groups_path, mode="r") as handle:
        assigned_groups = []
        for row in handle:
            quantile = row["quantile"]
            threshold = row["threshold"]
            group_to_assign = sorted(list(set(row["coordinated_groups"].keys()).difference(assigned_groups)))
            for group in group_to_assign:
                user_df.loc[user_df["user_id"].isin(row["coordinated_groups"][group]), "coordinated_group"] = int(group)



            ids = list(itertools.chain.from_iterable(row["coordinated_groups"].values()))
            user_df.loc[user_df["user_id"].isin(ids), "quantile"] = quantile
            user_df.loc[user_df["user_id"].isin(ids), "threshold"] = threshold


    user_df.to_csv(output_path, index=False, header=True, quoting = csv.QUOTE_NONNUMERIC)
    my_print(f"User coordination info saved to {output_path}")

    return output_path


if __name__ == "__main__":
    # Input example
    coordinated_groups_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/filtered_similarity_node_list_communities.csv")  # we use the node file in this subdir because it stores the info about the communities
    outdir_coordination_aware = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/")
    # Function call
    filtered_node_coordination_csv_path = compute_user_coordination(coordinated_groups_path, node_csv_path, outdir_coordination_aware)
    # Output example
    print(filtered_node_coordination_csv_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv"
