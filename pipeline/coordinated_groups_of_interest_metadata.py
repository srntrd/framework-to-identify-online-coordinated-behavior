import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import pandas as pd
from include.lib import my_print, load_pickle, compute_tfidf_tagclouds
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
import matplotlib as mpl
import seaborn as sns
import csv
import operator
import json
from pathlib import Path


def coordinated_groups_of_interest_metadata(node_csv_path, coordinated_groups_path, metadata_min_cardinality, metadata_top_communities, outdir_tfidf, outdir_coordination_aware):
    """
        Computes metadata (label, color, etc.) about a subset of coordinated groups in preparation for the analysis and visualization

        :param node_csv_path: the path of the csv with the nodes
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")
        :param coordinated_groups_path: the path of the jsonl with the coordinated groups and their evolution at each threshold
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
        :param metadata_min_cardinality: minimum size of communities to consider
            - (e.g., 2).
        :param metadata_top_communities: maxim number of communities to consider
            - (e.g., 10). More than 10 is not recommended due to color limitations.
        :param outdir_tfidf: the path of the directory that contains the user vector models
            - (e.g., "output/example_output/tfidf_models")
        :param outdir_coordination_aware: the path of the directory where to create a subdirectory to save the metadata named f"plots_top{metadata_top_communities}_coordinated_groups_mincardinality{metadata_min_cardinality}/"
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/")
        :return:
        - output_path: the path of the json with the metadata of the communities of interest
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
        - outdir_plots: the path of a new subdirectory to save the output
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")

    """
    dct_group_to_color = {0: {'colormap': 'Blues'},1: {'colormap': 'Oranges'},2: {'colormap': 'Greens'},3: {'colormap': 'Reds'},4: {'colormap': 'YlOrBr'},5: {'colormap': 'Purples'},6: {'colormap': 'Greys'},7: { 'colormap': 'GnBu'},8: {'colormap': 'YlGn'},9: {'colormap': 'PuRd'}}

    outdir_plots = outdir_coordination_aware / Path(f"plots_top{metadata_top_communities}_coordinated_groups_mincardinality{metadata_min_cardinality}/")
    Path(outdir_plots).mkdir(parents = True, exist_ok = True)
    output_path = outdir_plots / Path("coordinated_groups_metadata.json")

    ids = load_pickle(outdir_tfidf / Path("ids.pickle"))
    corpus = load_pickle(outdir_tfidf / Path("hashtags/corpus.pickle"))
    dictionary = Dictionary.load(str(outdir_tfidf / Path("hashtags/dct.pickle")))
    model = TfidfModel.load(str(outdir_tfidf / Path("hashtags/model.pickle")))
    df_node = pd.read_csv(node_csv_path, dtype = {"user_id": str, "coordinated_group": 'Int64'})

    df_count = df_node.groupby("coordinated_group").size().sort_values(ascending = False).reset_index().rename(columns={0:'count'})
    df_count = df_count[df_count['count'] >= metadata_min_cardinality].head(metadata_top_communities)
    communities_metadata = {}

    for i, row in df_count.iterrows():
        # compute top hashtag
        ids_to_consider = df_node.loc[df_node["coordinated_group"] == row["coordinated_group"]]["user_id"].tolist()
        tag_tfidf_dic = compute_tfidf_tagclouds(ids_to_consider, ids, corpus, dictionary, model)
        top_hashtag = max(tag_tfidf_dic.items(), key = operator.itemgetter(1))[0]

        communities_metadata[str(row["coordinated_group"])] = {
            "coordinated_group": int(row["coordinated_group"]),
            "size": int(row["count"]), # number of users
            "colormap": dct_group_to_color[i]["colormap"],
            "hex_color": sns.color_palette(dct_group_to_color[i]["colormap"], 1).as_hex()[0],
            "top_hashtag": top_hashtag,
            "label": f'group{int(row["coordinated_group"])}_{top_hashtag}'
        }

    metadata = {
        "top_communities_by_size": metadata_top_communities, # max_number_of_communities_to_consider
        "min_cardinality": metadata_min_cardinality,
        "communities": communities_metadata
    }
    with open(output_path, "w") as handle:
        json.dump(metadata, handle)

    my_print(f"Extracted coordinated groups of interest (top {metadata_top_communities} communities by size, with size >= {metadata_min_cardinality}) to {output_path}")
    # coloring nodes according to their communities
    my_print("Assigning coordination-aware color to nodes")
    cg = pd.read_json(coordinated_groups_path, orient = None, lines = True, precise_float = True)
    df_node['color'] = '#aaaaaa'
    for i, (k, community) in enumerate(communities_metadata.items()):
        k = int(k)
        color = community['colormap']
        my_rgbs = sns.color_palette(color, 20).as_hex()
        cmap = mpl.colors.LinearSegmentedColormap.from_list('custom_sequential_colormap', my_rgbs, N = 256)
        min_weight = cg[cg['quantile'] == cg['quantile'].min()]['threshold'].tolist()[0]
        max_weight = cg[cg['quantile'] == cg['quantile'].max()]['threshold'].tolist()[0]
        norm = mpl.colors.Normalize(vmin = min_weight, vmax = max_weight)
        df_node.loc[df_node['coordinated_group'] == k, 'color'] = df_node.apply(lambda row: mpl.colors.rgb2hex(cmap(norm(row['threshold']))), axis = 1)

    df_node.to_csv(node_csv_path, index = False, header = True, quoting = csv.QUOTE_NONNUMERIC)
    my_print(f"Saved coordination-aware color attributes for communities of interest in {node_csv_path}")

    return output_path, outdir_plots


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")
    coordinated_groups_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/coordinated_groups.jsonl")
    metadata_min_cardinality = 2
    metadata_top_communities = 10
    outdir_tfidf = Path("../output/example_output/tfidf_models/")
    outdir_coordination_aware = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/")
    # Function call
    communities_metadata_path, outdir_plots = coordinated_groups_of_interest_metadata(node_csv_path,
                                                                                      coordinated_groups_path,
                                                                                      metadata_min_cardinality,
                                                                                      metadata_top_communities,
                                                                                      outdir_tfidf,
                                                                                      outdir_coordination_aware)
    # Output example
    print(communities_metadata_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json"
    print(outdir_plots)               # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/"
