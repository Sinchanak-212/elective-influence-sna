import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
EDGE_PATH = ROOT / "data" / "processed" / "weighted_similarity_edges.csv"
REPORT_DIR = ROOT / "outputs" / "reports"
GRAPH_PATH = ROOT / "outputs" / "graphs" / "similarity_communities_louvain.png"
ASSIGNMENTS_PATH = REPORT_DIR / "similarity_community_assignments.csv"
SUMMARY_PATH = REPORT_DIR / "similarity_community_summary.csv"

THRESHOLDS = (0.30, 0.60)
RANDOM_SEED = 42


def _canonicalize(
    communities: list[set[str]],
) -> list[tuple[str, set[str]]]:
    ordered = sorted(communities, key=lambda group: tuple(sorted(group)))
    return [
        (f"C{index:02d}", group)
        for index, group in enumerate(ordered, start=1)
    ]


def _partitions(graph: nx.Graph) -> dict[str, list[set[str]]]:
    return {
        "Louvain": [
            set(group)
            for group in nx.community.louvain_communities(
                graph,
                weight="weight",
                seed=RANDOM_SEED,
            )
        ],
        "Greedy modularity": [
            set(group)
            for group in nx.community.greedy_modularity_communities(
                graph,
                weight="weight",
            )
        ],
    }


def main() -> None:
    respondents = pd.read_csv(DATA_PATH)
    edges = pd.read_csv(EDGE_PATH)
    required_respondent_columns = {
        "respondent_id",
        "preferred_subject_category",
    }
    required_edge_columns = {"student_1", "student_2", "similarity_score"}
    if missing := sorted(required_respondent_columns - set(respondents.columns)):
        raise ValueError(f"Survey is missing required columns: {missing}")
    if missing := sorted(required_edge_columns - set(edges.columns)):
        raise ValueError(f"Similarity edge file is missing required columns: {missing}")
    if respondents["respondent_id"].isna().any() or not respondents[
        "respondent_id"
    ].is_unique:
        raise ValueError("Respondent IDs must be present and unique.")

    edges["similarity_score"] = pd.to_numeric(
        edges["similarity_score"], errors="raise"
    )
    if (
        edges["similarity_score"].isna().any()
        or not edges["similarity_score"].between(0, 1, inclusive="right").all()
    ):
        raise ValueError("Similarity scores must be finite values in (0, 1].")

    respondent_ids = set(respondents["respondent_id"])
    unknown_ids = (
        set(edges["student_1"]) | set(edges["student_2"])
    ) - respondent_ids
    if unknown_ids:
        raise ValueError(f"Edge file contains unknown respondent IDs: {sorted(unknown_ids)}")
    if (edges["student_1"] == edges["student_2"]).any():
        raise ValueError("Similarity network must not contain self-loops.")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    assignment_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    louvain_partitions: dict[float, list[set[str]]] = {}
    subject_by_id = respondents.set_index("respondent_id")[
        "preferred_subject_category"
    ].to_dict()

    for threshold in THRESHOLDS:
        graph = nx.Graph()
        for respondent_id in respondents["respondent_id"]:
            graph.add_node(respondent_id)

        selected_edges = edges.loc[edges["similarity_score"] >= threshold]
        for row in selected_edges.itertuples(index=False):
            if graph.has_edge(row.student_1, row.student_2):
                raise ValueError("Similarity edge file contains duplicate node pairs.")
            graph.add_edge(
                row.student_1,
                row.student_2,
                weight=float(row.similarity_score),
            )

        if graph.number_of_edges() == 0:
            raise ValueError(
                f"No similarity edges remain at threshold {threshold:.2f}."
            )

        for algorithm, communities in _partitions(graph).items():
            canonical_communities = _canonicalize(communities)
            score = nx.community.modularity(
                graph,
                communities,
                weight="weight",
            )
            summary_rows.append(
                {
                    "threshold": threshold,
                    "algorithm": algorithm,
                    "nodes": graph.number_of_nodes(),
                    "edges": graph.number_of_edges(),
                    "community_count": len(communities),
                    "community_sizes": ";".join(
                        str(len(group)) for _, group in canonical_communities
                    ),
                    "weighted_modularity": round(score, 6),
                }
            )
            for community_id, members in canonical_communities:
                for respondent_id in sorted(members):
                    assignment_rows.append(
                        {
                            "threshold": threshold,
                            "algorithm": algorithm,
                            "respondent_id": respondent_id,
                            "community_id": community_id,
                            "preferred_subject_category": subject_by_id[
                                respondent_id
                            ],
                        }
                    )
            if algorithm == "Louvain":
                louvain_partitions[threshold] = communities

    pd.DataFrame(assignment_rows).to_csv(ASSIGNMENTS_PATH, index=False)
    pd.DataFrame(summary_rows).to_csv(SUMMARY_PATH, index=False)

    fig, axes = plt.subplots(1, len(THRESHOLDS), figsize=(16, 8))
    for ax, threshold in zip(axes, THRESHOLDS):
        graph = nx.Graph()
        for respondent_id in respondents["respondent_id"]:
            graph.add_node(respondent_id)
        for row in edges.loc[edges["similarity_score"] >= threshold].itertuples(
            index=False
        ):
            graph.add_edge(
                row.student_1,
                row.student_2,
                weight=float(row.similarity_score),
            )

        communities = _canonicalize(louvain_partitions[threshold])
        community_for_node = {
            member: community_id
            for community_id, members in communities
            for member in members
        }
        community_ids = [community_id for community_id, _ in communities]
        palette = plt.get_cmap("tab20")
        color_for_community = {
            community_id: palette(index % 20)
            for index, community_id in enumerate(community_ids)
        }
        positions = nx.spring_layout(
            graph,
            seed=RANDOM_SEED,
            weight="weight",
        )
        nx.draw_networkx_edges(
            graph,
            positions,
            ax=ax,
            edge_color="#888888",
            alpha=0.35,
            width=1.1,
        )
        nx.draw_networkx_nodes(
            graph,
            positions,
            ax=ax,
            node_color=[
                color_for_community[community_for_node[node]]
                for node in graph.nodes()
            ],
            node_size=620,
            edgecolors="black",
            linewidths=0.5,
        )
        nx.draw_networkx_labels(
            graph,
            positions,
            ax=ax,
            font_size=7,
        )
        ax.set_title(
            f"Louvain; similarity ≥ {threshold:.2f}\n"
            f"{len(communities)} inferred communities"
        )
        ax.axis("off")

    fig.suptitle(
        "Communities in weighted profile-similarity networks\n"
        "Groups indicate survey-profile similarity, not observed friendships or influence",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(GRAPH_PATH, dpi=250, bbox_inches="tight")
    plt.close(fig)

    print("Community detection: weighted Louvain and greedy modularity benchmark")
    print("Thresholds:", ", ".join(f"{threshold:.2f}" for threshold in THRESHOLDS))
    print("Assignments saved:", ASSIGNMENTS_PATH)
    print("Method summary saved:", SUMMARY_PATH)
    print("Louvain visualization saved:", GRAPH_PATH)


if __name__ == "__main__":
    main()
