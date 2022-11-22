from .lib import my_print, load_graph_from_csvs
import networkx as nx
import pandas as pd
import jsonlines

def cb_network_stats(node_csv_path, edge_csv_path, coord_group_path):
    my_print("Building graph...")
    G = load_graph_from_csvs(node_csv_path, edge_csv_path)
    #G = nx.convert_matrix.from_pandas_edgelist(edges_df, "source", "target", "weight")
    quantiles = []
    thresholds = []
    cb_groups = []
    columns = ["quantile", "threshold", "group",
               "size",
               "weighted_clustering", "unweighted_clustering",
               "density",
               "weighted_assortativity", "unweighted_assortativity"]
    with jsonlines.open(coord_group_path, "r") as handle:
        for row in handle:
            quantiles.append(round(row["quantile"],2))
            thresholds.append(row["threshold"])
            cb_groups.append(row["coordinated_groups"])
    group_labels = sorted(cb_groups[0].keys())

    stats = []

    for i, threshold in enumerate(thresholds):
        my_print("+"*50)

        my_print("Processing threshold {} ({}/{})...".format(threshold, i, len(thresholds)))

        G_threshold = nx.Graph(((source, target, attr) for source, target, attr in G.edges(data=True)
                                if attr['weight'] >= threshold))
        group_labels = sorted(list(set(group_labels + list(cb_groups[i].keys()))))
        for group_label in group_labels:
            my_print("Processing group {0}/{1}.".format(group_label, len(group_labels)))
            group_nodes = cb_groups[i].get(group_label, [])
            size = len(group_nodes)
            if len(group_nodes) > 0:

                G_group = nx.Graph(((source, target, attr) for source, target, attr in G_threshold.edges(data=True)
                                    if source in group_nodes and target in group_nodes))

                weighted_clustering = nx.average_clustering(G_group, weight="weight")
                unweighted_clustering = nx.average_clustering(G_group, weight=None)
                density = nx.density(G_group)
                weighted_assortativity = nx.degree_pearson_correlation_coefficient(G_group, weight="weight")
                unweighted_assortativity = nx.degree_pearson_correlation_coefficient(G_group, weight=None)
            else:
                weighted_clustering = None
                unweighted_clustering = None
                density = None
                weighted_assortativity = None
                unweighted_assortativity = None

            stats.append([quantiles[i], threshold, group_label,
                         size,
                         weighted_clustering, unweighted_clustering,
                         density,
                         weighted_assortativity, unweighted_assortativity])

        df_stats = pd.DataFrame(stats, columns = columns)
        max_size = {row['group']:row['size'] for i, row in df_stats[df_stats['quantile']==0].iterrows()}
        df_stats['size_(%)'] = df_stats.apply(lambda row: int((row['size'] * 100) / max_size[row['group']]), axis = 1)
        df_stats['size_ratio'] = df_stats.apply(lambda row: (row['size']) / max_size[row['group']], axis = 1)

    return df_stats






