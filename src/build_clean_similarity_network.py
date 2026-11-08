import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data/raw/survey_responses_anonymized.csv"
EDGE_PATH = ROOT / "data/processed/weighted_similarity_edges.csv"
OUTPUT_PATH = ROOT / "outputs/graphs/weighted_similarity_network_clean.png"

THRESHOLD = 0.60

df = pd.read_csv(DATA_PATH)
edges_df = pd.read_csv(EDGE_PATH)

G = nx.Graph()

# Include all students, even those without strong connections
for _, row in df.iterrows():
    G.add_node(
        row["respondent_id"],
        subject=row["preferred_subject_category"]
    )

# Include only stronger similarity connections
filtered = edges_df[
    edges_df["similarity_score"] >= THRESHOLD
]

for _, row in filtered.iterrows():
    G.add_edge(
        row["student_1"],
        row["student_2"],
        weight=row["similarity_score"]
    )

# Separate nodes visually
positions = nx.spring_layout(
    G,
    seed=42,
    k=1.4,
    iterations=300
)

# Assign colors by preferred subject category
subjects = sorted(df["preferred_subject_category"].unique())
palette = plt.cm.tab20

color_map = {
    subject: palette(i / max(len(subjects), 1))
    for i, subject in enumerate(subjects)
}

node_colors = [
    color_map[G.nodes[node]["subject"]]
    for node in G.nodes()
]

edge_widths = [
    1 + G[u][v]["weight"] * 3
    for u, v in G.edges()
]

fig, ax = plt.subplots(figsize=(16, 13))

nx.draw_networkx_edges(
    G,
    positions,
    ax=ax,
    width=edge_widths,
    edge_color="gray",
    alpha=0.35
)

nx.draw_networkx_nodes(
    G,
    positions,
    ax=ax,
    node_color=node_colors,
    node_size=700,
    edgecolors="black",
    linewidths=0.8
)

nx.draw_networkx_labels(
    G,
    positions,
    ax=ax,
    font_size=8,
    font_weight="bold"
)

legend_items = [
    Patch(
        facecolor=color_map[subject],
        edgecolor="black",
        label=subject
    )
    for subject in subjects
]

ax.legend(
    handles=legend_items,
    title="Preferred Subject Category",
    loc="upper left",
    bbox_to_anchor=(1.02, 1),
    fontsize=8
)

ax.set_title(
    "Weighted Student Profile Similarity Network\n"
    "(Similarity Score = 0.60)",
    fontsize=15,
    pad=20
)

ax.axis("off")
fig.tight_layout()

fig.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print("\n===== CLEAN NETWORK SUMMARY =====")
print("Students:", G.number_of_nodes())
print("Strong connections:", G.number_of_edges())
print("Threshold:", THRESHOLD)
print("Connected components:", nx.number_connected_components(G))
print("Network density:", round(nx.density(G), 3))
print("Isolated students:", list(nx.isolates(G)))
print("\nGraph saved:", OUTPUT_PATH)
