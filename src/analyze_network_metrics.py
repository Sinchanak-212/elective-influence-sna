import pandas as pd
import networkx as nx
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data/raw/survey_responses_anonymized.csv"
EDGE_PATH = ROOT / "data/processed/weighted_similarity_edges.csv"
OUTPUT_PATH = ROOT / "data/processed/network_centrality_metrics.csv"

THRESHOLD = 0.60

df = pd.read_csv(DATA_PATH)
edges = pd.read_csv(EDGE_PATH)

G = nx.Graph()

for student in df["respondent_id"]:
    G.add_node(student)

for _, edge in edges.iterrows():
    score = float(edge["similarity_score"])

    if score >= THRESHOLD:
        G.add_edge(
            edge["student_1"],
            edge["student_2"],
            weight=score,
            distance=1 / score
        )

degree = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(
    G, weight="distance", normalized=True
)
closeness = nx.closeness_centrality(
    G, distance="distance"
)
strength = dict(G.degree(weight="weight"))

results = pd.DataFrame({
    "student": list(G.nodes()),
    "degree_centrality": [degree[n] for n in G.nodes()],
    "betweenness_centrality": [betweenness[n] for n in G.nodes()],
    "closeness_centrality": [closeness[n] for n in G.nodes()],
    "weighted_degree": [strength[n] for n in G.nodes()]
})

results = results.sort_values(
    "degree_centrality",
    ascending=False
)

results.to_csv(OUTPUT_PATH, index=False)

print("\n===== NETWORK CENTRALITY ANALYSIS =====")
print("Students:", G.number_of_nodes())
print("Strong connections:", G.number_of_edges())
print("Connected components:", nx.number_connected_components(G))

for metric in [
    "degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "weighted_degree"
]:
    print(f"\nTOP 5  {metric.upper()}")
    print(
        results.nlargest(5, metric)[["student", metric]]
        .to_string(index=False)
    )

print("\nIsolated students:", list(nx.isolates(G)))
print("\nResults saved:", OUTPUT_PATH)
