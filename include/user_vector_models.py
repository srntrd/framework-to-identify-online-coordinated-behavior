from gensim.corpora import Dictionary
from gensim.models import TfidfModel

def compute_tf_idf_model(documents):
    """

    :param documents:
    :return:
    """
    dct = Dictionary(documents)  # fit dictionary
    corpus = [dct.doc2bow(doc) for doc in documents]  # convert corpus to BoW format
    model = TfidfModel(corpus)  # fit model

    return dct, corpus, model





