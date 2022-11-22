import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from include.lib import my_print, compute_seed_comm, parse_seed_comm
from pathlib import Path

def compute_seed_communities(node_csv_path, edge_csv_path, louvain_resolution, outdir_backbone):
    """
    Computes the communities of the network backbone. This communities will be used as seed for the coordination-aware community detection.

    :param node_csv_path: the path of the csv with the nodes
        - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_node_list.csv")
    :param edge_csv_path: the path of the csv with the edges
        - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
    :param louvain_resolution: the resolution parameter of the louvain algorithm
        - (e.g., 1)
    :param outdir_backbone: the path of the directory
        - (e.g., "output/example_output/network_backbone_alpha0.15/") where a new subdirectory named f"louvain_communities_res{louvain_resolution}/" will be created to save the output
    :return:
        - output_node_csv_path: the path of the csv with nodes and their corresponding community computed with the input louvain_resolution (csv header: "user_id", "modularity_def")
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/filtered_similarity_node_list_communities.csv")
        - output_seed_path: the path of a json file where the keys are the communities and the values are the user ids belonging to the community
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/seed_communities.json")
    """
    outdir_communities = outdir_backbone / Path(f"louvain_communities_res{louvain_resolution}/")
    Path(outdir_communities).mkdir(parents = True, exist_ok = True)
    output_node_csv_path = outdir_communities / Path("filtered_similarity_node_list_communities.csv")
    output_seed_path = outdir_communities / Path("seed_communities.json")

    output_node_csv_path = compute_seed_comm(node_csv_path, edge_csv_path, louvain_resolution, output_node_csv_path)

    output_seed_path = parse_seed_comm(output_node_csv_path, output_seed_path)

    return output_node_csv_path, output_seed_path, outdir_communities


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/filtered_similarity_node_list.csv")
    edge_csv_path = Path("../output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
    louvain_resolution = 1
    outdir_backbone = Path("../output/example_output/network_backbone_alpha0.15/")
    # Function call
    filtered_node_communities_csv_path, seed_mod_path, outdir_communities = compute_seed_communities(node_csv_path, edge_csv_path, louvain_resolution, outdir_backbone)
    # Output example
    print(filtered_node_communities_csv_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/filtered_similarity_node_list_communities.csv"
    print(seed_mod_path)                       # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/seed_communities.json"
    print(outdir_communities)                  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/"
