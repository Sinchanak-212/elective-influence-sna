
import pandas as pd
import networkx as nx
from itertools import combinations

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/survey_responses_anonymized.csv"

df = pd.read_csv(DATA_PATH)

# Exclude non-engineering responses from primary analysis
df = df[
    df["branch"].str.strip().str.casefold() != "law"
].copy()

weights = {
    "preferred_subject_category": 0.50,
    "branch": 0.20,
    "primary_reason": 0.20,
    "year": 0.10
}

print("ENGINEERING-ONLY POPULATION:", len(df))

for threshold in [0.30, 0.50, 0.60]:

    G = nx.Graph()
    G.add_nodes_from(df["respondent_id"])

    for (_, a), (_, b) in combinations(df.iterrows(), 2):

        score = sum(
            weight
            for attribute, weight in weights.items()
            if a[attribute] == b[attribute]
        )

        if score >= threshold:
            G.add_edge(
                a["respondent_id"],
                b["respondent_id"],
                weight=round(score, 2)
            )

    components = list(nx.connected_components(G))

    print(f"\n===== THRESHOLD {threshold} =====")
    print("Students:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Density:", round(nx.density(G), 3))
    print("Components:", len(components))
    print("Largest component:", max(map(len, components)))
    print("Isolated students:", list(nx.isolates(G)))
