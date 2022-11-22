# Framework-to-identify-online-coordinated-behavior

This framework identifies coordinated behavior by analysing the activity traces (sequences) of social media users.
In particular, given a set of users and their tweets, the framework builds a user similarity network where 
the nodes are the users and the edges are weighted according to their retweet similarities, which is proxy of coordination. Then, it filters the network in 
order to retain the backbone of the network. Next, it extracts the communties with a modified 
version of the louvain algorithm that takes into consideration the evolution of communities at all coordination levels (edge weight similarity thresholds). 
Finally, it performs some statistics and visualizations of the most coordinated communities.

Detailed information about the framework are explained here: *to-be-added*


## Usage

This repository is self-contained and can be run as a standalone repository. 
The framework is composed of a pipeline (directory `pipeline`) where each module can be customized
using parameters. The stages of the pipeline must run in order as coded in the example script `process_pipeline.py`
To run the example script: `python process_pipeline_test.py`
Each module can be run on its own but the proper input needs to be specified in the code.
When dealing with big data, we suggest to run single stages of the pipeline, as they may require more computational time.

### Input data

The input data must be a jsonl file, where each line is a json corresponding to a user.
Each json contains:
- *user_id*;
- *timestamps*: the list of its tweets' timestamps, in ascending order;
- *raw_sequences*: the list of the user's tweet objs, in ascending order such that the i-th "timestamp" is the timestamp of the i-th tweet in "raw_sequences".

Example: ```{"user_id": 111, "timestamps": [1601596899.0, 1601597248.0], "raw_sequences": [{"id":"tweet1", "timestamp": 1601596899.0,"entities": {...}, "retweeted_status": {"id":"retweet1"}, etc.},{"id":"tweet2", "timestamp":1601597248.0, "entities": {...}, "retweeted_status": {...}, etc.}] }```

An example of input data is provided in `input_data/example_input_superspreaders_raw_seqs.jsonl` and used when running the example script (`process_pipeline_test.py`), if not otherwise specified.
It contains user information and tweets with ids replaced with random ids.


### Output data

The output, all intermediate files of support and other subdirectories, and the final images will be stored in a subdirectory under the `output` directory. 
Example of the output is in `output/example_output`, which referes to the input data `input_data/example_input_superspreaders_raw_seqs.jsonl`.
The output direcrory of the example script `process_pipeline_test.py` is `output/output_superspreaders`, if not otherwise specified.


### Pipeline modules

The stages of the pipeline must be run in the following order (as done in `process_pipeline_test.py):
1. `parse_sequences.py` : Parse a input jsonl file of users and their twitter objects and returns a jsonl file with parsed and formatted relevant information as follows:
    - *user_id*;
    - *timestamps*: the list of its tweets' timestamps ordered asc;
    - *retweeted_status_ids*: the list of the user's retweet ids ordered asc (corresponding to the *timestamps* list);
    - *retweeted_status_timestamps*: the list of the user's retweet timestamps ordered asc (corresponding to the *timestamps* list);
    - *retweeted_status_user_ids*: the list of the user's retweeted user ids (corresponding to the *timestamps* list);
    - *hashtags*: list of lists, where each element corresponds to the list of hashtags contained in the i-th tweet of the *timestamps* list;
    - *mentions*: list of lists, where each element corresponds to the list of mentions (i.e., mentioned user ids) contained in the i-th tweet of the *timestamps* list;
    - *urls*: list of lists, where each element corresponds to the list of urls contained in the i-th tweet of the *timestamps* list.

    Example: ```{"user_id": 111,
                "timestamps": [1601596899.0, 1601597248.0],
                "retweeted_status_ids": ["retweet0001", "retweet0002"],
                "retweeted_status_timestamps": [1668946003.0, 1668945703.0],
                "retweeted_status_user_ids": ["user0001", "user0002"],
                "hashtags": [["elections","vote"],["today"]],
                "mentions": [["user222"],["user222","user333"]],
                "urls": [["http://vote.com",[]]```
    
    This module is for parsing the input. if one can provide an input file already formatted in this way this step can be skipped.
2. `compute_user_vector_models.py` : Computes user vector models for retweets and hashtags using gensim. Different models could be implemented by modifying the script (e.g., mentions).
3. `save_user_similarities.py` : Computes the the user similarity network where the nodes are the users and the edges are weighted based on the retweet similarities of the user vector models of retweets. Different models could be implemented and used by modifying the script in order to create networks based on the similarity of other activities (e.g., hasthags, mentions). 
4. `add_multiscale_backbone_to_edgelist.py` : Computes the significance scores (i.e., alpha) of edge weights in networks.
5. `filter_edgelist.py` : Computes the network backbone by filtering the nodes and edges in order to keep the edges with a significance score (i.e., alpha) lower than the alpha parameter.
6. `compute_seed_communities.py` : Computes the communities of the network backbone. This communities will be used as seed for the coordination-aware community detection.
7. `compute_coordinated_groups.py` : Applies coordination-aware community detection. Starting from the communities extracted as seed, it applies increansingly restrictive threshold to isolate nodes that survive, corresponding to increasingly coordinated users.
8. `compute_user_coordination.py` : Computes for nodes/users information about their coordination levels.
9. `coordinated_groups_of_interest_metadata.py` : Computes metadata about a subset of coordinated communities to analyse and visualize (e.g, assigns label, color, etc.).
10. `draw_user_similarity_network.py` : Creates a visualization of the user similarity network and the communities, with nodes color-coded based on their coordination level.
11. `wordcloud_narratives.py` : Creates the hashtag cloud visualization of the communities under investigation.
12. `compute_size_vs_coordination.py` : Creates a plot for the communities under investigation comparing their coordination vs their network metrics (e.g., size) and assigns the community coordination value.


## Please cite the following works

*to-be-added*


