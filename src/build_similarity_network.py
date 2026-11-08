import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
GRAPH_PATH = ROOT / "outputs" / "graphs" / "student_similarity_network.png"
GRAPHML_PATH = ROOT / "outputs" / "graphs" / "student_similarity_network.graphml"
EDGES_PATH = ROOT / "data" / "processed" / "similarity_edges.csv"

GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
EDGES_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Create an undirected graph
G = nx.Graph()

# Add all students as nodes
for _, row in df.iterrows():
    G.add_node(
        row["respondent_id"],
        subject_category=row["preferred_subject_category"]
    )

# Compare every pair of students
for i in range(len(df)):
    for j in range(i + 1, len(df)):

        student1 = df.iloc[i]
        student2 = df.iloc[j]

        if student1["preferred_subject_category"] == student2["preferred_subject_category"]:
            G.add_edge(
                student1["respondent_id"],
                student2["respondent_id"],
                weight=1,
                similarity="Same preferred subject category"
            )

# Assign colors based on subject category
categories = sorted(df["preferred_subject_category"].unique())
color_map = {
    category: plt.cm.tab10(i % 10)
    for i, category in enumerate(categories)
}

node_colors = [
    color_map[G.nodes[node]["subject_category"]]
    for node in G.nodes()
]

# Calculate layout
positions = nx.spring_layout(G, seed=42, k=0.9)

# Draw graph
plt.figure(figsize=(15, 11))

nx.draw_networkx_edges(
    G, positions,
    alpha=0.35,
    width=1.2,
    edge_color="gray"
)

nx.draw_networkx_nodes(
    G, positions,
    node_color=node_colors,
    node_size=750,
    edgecolors="black",
    linewidths=0.6
)

nx.draw_networkx_labels(
    G, positions,
    font_size=8,
    font_weight="bold"
)

plt.title(
    "Student Preferred Subject Similarity Network",
    fontsize=16
)

plt.axis("off")
plt.tight_layout()
plt.savefig(GRAPH_PATH, dpi=300, bbox_inches="tight")
plt.show()

# Calculate network metrics
degree_centrality = nx.degree_centrality(G)
components = list(nx.connected_components(G))

# Export edge list
edge_df = pd.DataFrame(
    [
        {
            "student_1": u,
            "student_2": v,
            "weight": data["weight"]
        }
        for u, v, data in G.edges(data=True)
    ],
    columns=["student_1", "student_2", "weight"]
)

edge_df.to_csv(EDGES_PATH, index=False)
nx.write_graphml(G, GRAPHML_PATH)

print("\n===== SIMILARITY NETWORK ANALYSIS =====")
print("Total students:", G.number_of_nodes())
print("Total similarity connections:", G.number_of_edges())
print("Connected components:", len(components))
print("Largest component size:", max(map(len, components)))
print("Network density:", round(nx.density(G), 3))

print("\n===== DEGREE CENTRALITY =====")
for student, score in sorted(
    degree_centrality.items(),
    key=lambda item: item[1],
    reverse=True
):
    print(student, ":", round(score, 3))

print("\n===== OUTPUT FILES =====")
print(GRAPH_PATH)
print(GRAPHML_PATH)
print(EDGES_PATH)
