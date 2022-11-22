from gensim.test.utils import get_tmpfile
from gensim.similarities import Similarity
from .lib import *
import csv


def save_cosine_similarities(ids_path, dct_path, corpus_path, model_path, output_path,
                             chunksize=256, shardsize=32768, norm='l2'):

    my_print("Loading data from pickles...")
    ids = load_pickle(ids_path)
    dct = load_pickle(dct_path)
    corpus = load_pickle(corpus_path)
    model = load_pickle(model_path)

    index_tmpfile = get_tmpfile("index")
    my_print("Building similarity model in {}...".format(index_tmpfile))
    index = Similarity(index_tmpfile, model[corpus], num_features=len(dct),
                       chunksize=chunksize,
                       shardsize=shardsize,
                       norm=norm)

    #print(index[model[corpus]])

    my_print("Save similarities:")
    with open(output_path, "w") as handle:
        writer = csv.writer(handle, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["source", "target", "weight"])
        for i, similarities in enumerate(index[model[corpus]]):
            for j, similarity in enumerate(similarities[i+1:]):
                if similarity > 0:
                    writer.writerow([ids[i], ids[j+i+1], similarity])
            my_print("{0}/{1} user processed.".format(i+1, len(ids)))

    return output_path










