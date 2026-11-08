# Elective Influence and Student Profile Similarity SNA

This project analyzes an anonymized survey of 25 students about elective choice,
study experience, academic outcomes, and peer discussion. It combines
descriptive survey analysis with networks inferred from shared survey-profile
attributes.

## Project structure

- `data/raw/survey_responses_anonymized.csv` — source survey; do not edit or
  publish respondent-level data.
- `data/processed/` — intermediate tables and network edges.
- `src/` — data validation, analysis, network construction, and visualization
  scripts.
- `outputs/graphs/` — generated figures.
- `outputs/reports/` — generated aggregate tables.
- `docs/report_outline.md` — suggested structure for a written report.

## Run the analyses

Run commands from the project root using the existing virtual environment.
The source dataset is read-only for these scripts.

```powershell
.\venv\Scripts\python.exe src\validate_data.py
.\venv\Scripts\python.exe src\analyze_elective_grades.py
.\venv\Scripts\python.exe src\build_similarity_network.py
.\venv\Scripts\python.exe src\build_weighted_similarity.py
.\venv\Scripts\python.exe src\build_clean_similarity_network.py
.\venv\Scripts\python.exe src\analyze_network_metrics.py
.\venv\Scripts\python.exe src\plot_centrality_comparison.py
.\venv\Scripts\python.exe src\analyze_peer_discussion.py
.\venv\Scripts\python.exe src\detect_similarity_communities.py
```

The centrality and community scripts use the weighted edge file created by
`build_weighted_similarity.py`. Outputs are written to `data/processed/`,
`outputs/graphs/`, and `outputs/reports/`.

## Analyses

- Validation checks respondent counts, IDs, missing values, and category
  distributions.
- Subject-category/outcome analysis cross-tabulates preferred elective area
  and self-reported academic outcome.
- The exact-match network links respondents who selected the same preferred
  subject category.
- The weighted profile-similarity network scores shared preferred subject
  category, branch, primary reason, and year using the weights in
  `src/build_weighted_similarity.py`.
- Centrality measures describe positions in the chosen, thresholded
  similarity graph; they do not measure real-world popularity or influence.
- Peer-discussion analysis summarizes respondents' actual answers and does not
  infer who spoke with whom.
- Community detection compares weighted Louvain and greedy modularity
  partitions at similarity thresholds 0.30 and 0.60. These are groups in an
  inferred profile-similarity graph, not observed social groups.

## Interpretation and privacy

The survey records whether respondents discussed the elective with friends and
whether their best friend chose the same elective, but it does not identify
discussion partners or provide named network nominations. Therefore, the
project cannot construct an observed friendship/discussion network from these
responses. Similarity edges are computed from shared profile attributes and
must not be described as friendship ties, peer influence, or causal effects.
All conclusions should remain descriptive, acknowledge the small sample, and
preserve respondent anonymity.
