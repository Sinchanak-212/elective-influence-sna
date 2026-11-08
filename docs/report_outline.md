# Report outline

## 1. Title and research questions

- State the elective-choice and student-network questions.
- Explain that the project uses an anonymized survey of 25 respondents.
- Define the distinction between self-reported peer discussion and inferred
  profile similarity.

## 2. Data and methods

- Describe the survey fields and validation checks.
- Summarize the preferred-subject-category versus academic-outcome
  cross-tabulation.
- Explain the exact-match network: an edge indicates a shared preferred
  subject category.
- Explain the weighted similarity score and its component weights:
  preferred subject category (0.50), branch (0.20), primary reason (0.20),
  and year (0.10).
- State the edge thresholds used: 0.30 for the stored weighted graph and
  0.60 for the centrality comparison and threshold sensitivity analysis.
- Define degree, betweenness, closeness, and weighted degree as graph
  statistics, not direct measures of influence.
- Describe the weighted Louvain method, greedy modularity benchmark, and
  modularity as a partition score.
- Describe peer discussion as respondent-level self-report; no partner
  identities or observed discussion links are available.

## 3. Survey findings

- Report preferred-subject-category and academic-outcome counts.
- Summarize reported discussion frequency and the cross-tabulation with
  whether the respondent's best friend selected the same elective.
- Summarize best-friend choice reasons among those who reported discussion.
- Include denominators for percentages and avoid interpreting associations as
  causal.

## 4. Network findings

- Report node/edge counts, density, components, and isolates for each
  explicitly stated network definition and threshold.
- Present centrality rankings with a clear reminder that nodes are anonymous
  survey respondents and edges are profile similarities.
- Present community counts, sizes, and weighted modularity for each method and
  threshold.
- Compare partitions across methods/thresholds cautiously; with 25
  respondents, community structure may be sensitive to modeling choices.
- Include the similarity-network and community figures, labeling them as
  inferred networks.

## 5. Discussion and limitations

- Separate directly reported survey findings from patterns inferred from
  shared attributes.
- Do not claim friendship, actual interaction partners, peer influence, or
  causal effects from the similarity networks.
- Discuss the small sample, self-report, categorical measurement, chosen
  attribute weights, threshold choice, and potential community-detection
  instability.
- Note that named/consented alter nominations or another direct interaction
  measure would be required to study observed social ties.

## 6. Conclusion

- Summarize descriptive findings only.
- Identify further data collection and robustness checks as future work.

## Suggested tables and figures

1. Respondent and survey-response summary.
2. Preferred subject category by academic outcome.
3. Peer-discussion status and best-friend response cross-tabulations.
4. Centrality comparison at the stated threshold.
5. Community-method and threshold summary, including community sizes and
   weighted modularity.
6. Weighted profile-similarity graph and Louvain community visualization.
