import sys, os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
from include.user_vector_models import compute_tf_idf_model
from include.lib import *
import jsonlines
from pathlib import Path
import csv


def compute_user_vector_models(userseq_json_path, outdir):
    """
        Computes user vector models for retweets and hashtags using gensim

        :param userseq_json_path: jsonl file where every line is a json corresponding to a user.
                                  Each json contains:
                                   - "user_id"
                                   - "timestamps": the list of its tweets' timestamps ordered asc
                                   - "retweeted_status_ids": the list of the user's retweet ids ordered asc (corresponding to the "timestamps" list)
                                   - "retweeted_status_timestamps": the list of the user's retweet timestamps ordered asc (corresponding to the "timestamps" list)
                                   - "retweeted_status_user_ids": the list of the user's retweeted user ids (corresponding to the "timestamps" list)
                                   - "hashtags": list of lists, where each element corresponds to the list of hashtags contained in the i-th tweet of the "timestamps" list
                                   - "mentions": list of lists, where each element corresponds to the list of mentions contained in the i-th tweet of the "timestamps" list
                                   - "urls": list of lists, where each element corresponds to the list of urls contained in the i-th tweet of the "timestamps" list
                                   Example: {  "user_id": 111,
                                            "timestamps": [1601596899.0, 1601597248.0],
                                            "retweeted_status_ids": ["retweet0001", "retweet0002"],
                                            "retweeted_status_timestamps": [1668946003.0, 1668945703.0],
                                            "retweeted_status_user_ids": ["user0001", "user0002"],
                                            "hashtags": [["elections","vote"],["today"]],
                                            "mentions": [["user222"],["user222","user333"]],
                                            "urls": [["http://vote.com",[]]
            - (e.g., input_data/input_superspreaders_seqs.jsonl)
        :param outdir: the path of the output directory (e.g., "output/example_output/") where new subdirectories will be crated ("tfidf_models/", "tfidf_models/RT/", "tfidf_models/hashtags/") to save and store the user vector models pickles
            - (e.g., "output/example_output/")
        :return: the path of the directory containing the saved pickles with information about the Dictionary, Corpora and TfidfModel for hashtags and retweets
            - (e.g., "output/example_output/tfidf_models/")
       """

    Path(outdir).mkdir(parents = True, exist_ok = True)  # create output directory
    outdir_tfidf = outdir / Path("tfidf_models/")
    outdir_rt = outdir_tfidf / Path("RT/")
    outdir_hashtag = outdir_tfidf / Path("hashtags/")

    Path(outdir_tfidf).mkdir(parents = True, exist_ok = True)
    Path(outdir_rt).mkdir(parents=True, exist_ok=True)
    Path(outdir_hashtag).mkdir(parents=True, exist_ok=True)

    ids_path = outdir_tfidf / Path("ids.pickle")
    dct_path_rt = outdir_rt / Path("dct.pickle")
    corpus_path_rt = outdir_rt / Path("corpus.pickle")
    model_path_rt = outdir_rt / Path("model.pickle")
    dct_path_hashtags = outdir_hashtag / Path("dct.pickle")
    corpus_path_hashtags = outdir_hashtag / Path("corpus.pickle")
    model_path_hashtags = outdir_hashtag / Path("model.pickle")

    user_ids = []
    user_rts = []
    user_hashtags = []

    my_print("Loading user sequences and saving nodes to CSV...")

    with jsonlines.open(userseq_json_path, mode="r") as handle:
        for user in handle:
            user_ids.append(user["user_id"])
            user_rts.append(user["retweeted_status_ids"])
            user_hashtags.append(list(flatten_iterable(user["hashtags"])))

    my_print("Saving user ids to pickle...")
    save_pickle(user_ids, ids_path)  # e.g., ['1266801030643232768', '120157829']

    my_print("Computing user RT TF-IDF model...")
    dct, corpus, model = compute_tf_idf_model(user_rts)
    my_print("Saving user RT TF-IDF model to pickle...")
    save_pickle(dct, dct_path_rt)  # e.g., unique retweet ids - Dictionary(8 unique tokens: ['1312702345642496000', '1313285277276921859', '1313435619587231744', '1314190484705808386', '1315083733851148291']...)
    save_pickle(corpus, corpus_path_rt)  # e.g., [[(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)], [(5, 1), (6, 1), (7, 1)]]
    save_pickle(model, model_path_rt)  # e.g., TfidfModel(num_docs=1, num_nnz=8)

    my_print("Computing user hashtag TF-IDF model...")
    dct, corpus, model = compute_tf_idf_model(user_hashtags)
    my_print("Saving user hashtag TF-IDF model to pickle...")
    save_pickle(dct, dct_path_hashtags)  # e.g., Dictionary(10 unique tokens: ['covid', 'eo', 'kag', 'prayer', 'prayformelania', 'prayfortrump', 'trump', 'election2020', 'remate', 'usa20unam'])
    save_pickle(corpus, corpus_path_hashtags)  # e.g., [[(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)], [(7, 3), (8, 2), (9, 3)]] # e.g., user at index 1, uses hashtag at index 7 (election2020) three times
    save_pickle(model, model_path_hashtags)  # e.g., TfidfModel(num_docs=1, num_nnz=10)

    my_print(f"Saved user vector models in path {outdir_tfidf}")

    my_print("Finished!")

    return outdir_tfidf


if __name__ == "__main__":
    # Input example
    userseq_json_path = Path("../input_data/input_superspreaders_seqs.jsonl")
    outdir = Path("../output/example_output/")
    # Function call
    user_vector_models_path = compute_user_vector_models(userseq_json_path, outdir)
    # Output example
    print(user_vector_models_path)  # "../output/example_output/tfidf_models/"
