import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data/raw/survey_responses_anonymized.csv"
GRAPH_PATH = ROOT / "outputs/graphs/weighted_similarity_network.png"
EDGE_PATH = ROOT / "data/processed/weighted_similarity_edges.csv"

GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
EDGE_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Importance of each attribute
weights = {
    "preferred_subject_category": 0.50,
    "branch": 0.20,
    "primary_reason": 0.20,
    "year": 0.10
}

THRESHOLD = 0.30

G = nx.Graph()

# Add student nodes
for _, row in df.iterrows():
    G.add_node(
        row["respondent_id"],
        subject=row["preferred_subject_category"]
    )

# Compare every pair
for i in range(len(df)):
    for j in range(i + 1, len(df)):

        a = df.iloc[i]
        b = df.iloc[j]

        score = 0
        common = []

        for attribute, weight in weights.items():
            if a[attribute] == b[attribute]:
                score += weight
                common.append(attribute)

        if score >= THRESHOLD:
            G.add_edge(
                a["respondent_id"],
                b["respondent_id"],
                weight=round(score, 2),
                shared_attributes=", ".join(common)
            )

# Visualize network
positions = nx.spring_layout(G, seed=42, k=0.8)

subjects = sorted(df["preferred_subject_category"].unique())
palette = plt.cm.tab10

color_map = {
    subject: palette(i % 10)
    for i, subject in enumerate(subjects)
}

node_colors = [
    color_map[G.nodes[node]["subject"]]
    for node in G.nodes()
]

plt.figure(figsize=(15, 11))

nx.draw_networkx_edges(
    G, positions,
    width=[
        1 + G[u][v]["weight"] * 4
        for u, v in G.edges()
    ],
    edge_color="gray",
    alpha=0.5
)

nx.draw_networkx_nodes(
    G, positions,
    node_color=node_colors,
    node_size=750,
    edgecolors="black"
)

nx.draw_networkx_labels(
    G, positions,
    font_size=8
)

plt.title(
    "Weighted Student Profile Similarity Network",
    fontsize=16
)

plt.axis("off")
plt.tight_layout()
plt.savefig(GRAPH_PATH, dpi=300, bbox_inches="tight")
plt.close()

# Network metrics
components = list(nx.connected_components(G))
centrality = nx.degree_centrality(G)
strength = dict(G.degree(weight="weight"))

# Export connections
edges = [
    {
        "student_1": u,
        "student_2": v,
        "similarity_score": data["weight"],
        "shared_attributes": data["shared_attributes"]
    }
    for u, v, data in G.edges(data=True)
]

pd.DataFrame(
    edges,
    columns=[
        "student_1",
        "student_2",
        "similarity_score",
        "shared_attributes"
    ]
).to_csv(EDGE_PATH, index=False)

print("\n===== WEIGHTED SIMILARITY ANALYSIS =====")
print("Students:", G.number_of_nodes())
print("Connections:", G.number_of_edges())
print("Connected components:", len(components))
print("Largest component:", max(map(len, components)))
print("Network density:", round(nx.density(G), 3))

print("\n===== DEGREE CENTRALITY =====")
for student, value in sorted(
    centrality.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(student, round(value, 3))

print("\n===== WEIGHTED DEGREE (STRENGTH) =====")
for student, value in sorted(
    strength.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(student, round(value, 2))

print("\nGraph saved:", GRAPH_PATH)
print("Edges saved:", EDGE_PATH)
