
from .lib import *
import jsonlines
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat


def handle_sources(tweet, source_keys):

    sequences = []
    for skl in source_keys:
        seq = []
        for sk in skl:
            k = sk.split(".")
            seq.extend([str(item[k[-1]]).lower() for item in nested_get_value(tweet, k[:-1])])

        sequences.append(sorted(list(set(seq))))

    return sequences


def parse_raw_sequences(raw_sequences_path, output_path):
    """
    Parse raw sequences to extract proper vectors and save them to output_path.
    :param raw_sequences_path: [str] the path to the raw sequences JSONlines file
    :param output_path: [str] output path
    :return: None
    """
    hashtag_keys = ["entities.hashtags.text",
                    "extended_tweet.entities.hashtags.text",
                    "retweeted_status.entities.hashtags.text",
                    "retweeted_status.extended_tweet.entities.hashtags.text"]

    mention_keys = ["entities.user_mentions.id",
                    "extended_tweet.entities.user_mentions.id",
                    "retweeted_status.entities.user_mentions.id",
                    "retweeted_status.extended_tweet.entities.user_mentions.id"]

    url_keys = ["entities.urls.expanded_url",
                "extended_tweet.entities.urls.expanded_url",
                "retweeted_status.entities.urls.expanded_url",
                "retweeted_status.extended_tweet.entities.urls.expanded_url"]

    with jsonlines.open(raw_sequences_path, "r") as input_handle:
        with jsonlines.open(output_path, "w") as output_handle:
            for i, user in enumerate(input_handle):
                to_write = dict()
                to_write["user_id"] = user["user_id"]
                to_write["timestamps"] = user["timestamps"]
                to_write["retweeted_status_ids"] = [t["retweeted_status"]["id_str"] for t in user["raw_sequences"]]
                to_write["retweeted_status_timestamps"] = [UTC_to_timestamp(date_string_to_UTC(t["retweeted_status"]["created_at"])) for t in user["raw_sequences"]]
                hashtags, mentions, urls = zip(*[x for x in ProcessPoolExecutor().map(handle_sources, user["raw_sequences"], repeat([hashtag_keys, mention_keys, url_keys]))])
                to_write["retweeted_status_user_ids"] = [t["retweeted_status"]["user"]["id_str"] for t in user["raw_sequences"]]
                to_write["hashtags"] = list(hashtags)
                to_write["mentions"] = list(mentions)
                to_write["urls"] = list(urls)
                output_handle.write(to_write)
                my_print("{} users processed.".format(i+1))














