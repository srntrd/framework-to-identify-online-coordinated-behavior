import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import pandas as pd
from include.lib import my_print, load_pickle, compute_tfidf_tagclouds
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
import matplotlib.pyplot as plt
from wordcloud import WordCloud, get_single_color_func
from matplotlib.lines import Line2D
import json
from pathlib import Path

def wordcloud_narratives(node_csv_path, communities_metadata_path, outdir_tfidf, outdir_plots):
    """
        Create the hashtag cloud visualization of the communities under investigation

        :param node_csv_path: the path of the csv with the nodes
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")
        :param communities_metadata_path: metadata about the communities under investigation
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
        :param outdir_tfidf: the path of the directory that contains the user vector models
            - (e.g., "output/example_output/tfidf_models")
        :param outdir_plots: the path of the directory where to save the output plot
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")

        :return: the path of the png file with the visualization
            - (e.g., "output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/hashtagclouds_communities.png")

    """

    output_path = outdir_plots / Path("hashtagclouds_communities.png")

    my_print("Drawing hashtag cloud...")

    ids = load_pickle(outdir_tfidf / Path("ids.pickle"))
    corpus = load_pickle(outdir_tfidf / Path("hashtags/corpus.pickle"))
    dictionary = Dictionary.load(str(outdir_tfidf / Path("hashtags/dct.pickle")))
    model = TfidfModel.load(str(outdir_tfidf / Path("hashtags/model.pickle")))

    df_node = pd.read_csv(node_csv_path, dtype = {"user_id": str})
    with open(communities_metadata_path, "r") as handle:
        communities_metadata = json.load(handle)

    total_clusters = len(communities_metadata)
    ncols = 2
    nrows = total_clusters // ncols
    if total_clusters % ncols != 0:
        nrows += 1
    position = range(1, total_clusters + 1)
    fig = plt.figure(1)

    for i, (k, community) in enumerate(communities_metadata['communities'].items()):
        k = int(k)
        label = community['label']
        my_print(f"Computing cloud for community {label}...")
        ids_to_consider = df_node.loc[df_node["coordinated_group"] == k]["user_id"].tolist()
        hex_color = community['hex_color']
        cardinality = len(ids_to_consider)
        if cardinality !=  community['size']:
            my_print("odd: cardinality != size in metadata")

        tag_tfidf_dic = compute_tfidf_tagclouds(ids_to_consider, ids, corpus, dictionary, model)

        wc = WordCloud(background_color = "white",
                       width = 1000,
                       height = 1000,
                       max_words = 200,
                       relative_scaling = 0.5,
                       random_state = 0,
                       max_font_size = 250,
                       prefer_horizontal = 1,
                       font_path = 'Arial',
                       ).generate_from_frequencies(tag_tfidf_dic)
        wc.recolor(color_func = get_single_color_func(hex_color))

        ax = fig.add_subplot(nrows, ncols, position[i])
        ax.imshow(wc)
        ax.axis('off')
        circ = Line2D([0], [0], marker = 'o', color = 'w',
                      label = f"{label} ({cardinality} users)",
                      markerfacecolor = hex_color,
                      markersize = 5)
        ax.legend(handles = [circ], prop = {'size': 10}, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True).get_frame().set_alpha(0.8)
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches = 'tight')
    plt.close()
    my_print(f"Saved figure network in {output_path}")
    return output_path


if __name__ == "__main__":
    # Input example
    node_csv_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/filtered_similarity_node_list_coordination.csv")  # nodes with info about coordination
    communities_metadata_path = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/coordinated_groups_metadata.json")
    outdir_tfidf = Path("../output/example_output/tfidf_models")
    outdir_plots = Path("../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/")
    # Function call
    plot_hashtagcloud_communities_path = wordcloud_narratives(node_csv_path, communities_metadata_path, outdir_tfidf, outdir_plots)
    # Output example
    print(plot_hashtagcloud_communities_path)  # "../output/example_output/network_backbone_alpha0.15/louvain_communities_res1/coordinated_communities_quantile(0,1,101)_mincardinality2/plots_top10_coordinated_groups_mincardinality2/hashtagclouds_communities.png"
