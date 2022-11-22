import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
#sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
from include.lib import my_print
from include.user_sequences import parse_raw_sequences
from pathlib import Path

def parse_sequences(raw_sequences_path, input_dir):
    """
    Parse a jsonl file of users and their twitter objects, and returns a jsonl file with parsed and formatted relevant information

    :param raw_sequences_path: jsonl file where every line is a json corresponding to a user.
                               Each json contains:
                                - "user_id"
                                - "timestamps": the list of its tweets' timestamps ordered asc
                                - "raw_sequences": the list of the user's tweet objs ordered asc (corresponding to the "timestamps" list)
                               Example: { "user_id": 111, "timestamps": [1601596899.0, 1601597248.0], "raw_sequences": [{"id":"tweet1", "timestamp": 1601596899.0,"entities": {...}, "retweeted_status": {"id":"retweet1"}, etc.},{"id":"tweet2", "timestamp":1601597248.0, "entities": {...}, "retweeted_status": {...}, etc.}] }
        - (e.g., "input_data/input_superspreaders_raw_seqs.jsonl")
    :param input_dir: the path of the directory where the data will be saved:
        - (e.g., "input_data/")
    :return: the path of jsonl file in which every line is a json user.
                                Each json contains:
                                - "user_id"
                                - "timestamps": the list of its tweets' timestamps ordered asc
                                - "retweeted_status_ids": the list of the user's retweet ids ordered asc (corresponding to the "timestamps" list)
                                - "retweeted_status_timestamps": the list of the user's retweet timestamps ordered asc (corresponding to the "timestamps" list)
                                - "retweeted_status_user_ids": the list of the user's retweeted user ids (corresponding to the "timestamps" list)
                                - "hashtags": list of lists, where each element corresponds to the list of hashtags contained in the i-th tweet of the "timestamps" list
                                - "mentions": list of lists, where each element corresponds to the list of mentions (user id) contained in the i-th tweet of the "timestamps" list
                                - "urls": list of lists, where each element corresponds to the list of urls contained in the i-th tweet of the "timestamps" list
                                Example: {  "user_id": 111,
                                            "timestamps": [1601596899.0, 1601597248.0],
                                            "retweeted_status_ids": ["retweet0001", "retweet0002"],
                                            "retweeted_status_timestamps": [1668946003.0, 1668945703.0],
                                            "retweeted_status_user_ids": ["user0001", "user0002"],
                                            "hashtags": [["elections","vote"],["today"]],
                                            "mentions": [["user222"],["user222","user333"]],
                                            "urls": [["http://vote.com",[]]
        - (e.g., "input_data/input_superspreaders_seqs.jsonl")

    """
    output_path = input_dir / Path("input_superspreaders_seqs.jsonl")

    my_print(f"Parsing raw sequences from {raw_sequences_path}...")

    parse_raw_sequences(raw_sequences_path, output_path)

    my_print("Parsed sequences saved to {}.".format(output_path))

    my_print("Finished!")

    return output_path


if __name__ == '__main__':
    # Input example
    input_dir = Path("../input_data/")
    raw_sequences_path = Path("../input_data/input_superspreaders_raw_seqs.jsonl")
    # Function call
    userseq_json_path = parse_sequences(raw_sequences_path, input_dir)
    # Output example
    print(userseq_json_path)  # "../input_data/input_superspreaders_seqs.jsonl"
