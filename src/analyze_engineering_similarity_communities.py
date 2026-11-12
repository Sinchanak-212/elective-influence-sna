"""Compare communities and attribute mixing in engineering profile networks."""

import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.build_engineering_similarity_network import (
    PRIMARY_THRESHOLD,
    build_similarity_graph,
    load_engineering_population,
)


REPORT_DIR = ROOT / "outputs" / "reports"
GRAPH_DIR = ROOT / "outputs" / "graphs"

ASSIGNMENTS_PATH = REPORT_DIR / "engineering_community_assignments.csv"
SUMMARY_PATH = REPORT_DIR / "engineering_community_summary.csv"
MIXING_PATH = REPORT_DIR / "engineering_attribute_mixing.csv"
SENSITIVITY_PATH = REPORT_DIR / "engineering_threshold_sensitivity.csv"
FIGURE_PATH = GRAPH_DIR / "engineering_community_comparison.png"

THRESHOLDS = (0.30, PRIMARY_THRESHOLD, 0.60)
RANDOM_SEED = 42
METHODS = ("Louvain", "Greedy modularity")
MIXING_ATTRIBUTES = (
    "preferred_subject_category",
    "branch",
    "primary_reason",
)


def canonicalize_communities(
    communities: list[set[str]],
) -> list[tuple[str, set[str]]]:
    """Return deterministically ordered, labeled communities."""
    ordered = sorted(communities, key=lambda group: tuple(sorted(group)))
    return [
        (f"C{index:02d}", group)
        for index, group in enumerate(ordered, start=1)
    ]


def detect_communities(
    graph: nx.Graph,
    seed: int = RANDOM_SEED,
) -> dict[str, list[set[str]]]:
    """Run Louvain and greedy modularity, retaining every graph node."""
    if graph.is_directed():
        raise ValueError("Community analysis requires an undirected graph.")

    detected = {
        "Louvain": [
            set(group)
            for group in nx.community.louvain_communities(
                graph,
                weight="weight",
                seed=seed,
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

    expected_nodes = set(graph.nodes)
    for method, groups in detected.items():
        seen: set[str] = set()
        for group in groups:
            if seen.intersection(group):
                raise ValueError(f"{method} returned overlapping communities.")
            seen.update(group)
        if seen != expected_nodes:
            missing = sorted(expected_nodes - seen)
            unexpected = sorted(seen - expected_nodes)
            raise ValueError(
                f"{method} did not partition all graph nodes; "
                f"missing={missing}, unexpected={unexpected}"
            )

    return detected


def _weighted_categorical_assortativity(
    graph: nx.Graph,
    attribute: str,
) -> tuple[float, bool, str]:
    """Calculate weighted categorical assortativity from edge mixing."""
    edge_values = {
        graph.nodes[node][attribute]
        for edge in graph.edges
        for node in edge
    }
    if graph.number_of_edges() == 0:
        return math.nan, False, "no_edges"
    if len(edge_values) < 2:
        return math.nan, False, "fewer_than_two_edge_endpoint_categories"

    categories = sorted(edge_values)
    index = {category: position for position, category in enumerate(categories)}
    mixing = [
        [0.0 for _ in categories]
        for _ in categories
    ]
    for first, second, data in graph.edges(data=True):
        weight = float(data.get("weight", 1.0))
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Mixing weights must be finite and nonnegative.")
        first_index = index[graph.nodes[first][attribute]]
        second_index = index[graph.nodes[second][attribute]]
        mixing[first_index][second_index] += weight
        mixing[second_index][first_index] += weight

    total = sum(sum(row) for row in mixing)
    if total <= 0:
        return math.nan, False, "nonpositive_total_edge_weight"

    matrix = [[value / total for value in row] for row in mixing]
    row_marginals = [sum(row) for row in matrix]
    column_marginals = [
        sum(matrix[row][column] for row in range(len(categories)))
        for column in range(len(categories))
    ]
    expected_agreement = sum(
        row_marginals[position] * column_marginals[position]
        for position in range(len(categories))
    )
    denominator = 1 - expected_agreement
    if denominator <= 1e-12:
        return math.nan, False, "assortativity_denominator_is_zero"

    observed_agreement = sum(
        matrix[position][position]
        for position in range(len(categories))
    )
    coefficient = (observed_agreement - expected_agreement) / denominator
    return coefficient, True, ""


def summarize_attribute_mixing(
    graph: nx.Graph,
    threshold: float,
) -> list[dict[str, object]]:
    """Summarize same-category ties and weighted categorical assortativity."""
    rows = []
    for attribute in MIXING_ATTRIBUTES:
        if any(attribute not in graph.nodes[node] for node in graph.nodes):
            raise ValueError(f"Network nodes are missing attribute {attribute!r}.")

        edge_count = graph.number_of_edges()
        matching_edges = [
            (first, second, data)
            for first, second, data in graph.edges(data=True)
            if graph.nodes[first][attribute] == graph.nodes[second][attribute]
        ]
        total_weight = sum(
            float(data.get("weight", 1.0))
            for _, _, data in graph.edges(data=True)
        )
        matching_weight = sum(
            float(data.get("weight", 1.0))
            for _, _, data in matching_edges
        )
        assortativity, defined, undefined_reason = (
            _weighted_categorical_assortativity(graph, attribute)
        )
        endpoint_categories = {
            graph.nodes[node][attribute]
            for edge in graph.edges
            for node in edge
        }
        rows.append(
            {
                "threshold": threshold,
                "is_primary_threshold": threshold == PRIMARY_THRESHOLD,
                "attribute": attribute,
                "edge_count": edge_count,
                "matching_edge_count": len(matching_edges),
                "matching_edge_fraction": (
                    len(matching_edges) / edge_count if edge_count else math.nan
                ),
                "total_edge_weight": total_weight,
                "matching_edge_weight": matching_weight,
                "matching_edge_weight_fraction": (
                    matching_weight / total_weight if total_weight else math.nan
                ),
                "edge_endpoint_category_count": len(endpoint_categories),
                "weighted_categorical_assortativity": assortativity,
                "assortativity_defined": defined,
                "assortativity_undefined_reason": undefined_reason,
            }
        )
    return rows


def _dominant_category(counts: pd.Series) -> tuple[object, int, float]:
    """Return a unique mode and its share, or None when the mode is tied."""
    maximum = int(counts.max())
    leaders = sorted(value for value, count in counts.items() if count == maximum)
    dominant = leaders[0] if len(leaders) == 1 else None
    return dominant, maximum, maximum / int(counts.sum())


def analyze_communities(
    respondents: pd.DataFrame,
    thresholds: tuple[float, ...] = THRESHOLDS,
    seed: int = RANDOM_SEED,
) -> dict[str, pd.DataFrame]:
    """Analyze both community algorithms at each requested threshold."""
    if PRIMARY_THRESHOLD not in thresholds:
        raise ValueError("Threshold analysis must include the primary threshold 0.50.")
    if len(set(thresholds)) != len(thresholds):
        raise ValueError("Threshold values must be unique.")

    assignment_rows: list[dict[str, object]] = []
    community_summary_rows: list[dict[str, object]] = []
    sensitivity_rows: list[dict[str, object]] = []
    mixing_rows: list[dict[str, object]] = []
    graphs: dict[float, nx.Graph] = {}
    partitions: dict[tuple[float, str], list[set[str]]] = {}
    attribute_by_id = respondents.set_index("respondent_id").to_dict("index")

    for threshold in thresholds:
        graph = build_similarity_graph(respondents, threshold)
        graphs[threshold] = graph
        communities_by_method = detect_communities(graph, seed=seed)
        mixing_rows.extend(summarize_attribute_mixing(graph, threshold))
        component_count = nx.number_connected_components(graph)

        for method in METHODS:
            communities = communities_by_method[method]
            partitions[(threshold, method)] = communities
            canonical = canonicalize_communities(communities)
            modularity = (
                nx.community.modularity(graph, communities, weight="weight")
                if graph.number_of_edges()
                else math.nan
            )
            community_sizes = sorted(
                (len(group) for group in communities),
                reverse=True,
            )
            sensitivity_rows.append(
                {
                    "threshold": threshold,
                    "is_primary_threshold": threshold == PRIMARY_THRESHOLD,
                    "algorithm": method,
                    "node_count": graph.number_of_nodes(),
                    "edge_count": graph.number_of_edges(),
                    "density": nx.density(graph),
                    "connected_component_count": component_count,
                    "community_count": len(communities),
                    "community_sizes": ";".join(
                        str(size) for size in community_sizes
                    ),
                    "weighted_modularity": modularity,
                    "random_seed": seed if method == "Louvain" else "",
                }
            )

            for community_id, members in canonical:
                member_attributes = pd.DataFrame(
                    [attribute_by_id[node] for node in sorted(members)]
                )
                subject_counts = member_attributes[
                    "preferred_subject_category"
                ].value_counts().sort_index()
                branch_counts = member_attributes["branch"].value_counts().sort_index()
                dominant_subject, subject_count, subject_share = _dominant_category(
                    subject_counts
                )
                dominant_branch, branch_count, branch_share = _dominant_category(
                    branch_counts
                )
                community_summary_rows.append(
                    {
                        "threshold": threshold,
                        "is_primary_threshold": threshold == PRIMARY_THRESHOLD,
                        "algorithm": method,
                        "community_id": community_id,
                        "community_size": len(members),
                        "member_respondent_ids": ";".join(sorted(members)),
                        "dominant_preferred_subject_category": dominant_subject,
                        "dominant_subject_count": subject_count,
                        "dominant_subject_share": subject_share,
                        "preferred_subject_category_counts": json.dumps(
                            subject_counts.to_dict(),
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "dominant_branch": dominant_branch,
                        "dominant_branch_count": branch_count,
                        "dominant_branch_share": branch_share,
                        "branch_counts": json.dumps(
                            branch_counts.to_dict(),
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                        "weighted_modularity": modularity,
                    }
                )
                for respondent_id in sorted(members):
                    attributes = attribute_by_id[respondent_id]
                    assignment_rows.append(
                        {
                            "threshold": threshold,
                            "is_primary_threshold": threshold == PRIMARY_THRESHOLD,
                            "algorithm": method,
                            "community_id": community_id,
                            "community_size": len(members),
                            "respondent_id": respondent_id,
                            "preferred_subject_category": attributes[
                                "preferred_subject_category"
                            ],
                            "branch": attributes["branch"],
                        }
                    )

    return {
        "assignments": pd.DataFrame(assignment_rows),
        "community_summary": pd.DataFrame(community_summary_rows),
        "attribute_mixing": pd.DataFrame(mixing_rows),
        "threshold_sensitivity": pd.DataFrame(sensitivity_rows),
        "graphs": graphs,
        "partitions": partitions,
    }


def write_results(results: dict[str, object]) -> None:
    """Write all community analysis tables and the comparison figure."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    results["assignments"].to_csv(ASSIGNMENTS_PATH, index=False)
    results["community_summary"].to_csv(SUMMARY_PATH, index=False)
    results["attribute_mixing"].to_csv(MIXING_PATH, index=False)
    results["threshold_sensitivity"].to_csv(SENSITIVITY_PATH, index=False)
    draw_community_comparison(
        results["graphs"],
        results["partitions"],
        FIGURE_PATH,
    )


def draw_community_comparison(
    graphs: dict[float, nx.Graph],
    partitions: dict[tuple[float, str], list[set[str]]],
    output_path: Path = FIGURE_PATH,
) -> None:
    """Draw comparable community partitions using a shared node layout."""
    layout_graph = graphs[0.30]
    positions = nx.spring_layout(
        layout_graph,
        seed=RANDOM_SEED,
        weight="weight",
        k=1.1,
        iterations=400,
    )
    panels = (
        (0.30, "Louvain"),
        (PRIMARY_THRESHOLD, "Louvain"),
        (0.60, "Louvain"),
        (PRIMARY_THRESHOLD, "Greedy modularity"),
    )
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    for ax, (threshold, method) in zip(axes.flat, panels):
        graph = graphs[threshold]
        communities = canonicalize_communities(
            partitions[(threshold, method)]
        )
        community_for_node = {
            node: community_id
            for community_id, members in communities
            for node in members
        }
        palette = plt.get_cmap("tab20")
        color_by_community = {
            community_id: palette(index % 20)
            for index, (community_id, _) in enumerate(communities)
        }
        nx.draw_networkx_edges(
            graph,
            positions,
            ax=ax,
            edge_color="#667085",
            alpha=0.30,
            width=[
                0.6 + 2.2 * graph[first][second]["weight"]
                for first, second in graph.edges
            ],
        )
        nx.draw_networkx_nodes(
            graph,
            positions,
            ax=ax,
            node_color=[
                color_by_community[community_for_node[node]]
                for node in graph.nodes
            ],
            node_size=260,
            edgecolors="white",
            linewidths=0.9,
        )
        nx.draw_networkx_labels(
            graph,
            positions,
            ax=ax,
            font_size=6,
            font_weight="bold",
            font_color="#182230",
        )
        modularity = nx.community.modularity(
            graph,
            partitions[(threshold, method)],
            weight="weight",
        )
        ax.set_title(
            f"{method} — threshold {threshold:.2f}\n"
            f"{len(communities)} communities; weighted modularity {modularity:.3f}",
            fontsize=11,
            fontweight="semibold",
            pad=10,
        )
        ax.axis("off")

    fig.suptitle(
        "Communities in engineering student profile-similarity networks",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.02,
        "Fixed layout across panels; edge width reflects similarity score. "
        "Communities indicate profile similarity, not observed friendships or influence.",
        ha="center",
        fontsize=9,
        color="#475467",
    )
    fig.tight_layout(rect=(0.02, 0.05, 0.98, 0.95))
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    respondents = load_engineering_population()
    results = analyze_communities(respondents)
    write_results(results)

    print("Engineering respondents:", len(respondents))
    print("Primary threshold:", f"{PRIMARY_THRESHOLD:.2f}")
    print("Community assignments:", ASSIGNMENTS_PATH)
    print("Community profiles:", SUMMARY_PATH)
    print("Attribute mixing:", MIXING_PATH)
    print("Threshold sensitivity:", SENSITIVITY_PATH)
    print("Community comparison figure:", FIGURE_PATH)
    print("\nThreshold and method comparison:")
    print(
        results["threshold_sensitivity"][
            [
                "threshold",
                "algorithm",
                "edge_count",
                "community_count",
                "community_sizes",
                "weighted_modularity",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
