import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from textwrap import fill

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
OUTPUT_PATH = ROOT / "outputs" / "graphs" / "subject_grade_network.png"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Create a weighted bipartite graph
G = nx.Graph()

subjects = sorted(df["preferred_subject_category"].unique())
outcomes = sorted(df["academic_outcome"].unique())

# Add nodes
for subject in subjects:
    G.add_node(subject, node_type="subject")

for outcome in outcomes:
    G.add_node(outcome, node_type="outcome")

# Count combinations and create weighted edges
counts = df.groupby(
    ["preferred_subject_category", "academic_outcome"]
).size()

for (subject, outcome), weight in counts.items():
    G.add_edge(subject, outcome, weight=int(weight))

# Position subject nodes on the left and outcome nodes on the right
positions = {}

for i, subject in enumerate(subjects):
    positions[subject] = (0, 1 - i / max(len(subjects) - 1, 1))

for i, outcome in enumerate(outcomes):
    positions[outcome] = (1, 1 - i / max(len(outcomes) - 1, 1))

# Draw graph
plt.figure(figsize=(17, 11))

nx.draw_networkx_nodes(
    G, positions,
    nodelist=subjects,
    node_color="skyblue",
    node_size=2600
)

nx.draw_networkx_nodes(
    G, positions,
    nodelist=outcomes,
    node_color="lightgreen",
    node_size=2600
)

edges = list(G.edges(data=True))
edge_widths = [1 + data["weight"] * 1.2 for _, _, data in edges]

nx.draw_networkx_edges(
    G, positions,
    width=edge_widths,
    edge_color="gray",
    alpha=0.7
)

labels = {
    node: fill(node, width=22)
    for node in G.nodes()
}

nx.draw_networkx_labels(
    G, positions,
    labels=labels,
    font_size=8
)

edge_labels = {
    (u, v): data["weight"]
    for u, v, data in edges
}

nx.draw_networkx_edge_labels(
    G, positions,
    edge_labels=edge_labels,
    font_size=9
)

plt.title(
    "Preferred Subject Category vs Academic Outcome",
    fontsize=16
)

plt.text(0, 1.08, "SUBJECT CATEGORIES", ha="center", fontsize=11)
plt.text(1, 1.08, "ACADEMIC OUTCOMES", ha="center", fontsize=11)

plt.axis("off")
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
plt.show()

print("\n===== GRAPH SUMMARY =====")
print("Total nodes:", G.number_of_nodes())
print("Total edges:", G.number_of_edges())
print("Graph type: Weighted bipartite graph")
print("Saved graph to:", OUTPUT_PATH)
