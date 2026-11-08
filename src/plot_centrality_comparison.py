import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data/processed/network_centrality_metrics.csv"
OUTPUT = ROOT / "outputs/graphs/centrality_comparison.png"

df = pd.read_csv(INPUT)

metrics = {
    "degree_centrality": "Degree Centrality",
    "betweenness_centrality": "Betweenness Centrality",
    "closeness_centrality": "Closeness Centrality",
    "weighted_degree": "Weighted Degree"
}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for ax, (column, title) in zip(axes.flatten(), metrics.items()):
    top = df.nlargest(5, column).sort_values(column)

    ax.barh(
        top["student"],
        top[column]
    )

    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Score")
    ax.grid(axis="x", alpha=0.25)

fig.suptitle(
    "Top 5 Students — Network Centrality Comparison",
    fontsize=16,
    fontweight="bold"
)

fig.tight_layout()
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)

print("Centrality comparison chart saved:", OUTPUT)
