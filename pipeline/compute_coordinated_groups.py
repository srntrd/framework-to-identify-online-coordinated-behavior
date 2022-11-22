import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from include.lib import my_print
from include.coord_group_detection import compute_louvain_partitions, track_coordinated_groups
from include.coord_group_stats import cb_network_stats
import csv
from pathlib import Path


def compute_coordinated_groups(node_csv_path, edge_csv_path, seed_mod_path, outdir_communities, louvain_resolution, min_cardinality, quantile_start=0, quantile_stop=1, quantile_steps=101):
    """ Here, we apply our coordination-aware community detection.
        In particular, we start from the communities extracted as seed, and then apply increansingly restrictive threshold to isolate nodes that survive, which correspond to users that are increasingly more coordinated.
        The moving threshold corresponds to the quantile of the edges weight, in order to adapt the computation to dense graphs as well as to sparse graphs.

        :param node_csv_path: the path of the csv with the nodes
            - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_node_list.csv")
        :param edge_csv_path: the path of the csv with the edges
            - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
        :param seed_mod_path: the path of a json file with the seed communities
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/seed_communities.json")
        :param outdir_communities: the path of the directory
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/") where a new subdirectory named f"coordinated_communities_quantile({quantile_start},{quantile_stop},{quantile_steps})_mincardinality{min_cardinality}/" to save the output results
        :param louvain_resolution: the resolution parameter of the louvain algorithm. Must be the same used for computing the seed communities
            -  (e.g., 1)
        :param min_cardinality: minimum size of communities to consider
            - (e.g., 2)
        :param quantile_start: Start threshold.
            - (default=0)
        :param quantile_stop: Stop threshold.
            - (default=0)
        :param quantile_steps: Total steps of threshold.
            - (default=101 - corresponding to a single threshold step of 0.01 quantile)
        :return:
            - output_coordinated_groups_path: the path of the jsonl with the coordinated groups and their evolution at each threshold
                - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
            - output_coordinated_groups_stats_csv_path: the path of the csv with the coordinated groups and their evolution at each threshold plus network metric statistics at each threshold
                - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups_stats.csv")
            - outdir_coordination_aware: the path of the new subdirectory named after the parameters used and containing the output
                - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/")

    """

    outdir_coordination_aware = outdir_communities / Path(f"coordinated_communities_quantile({quantile_start},{quantile_stop},{quantile_steps})_mincardinality{min_cardinality}/")
    Path(outdir_coordination_aware).mkdir(parents = True, exist_ok = True)
    output_partitions_path = outdir_coordination_aware / Path("louvain_partitions.jsonl")
    output_coordinated_groups_path = outdir_coordination_aware / Path("coordinated_groups.jsonl")
    output_coordinated_groups_stats_csv_path = outdir_coordination_aware / Path("coordinated_groups_stats.csv")

    my_print(f"Computing partitions with seed {seed_mod_path}...")
    output_partitions_path = compute_louvain_partitions(node_csv_path, edge_csv_path, louvain_resolution, output_partitions_path,
                                                         quantile_start=quantile_start,
                                                         quantile_stop=quantile_stop,
                                                         quantile_steps=quantile_steps,
                                                         seed_mod_path=seed_mod_path)

    my_print("Tracking coordinated groups...")
    output_coordinated_groups_path = track_coordinated_groups(output_partitions_path, output_coordinated_groups_path, min_cardinality)

    my_print(f"Computing network metrics...")
    df_stats = cb_network_stats(node_csv_path, edge_csv_path, output_coordinated_groups_path)

    df_stats.to_csv(output_coordinated_groups_stats_csv_path, index = False, header = True, quoting = csv.QUOTE_NONNUMERIC)
    my_print(f"Saved coordinated groups with network metrics and statistics in csv {output_coordinated_groups_stats_csv_path}")

    my_print(f"Saved partitions in {output_partitions_path}")
    my_print(f"Saved coordinated groups in json {output_coordinated_groups_path}")
    my_print("Finished!")

    return output_coordinated_groups_path, output_coordinated_groups_stats_csv_path, outdir_coordination_aware


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/filtered_similarity_node_list_communities.csv")  # we use the node file in this subdir because it stores the info about the communities
    edge_csv_path = Path("../output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
    seed_mod_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/seed_communities.json")
    outdir_communities = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/")
    louvain_resolution = 1  # must be the same used for computing the seed_communities
    min_cardinality = 2
    # Function call
    coordinated_groups_path, coordinated_groups_stats_csv_path, outdir_coordination_aware = compute_coordinated_groups(node_csv_path, edge_csv_path, seed_mod_path, outdir_communities, louvain_resolution, min_cardinality, quantile_start=0, quantile_stop=1, quantile_steps=101)
    # Output example
    print(coordinated_groups_path)            # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl"
    print(coordinated_groups_stats_csv_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups_stats.csv"
    print(outdir_coordination_aware)          # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/"
