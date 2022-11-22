import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from include.user_similarities import save_cosine_similarities
from include.lib import *
from pathlib import Path


def save_user_similarities(outdir_tfidf, outdir, chunksize = 256, shardsize = 32768, norm = "l2"):
    """
        Computes the the user similarity network and saves in a csv file the nodes and edges,
        where the nodes are the users and the edges are weighted based on the retweet similarities of the user vector models.

        :param outdir_tfidf: the path of the directory where are stored the pickled of the user vector models
            - (e.g., "output/example_output/tfidf_models")
        :param outdir: the path of the output directory (e.g., "output/example_output/") where a new subdirectory named "network_raw/" will be created
            - (e.g., "output/example_output/")
        :param chunksize: parameter of the gensim.similarities.docsim.Similarity class used for scalability.
            - default 256.
        :param shardsize: parameter of the gensim.similarities.docsim.Similarity class used for scalability.
            - default 32768.
        :param norm: parameter of the gensim.similarities.docsim.Similarity class used for scalability.
            - default l2.
        :return:
            - output_node_csv_path: the path of the csv with the nodes
                - (e.g., "output/example_output/network_raw/similarity_node_list.csv")
            - output_edge_csv_path: the path of the csv with the edges
                - (e.g., "output/example_output/network_raw/similarity_edge_list.csv")

    """

    outdir_network = outdir / Path("network_raw/")
    Path(outdir_network).mkdir(parents = True, exist_ok = True)
    output_node_csv_path = outdir_network / Path("similarity_node_list.csv")
    output_edge_csv_path = outdir_network / Path("similarity_edge_list.csv")

    ids_path = outdir_tfidf / Path("ids.pickle")
    dct_path_rt = outdir_tfidf / Path("RT/dct.pickle")
    corpus_path_rt = outdir_tfidf / Path("RT/corpus.pickle")
    model_path_rt = outdir_tfidf / Path("RT/model.pickle")

    ids = load_pickle(ids_path)
    with open(output_node_csv_path, "w") as csv_file:
        writer = csv.writer(csv_file, quotechar = '"', quoting = csv.QUOTE_NONNUMERIC)
        writer.writerow(["user_id"])
        for user in ids:
            writer.writerow([user])


    output_edge_csv_path= save_cosine_similarities(ids_path, dct_path_rt, corpus_path_rt, model_path_rt, output_edge_csv_path, chunksize=chunksize, shardsize=shardsize, norm=norm)

    my_print("Finished!")
    my_print(f"Saved user similarity node list (user_id) in {output_node_csv_path}")
    my_print(f"Saved user similarity edge list (source, target, weight) in {output_edge_csv_path}")

    return output_node_csv_path, output_edge_csv_path


if __name__ == "__main__":
    # Input example
    outdir = Path("../output/example_output/")
    outdir_tfidf = Path("../output/example_output/tfidf_models/")
    # Function call
    node_csv_path, edge_csv_path = save_user_similarities(outdir_tfidf, outdir)
    # Output example
    print(node_csv_path)  # "../output/example_output/network_raw/similarity_node_list.csv"
    print(edge_csv_path)  # "../output/example_output/network_raw/similarity_edge_list.csv"
