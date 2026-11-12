# An Exploratory Social Network Analysis of Elective Preferences and Self-Reported Peer Discussion among Engineering Students

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
.\venv\Scripts\python.exe src\build_engineering_similarity_network.py
.\venv\Scripts\python.exe src\analyze_engineering_similarity_communities.py
.\venv\Scripts\python.exe src\analyze_peer_discussion.py
.\venv\Scripts\python.exe src\analyze_elective_grades.py
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

The engineering network and community scripts use the shared weighted
similarity assumptions (subject 0.50, branch 0.20, primary reason 0.20, year
0.10), with the 24 engineering respondents and threshold 0.50 as primary.
Thresholds 0.30 and 0.60 are sensitivity checks. Peer and academic scripts
also use this same validated engineering cohort, and write distinct
`engineering_*` outputs under `outputs/reports/` and `outputs/graphs/`.
Statistical methods use the Python standard library; no SciPy dependency is
required.

## Analyses

- Validation checks respondent counts, IDs, missing values, and category
  distributions.
- Academic analysis reports descriptive cross-tabs for preferred subject,
  primary reason, course difficulty, study-hours response, score range, and
  self-reported outcomes. Sparse categorical tables are not assigned
  chi-square p-values; ordinal Spearman estimates are exploratory.
- The exact-match network links respondents who selected the same preferred
  subject category.
- The weighted profile-similarity network scores shared preferred subject
  category, branch, primary reason, and year using the weights in
  `src/build_weighted_similarity.py`.
- Centrality measures describe positions in the chosen, thresholded
  similarity graph; they do not measure real-world popularity or influence.
- Peer-discussion analysis compares respondents' self-reported discussion
  status, best-friend answers, and academic responses; it does not infer who
  spoke with whom. “I don't know,” withheld, missing, and not-applicable
  responses are retained separately.
- Community detection compares weighted Louvain and greedy modularity
  partitions at similarity thresholds 0.30, 0.50 and 0.60. These are groups
  in an inferred profile-similarity graph, not observed social groups.

## Interpretation and privacy

The survey records whether respondents discussed the elective with friends and
whether their best friend chose the same elective, but it does not identify
discussion partners or provide named network nominations. Therefore, the
project cannot construct an observed friendship/discussion network from these
responses. Similarity edges are computed from shared profile attributes and
must not be described as friendship ties, peer influence, or causal effects.
All conclusions should remain descriptive, acknowledge the small sample, and
preserve respondent anonymity.

The Priority 2 weighted categorical assortativity uses each undirected
similarity edge's score as its weight. Each edge contributes both endpoint
orientations to the mixing matrix, normalized by twice the sum of edge weights;
the coefficient is `(trace(e) - sum(a_i * b_i)) / (1 - sum(a_i * b_i))`.
Because subject, branch, and primary reason also contribute to the graph's
construction, this is a description of a model-implied graph, not independent
evidence of social homophily.
