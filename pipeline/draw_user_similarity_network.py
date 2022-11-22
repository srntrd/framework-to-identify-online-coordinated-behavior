import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import pandas as pd
from include.lib import my_print, load_graph_from_csvs
import networkx as nx
from fa2 import ForceAtlas2
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import json
from matplotlib.lines import Line2D
from pathlib import Path

def draw_user_similarity_network(node_csv_path, edge_csv_path, communities_metadata_path, coordinated_groups_path, outdir_plots):
    """
        Create a visualization of the user similarity network and the communities, with nodes color-coded based on their coordination level


        :param node_csv_path: the path of the csv with the nodes
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")
        :param edge_csv_path: the path of the csv with the edges
            - (e.g., "output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
        :param communities_metadata_path: metadata about the communities under investigation
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
        :param coordinated_groups_path: the path of the jsonl with the coordinated groups and their evolution at each threshold
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
        :param outdir_plots: the path of the directory where to save the output
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")

        :return: the path of the png file with the visualization
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/network_communities.png")

    """
    output_path = outdir_plots / Path("network_communities.png")
    with open(communities_metadata_path, "r") as handle:
        communities_metadata = json.load(handle)

    cg = pd.read_json(coordinated_groups_path, orient = None, lines = True, precise_float = True)

    my_print(f"Drawing the network")

    G = load_graph_from_csvs(node_csv_path, edge_csv_path)

    # We suggest using dedicated software for the network visualisation
    forceatlas2 = ForceAtlas2(
        edgeWeightInfluence = 1.0,
        scalingRatio = 2.0,
        strongGravityMode = False,
        gravity = 1.0,
        verbose = False)

    positions = forceatlas2.forceatlas2_networkx_layout(G, pos = None, iterations = 2000)

    # coordination-aware color: nodes that survive at high similarity edge threshold are more coordinated and have darker color
    color = list( nx.get_node_attributes(G, "color").values() )
    nx.draw_networkx_nodes(G, positions, node_size = 50, node_color = color, alpha = 0.9)
    nx.draw_networkx_edges(G, positions, edge_color = "grey", alpha = 0.1)

    # create legend for node colors
    def create_tick(row):
        sost = 'more' if cg[cg['threshold'] == row['x']]['quantile'].tolist()[0] == 1 else 'less'
        return f"{sost} coordinated\nsurvival threshold: \n  - quantile: {cg[cg['threshold'] == row['x']]['quantile'].tolist()[0]} \n  - edge weight: {round(row['x'], 3)}"

    comm_legend = []
    for i, (k, community) in enumerate(communities_metadata['communities'].items()):
        my_rgbs = sns.color_palette(community['colormap'], 20).as_hex()
        cmap = mpl.colors.LinearSegmentedColormap.from_list('custom_sequential_color', my_rgbs, N = 256)
        minw = cg[cg['quantile'] == cg['quantile'].min()]['threshold'].tolist()[0]
        maxw = cg[cg['quantile'] == cg['quantile'].max()]['threshold'].tolist()[0]
        norm = mpl.colors.Normalize(vmin = minw, vmax = maxw)
        df_legend = pd.DataFrame({"x": [minw, maxw], "y": [minw, maxw]})
        df_legend['hex'] = df_legend.apply(lambda row: mpl.colors.rgb2hex(cmap(norm(row['x']))), axis = 1)
        df_legend['tick'] = df_legend.apply(lambda row: create_tick(row), axis = 1)
        sm = plt.cm.ScalarMappable(cmap = cmap, norm = norm)
        cb = plt.colorbar(sm,
                          label = 'user coordination - quantile (weight threshold)',
                          ticks = df_legend.x,
                          orientation = 'vertical',
                          spacing = 'uniform',
                          pad = 0)
        cb.ax.set_yticklabels(df_legend.tick, va='top')
        cb.ax.set_title(community['label'], fontsize=10, y=-0.05, rotation = 90, ha='center', va='top')
        if i!=0:
            cb.ax.set_yticklabels([])
            cb.set_label('')
        #plt.legend()
        plt.axis('off')

        circ = Line2D([0], [0], marker = 'o', color = 'w',
                      label = f"{community['label']} ({community['size']} users)",
                      markerfacecolor = community['hex_color'],
                      markersize = 5)
        comm_legend.append(circ)
    plt.legend(title = f'Communities of interest (within the \ntop {communities_metadata["top_communities_by_size"]} communities by size, having\nmin_cardinality: {communities_metadata["min_cardinality"]})',
               handles = comm_legend,
               prop = {'size': 10},
               loc = 'upper center',
               bbox_to_anchor = (0.5, -0.05, 0., 0.),  #bbox_to_anchor=(0., -0.05, 1., 0.)
               fancybox = True).get_frame().set_alpha(0.8)


    plt.tight_layout()
    #plt.show()
    plt.savefig(output_path, bbox_inches = 'tight')
    plt.close()
    my_print(f"Saved figure network in {output_path}")

    return output_path


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")  # nodes with info about coordination
    edge_csv_path = Path("../output/example_output/network_backbone_alpha0.15/filtered_similarity_edge_list.csv")
    communities_metadata_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
    coordinated_groups_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
    outdir_plots = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")
    # Function call
    plot_network_communities_path = draw_user_similarity_network(node_csv_path, edge_csv_path, communities_metadata_path, coordinated_groups_path, outdir_plots)
    # Output example
    print(plot_network_communities_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/network_communities.png"
