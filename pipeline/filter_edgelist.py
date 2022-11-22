import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import csv
from include.lib import my_print
import pandas as pd
from pathlib import Path


def filter_edgelist(input_edge_csv_path, alpha, outdir):
    """
        Computes the network backbone, by filtering the nodes and edges to keep the edges having a significance score (alpha) lower than the alpha input

        :param input_edge_csv_path: the path of the csv with the edges
            - (e.g., "output/example_output/network_raw/similarity_edge_list.csv")
        :alpha: alpha input to retain edges with alpha lower than alpha
            - (e.g., 0.15)
        :outdir: the path of the output directory (e.g., "output/example_output") where a new subdirectory named f"network_backbone_alpha{alpha}/" will be created
            - (e.g., "output/example_output")
        :return:
            - output_node_csv_path: the path of the csv with the filtered nodes
                - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_node_list.csv")
            - filtered_edge_csv_path: the path of the csv with the filtered edge
                - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
            - outdir_backbone: the path of the new subdirectory containing the csv nodes and edges of the network backbone
                - (e.g., "output/example_output/network_backbone_alpha0.15/")
    """
    outdir_backbone = outdir / Path(f"network_backbone_alpha{alpha}/")
    Path(outdir_backbone).mkdir(parents = True, exist_ok = True)
    output_node_csv_path = outdir_backbone / Path("filtered_similarity_node_list.csv")
    output_edge_csv_path = outdir_backbone / Path("filtered_similarity_edge_list.csv")
    my_print(f"Filtering {input_edge_csv_path} with alpha = {alpha}")

    c = 0
    with open(input_edge_csv_path, "r") as input_handle:
        reader = csv.reader(input_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        with open(output_edge_csv_path, "w") as output_handle:
            writer = csv.writer(output_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            for edge in reader:
                if (edge[3] == 'alpha') or (edge[3] < alpha):
                    writer.writerow(edge)
                    c += 1

    df_edge = pd.read_csv(output_edge_csv_path, dtype = {
        "source": str,
        "target": str
    })
    df_node = pd.DataFrame(pd.unique(df_edge[['source', 'target']].values.ravel('K')), columns = ['user_id'])
    df_node.to_csv(output_node_csv_path, index = False, header = True, quoting = csv.QUOTE_NONNUMERIC)

    my_print(f"{c} filtered edges saved to {output_edge_csv_path}")
    my_print(f"{len(df_node)} filtered nodes saved to {output_node_csv_path}")
    my_print("Finished!")

    return output_node_csv_path, output_edge_csv_path, outdir_backbone


if __name__ == "__main__":
    # Input example
    alpha = 0.15
    outdir = Path("../output/example_output/")
    input_edge_csv_path = Path("../output/example_output/network_raw/similarity_edge_list.csv")
    # Function call
    filtered_node_csv_path, filtered_edge_csv_path, outdir_backbone = filter_edgelist(input_edge_csv_path, alpha, outdir)
    # Output example
    print(filtered_node_csv_path)  # "../output/example_output/network_backbone_alpha0.15/filtered_similarity_node_list.csv"
    print(filtered_edge_csv_path)  # "../output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv"
    print(outdir_backbone)         # "../output/example_output/network_backbone_alpha0.15/"
