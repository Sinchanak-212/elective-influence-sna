"""Build the engineering-only weighted profile-similarity network."""

from itertools import combinations
from math import isfinite
from pathlib import Path

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

NODE_PATH = OUTPUT_DIR / "engineering_similarity_nodes.csv"
EDGE_PATH = OUTPUT_DIR / "engineering_similarity_edges.csv"
SUMMARY_PATH = OUTPUT_DIR / "engineering_network_summary.csv"
COMPONENT_PATH = OUTPUT_DIR / "engineering_similarity_components.csv"

PRIMARY_THRESHOLD = 0.50
ATTRIBUTE_WEIGHTS = {
    "preferred_subject_category": 0.50,
    "branch": 0.20,
    "primary_reason": 0.20,
    "year": 0.10,
}
REQUIRED_COLUMNS = (
    "respondent_id",
    "branch",
    "year",
    "primary_reason",
    "preferred_subject_category",
)


def load_engineering_population(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and validate the survey, excluding non-engineering respondents."""
    respondents = pd.read_csv(path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(respondents.columns))
    if missing_columns:
        raise ValueError(f"Survey is missing required columns: {missing_columns}")

    if respondents[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Required similarity fields contain missing values.")

    for column in REQUIRED_COLUMNS:
        respondents[column] = respondents[column].astype(str).str.strip()
        if respondents[column].eq("").any():
            raise ValueError(f"Required similarity field {column!r} is blank.")

    if respondents["respondent_id"].duplicated().any():
        raise ValueError("Respondent IDs must be unique.")

    is_law = respondents["branch"].str.casefold().eq("law")
    engineering = respondents.loc[~is_law].copy()
    if engineering.empty:
        raise ValueError("No engineering respondents remain after filtering Law.")

    return engineering.reset_index(drop=True)


def _similarity_score(
    first: dict[str, object], second: dict[str, object]
) -> tuple[float, tuple[str, ...]]:
    shared_attributes = tuple(
        attribute
        for attribute in ATTRIBUTE_WEIGHTS
        if first[attribute] == second[attribute]
    )
    score = round(sum(ATTRIBUTE_WEIGHTS[name] for name in shared_attributes), 2)
    return score, shared_attributes


def build_similarity_graph(
    respondents: pd.DataFrame,
    threshold: float = PRIMARY_THRESHOLD,
) -> nx.Graph:
    """Build a weighted graph from shared survey attributes at a threshold."""
    if not isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Similarity threshold must be a finite value from 0 to 1.")

    graph = nx.Graph()
    for row in respondents.to_dict("records"):
        respondent_id = row["respondent_id"]
        graph.add_node(
            respondent_id,
            **{column: row[column] for column in REQUIRED_COLUMNS if column != "respondent_id"},
        )

    records = respondents.to_dict("records")
    for first, second in combinations(records, 2):
        score, shared_attributes = _similarity_score(first, second)
        if score >= threshold:
            graph.add_edge(
                first["respondent_id"],
                second["respondent_id"],
                weight=score,
                distance=1 / score,
                shared_attributes=", ".join(shared_attributes),
            )

    return graph


def analyze_similarity_graph(
    graph: nx.Graph,
    threshold: float = PRIMARY_THRESHOLD,
) -> dict[str, pd.DataFrame]:
    """Create node metrics, edge, component-membership, and summary tables."""
    components = sorted(
        (set(component) for component in nx.connected_components(graph)),
        key=lambda component: min(component),
    )
    component_for_node = {
        node: (f"C{index:02d}", len(component))
        for index, component in enumerate(components, start=1)
        for node in component
    }

    degree_centrality = nx.degree_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(
        graph,
        weight="distance",
        normalized=True,
    )
    closeness_centrality = nx.closeness_centrality(graph, distance="distance")
    strength = dict(graph.degree(weight="weight"))

    node_rows = []
    component_rows = []
    for respondent_id in sorted(graph.nodes):
        attributes = graph.nodes[respondent_id]
        component_id, component_size = component_for_node[respondent_id]
        is_isolated = graph.degree(respondent_id) == 0
        node_rows.append(
            {
                "respondent_id": respondent_id,
                "branch": attributes["branch"],
                "year": attributes["year"],
                "preferred_subject_category": attributes[
                    "preferred_subject_category"
                ],
                "primary_reason": attributes["primary_reason"],
                "component_id": component_id,
                "component_size": component_size,
                "is_isolated": is_isolated,
                "degree": graph.degree(respondent_id),
                "degree_centrality": degree_centrality[respondent_id],
                "betweenness_centrality": betweenness_centrality[respondent_id],
                "closeness_centrality": closeness_centrality[respondent_id],
                "weighted_degree_strength": strength[respondent_id],
            }
        )
        component_rows.append(
            {
                "respondent_id": respondent_id,
                "component_id": component_id,
                "component_size": component_size,
                "is_isolated": is_isolated,
            }
        )

    edge_rows = [
        {
            "student_1": first,
            "student_2": second,
            "similarity_score": attributes["weight"],
            "shared_attributes": attributes["shared_attributes"],
        }
        for first, second, attributes in graph.edges(data=True)
    ]
    edge_rows.sort(key=lambda edge: (edge["student_1"], edge["student_2"]))

    isolated_nodes = sorted(nx.isolates(graph))
    summary = pd.DataFrame(
        [
            {
                "population": "engineering_only",
                "similarity_threshold": threshold,
                "node_count": graph.number_of_nodes(),
                "edge_count": graph.number_of_edges(),
                "density": nx.density(graph),
                "connected_component_count": len(components),
                "largest_component_size": max(
                    (len(component) for component in components), default=0
                ),
                "component_sizes": ";".join(
                    str(len(component)) for component in components
                ),
                "isolated_node_count": len(isolated_nodes),
                "isolated_respondent_ids": ";".join(isolated_nodes),
            }
        ]
    )

    return {
        "nodes": pd.DataFrame(node_rows),
        "edges": pd.DataFrame(
            edge_rows,
            columns=[
                "student_1",
                "student_2",
                "similarity_score",
                "shared_attributes",
            ],
        ),
        "components": pd.DataFrame(component_rows),
        "summary": summary,
    }


def write_analysis(tables: dict[str, pd.DataFrame]) -> None:
    """Write the new engineering-only network outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tables["nodes"].to_csv(NODE_PATH, index=False)
    tables["edges"].to_csv(EDGE_PATH, index=False)
    tables["summary"].to_csv(SUMMARY_PATH, index=False)
    tables["components"].to_csv(COMPONENT_PATH, index=False)


def main() -> None:
    respondents = load_engineering_population()
    graph = build_similarity_graph(respondents)
    tables = analyze_similarity_graph(graph)
    write_analysis(tables)

    summary = tables["summary"].iloc[0]
    print("Engineering respondents:", summary["node_count"])
    print("Similarity threshold:", f"{PRIMARY_THRESHOLD:.2f}")
    print("Edges:", summary["edge_count"])
    print("Density:", f"{summary['density']:.6f}")
    print("Connected components:", summary["connected_component_count"])
    print("Isolated respondents:", summary["isolated_respondent_ids"] or "None")
    print("Nodes and centrality metrics:", NODE_PATH)
    print("Edges:", EDGE_PATH)
    print("Component membership:", COMPONENT_PATH)
    print("Network summary:", SUMMARY_PATH)


if __name__ == "__main__":
    main()
