import sys
from include.lib import my_print
from pathlib import Path
from pipeline.parse_sequences import parse_sequences
from pipeline.compute_user_vector_models import compute_user_vector_models
from pipeline.save_user_similarities import save_user_similarities
from pipeline.add_multiscale_backbone_to_edgelist import add_multiscale_backbone_to_edgelist
from pipeline.filter_edgelist import filter_edgelist
from pipeline.compute_seed_communities import compute_seed_communities
from pipeline.compute_coordinated_groups import compute_coordinated_groups
from pipeline.compute_user_coordination import compute_user_coordination
from pipeline.coordinated_groups_of_interest_metadata import coordinated_groups_of_interest_metadata
from pipeline.draw_user_similarity_network import draw_user_similarity_network
from pipeline.wordcloud_narratives import wordcloud_narratives
from pipeline.compute_size_vs_coordination import compute_size_vs_coordination


def main(input_filepath, output_directory):

	raw_sequences_path = Path(input_filepath)  # input data
	input_dir = Path("input_data/")
	outdir = Path("output") / Path(output_directory)
	# create directories
	Path(input_dir).mkdir(parents = True, exist_ok = True)
	Path(outdir).mkdir(parents = True, exist_ok = True)

	my_print("PARSING INPUT DATA")
	#user_sequences_json_path = parse_sequences(raw_sequences_path, input_dir)  # output: "input_data/input_superspreaders_seqs.jsonl"
	user_sequences_json_path = "input_data/input_superspreaders_seqs.jsonl"

	my_print("COMPUTING USER VECTOR MODELS")
	user_vector_models_path  = compute_user_vector_models(user_sequences_json_path, outdir)

	my_print("CREATING THE USER SIMILARITY NETWORK")
	node_csv_path, edge_csv_path = save_user_similarities(user_vector_models_path, outdir)

	my_print("COMPUTING AND FILTERING THE USER SIMILARITY NETWORK BACKBONE")
	edge_csv_path = add_multiscale_backbone_to_edgelist(node_csv_path, edge_csv_path)
	alpha = 0.15
	filtered_node_csv_path, filtered_edge_csv_path, outdir_backbone = filter_edgelist(edge_csv_path, alpha, outdir)

	my_print("COMPUTING SEED COMMUNITIES")
	louvain_resolution = 1
	filtered_node_communities_csv_path, seed_mod_path, outdir_communities = compute_seed_communities(filtered_node_csv_path, filtered_edge_csv_path, louvain_resolution, outdir_backbone)

	my_print("COMPUTING COORDINATION-AWARE COMMUNITY DETECTION FROM SEEDS")
	min_cardinality = 2
	coordinated_groups_path, coordinated_groups_stats_csv_path, outdir_coordination_aware = compute_coordinated_groups(filtered_node_communities_csv_path, filtered_edge_csv_path, seed_mod_path, outdir_communities, louvain_resolution, min_cardinality)

	my_print("COMPUTE USER COORDINATION LEVELS")
	filtered_node_coordination_csv_path = compute_user_coordination(coordinated_groups_path, filtered_node_communities_csv_path, outdir_coordination_aware)

	my_print("PLOTTING NETWORK VISUALIZATIONS FOR COMMUNITIES OF INTEREST")
	metadata_top_communities = 10
	metadata_min_cardinality = 2
	communities_metadata_path, outdir_plots = coordinated_groups_of_interest_metadata(filtered_node_coordination_csv_path, coordinated_groups_path, metadata_min_cardinality, metadata_top_communities, user_vector_models_path, outdir_coordination_aware)
	plot_network_communities_path = draw_user_similarity_network(filtered_node_coordination_csv_path, filtered_edge_csv_path, communities_metadata_path, coordinated_groups_path, outdir_plots)
	plot_hashtagcloud_communities_path = wordcloud_narratives(filtered_node_coordination_csv_path, communities_metadata_path, user_vector_models_path, outdir_plots)
	plot_metrics_coordination_path = compute_size_vs_coordination(coordinated_groups_stats_csv_path, communities_metadata_path, outdir_plots)
	my_print(f"Saved plots in path {outdir_plots}")

	my_print("END")


if __name__ == "__main__":
	input_filepath = sys.argv[1] if len(sys.argv) >= 2 else Path("input_data/input_superspreaders_raw_seqs.jsonl")
	output_directory = sys.argv[2] if len(sys.argv) >=3 else Path("output_superspreaders/")
	main(input_filepath, output_directory)

