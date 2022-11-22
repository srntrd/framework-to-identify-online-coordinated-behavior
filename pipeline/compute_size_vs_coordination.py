import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import pandas as pd
from include.lib import my_print
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
from pathlib import Path


def compute_size_vs_coordination(coordinated_groups_stats_csv_path, communities_metadata_path, outdir_plots):
    """
        Create the plot for the communities under investigation comparing their coordination vs their network metrics (size, size (%))) and assign the community coordination value

        :param coordinated_groups_stats_csv_path: the path of the csv with the nodes
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups_stats.csv")
        :param communities_metadata_path: metadata about the communities under investigation
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
        :param outdir_plots: the path of the directory where to save the output
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")
        :return: the path of the png file with the visualization
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/network_metrics_vs_coordination.png")

    """
    output_path = outdir_plots / Path("network_metrics_vs_coordination.png")


    with open(communities_metadata_path, "r") as handle:
        communities_metadata = json.load(handle)
    df_stats =  pd.read_csv(coordinated_groups_stats_csv_path)
    communities_of_interest = list([int(k) for k, v in communities_metadata['communities'].items()])
    df_stats = df_stats[df_stats['group'].isin(communities_of_interest)]
    df_stats['group_label'] = df_stats.apply(lambda row: communities_metadata['communities'][str(int(row.group))]["label"], axis = 1)

    fig, axes = plt.subplots(1, 3, sharex = 'col', figsize = (15, 5))
    for i, metric in enumerate(['size','size_(%)']):
        axes.flat[i] = sns.lineplot(x = 'quantile',
                          y = metric,
                          data = df_stats,
                          palette = [v['hex_color'] for k,v in communities_metadata['communities'].items()],
                          hue = 'group_label',
                          ax = axes.flat[i],
                          # style='group_label',
                          markers = False)
        axes.flat[i].set(xlabel = 'coordination')
        axes.flat[i].set_ylim(ymin=0)
        axes.flat[i].set_xlim(0,1)
    # add plot of the size perc curve integral
    area = []
    for i in range(0, df_stats.group.nunique()):
        x = df_stats[df_stats['group'] == i]['quantile'].values
        y = df_stats[df_stats['group'] == i]['size_ratio'].values
        curr = {
            'group': i,
            'group_label': df_stats[df_stats['group'] == i]['group_label'].values[0],
            'community_coordination': np.trapz(x = x, y = y),
            'size': df_stats[df_stats['group'] == i]['size'].max()
        }
        area.append(curr)
    area_df = pd.DataFrame(area)
    sns.scatterplot(data = area_df,
                    x = "community_coordination",
                    y = "size",
                    hue = "group_label",
                    s = 80,
                    ax = axes.flat[2],
                    palette = [v['hex_color'] for k, v in communities_metadata['communities'].items()],
                    sizes = (70, 200))
    axes.flat[2].set_ylim(ymin=0)
    axes.flat[2].set_xlim(0, 1)

    plt.tight_layout()
    fig.savefig(output_path, bbox_inches = 'tight')
    plt.close()
    my_print(f"Saved plot metrics vs coordination in {output_path}")
    return output_path


if __name__ == "__main__":
    # Input example
    coordinated_groups_stats_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups_stats.csv")
    communities_metadata_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
    outdir_plots = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")
    # Function call
    plot_metrics_coordination_path = compute_size_vs_coordination(coordinated_groups_stats_csv_path, communities_metadata_path, outdir_plots)
    # Output example
    print(plot_metrics_coordination_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/network_metrics_vs_coordination.png"

