# An Exploratory Social Network Analysis of Elective Preferences and Self-Reported Peer Discussion among Engineering Students

## Population and analysis status

- The raw survey has 25 responses; the primary engineering analyses include 24
  respondents and exclude the one Law respondent. The original survey remains
  unchanged.
- The project combines respondent-level self-reports with a constructed
  profile-similarity graph. The graph is not an observed friendship or
  discussion network.
- The 0.50 similarity threshold is primary; 0.30 and 0.60 are sensitivity
  checks. The score weights are analytical assumptions, not a validated scale.
- Priority 1 and 2 network outputs are retained separately from the
  engineering-only peer-discussion and academic summaries.

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
- State that the primary analysis uses the 24 engineering respondents and
  threshold 0.50; thresholds 0.30 and 0.60 are sensitivity checks. The Law
  respondent is excluded from the engineering network.
- Describe the weights and 0.50 primary threshold as analytical assumptions,
  not as a validated scientific scale.
- Define degree, betweenness, closeness, and weighted degree as graph
  statistics, not direct measures of influence.
- Describe fixed-seed weighted Louvain and weighted greedy modularity
  partitions, their community counts/sizes, and weighted modularity. Treat
  modularity as a graph-partition score, not validation or evidence that
  communities are real social groups.
- Report same-attribute mixing and weighted categorical assortativity for
  preferred subject category, branch, and primary reason. Explain that these
  attributes also help construct similarity edges, so observed mixing is not
  independent evidence of social homophily.
- State the exact Priority 2 assortativity calculation. For an attribute with
  categories \(i,j\), let \(w_{uv}\) be the similarity score on an undirected
  edge \(\{u,v\}\), and \(W=\sum_{\{u,v\}}w_{uv}\). The mixing matrix is
  \(e_{ij}=\sum_{\{u,v\}}w_{uv}
  [I(x_u=i,x_v=j)+I(x_u=j,x_v=i)]/(2W)\): each edge is weighted by its
  similarity score and contributes both orientations. With row and column
  marginals \(a_i=\sum_j e_{ij}\), \(b_i=\sum_j e_{ji}\), the coefficient is
  \(r=(\operatorname{tr}(e)-\sum_i a_i b_i)/(1-\sum_i a_i b_i)\). It is
  undefined when the denominator is zero or no usable edge-category variation
  exists. This statistic is a graph description, not evidence of social ties.
- Describe peer discussion as respondent-level self-report; no partner
  identities or observed discussion links are available.
- For peer comparisons, report counts, percentages, and their denominators.
  Keep “I don't know,” “Prefer not to say,” and unavailable/not-completed
  responses distinct from negative responses.
- Use a two-sided Fisher exact test for the discussion-status by
  best-friend-same-elective 2x2 table. Report a chi-square test only if all
  expected cell counts meet the stated minimum of 5; do not test sparse
  multi-category tables mechanically. Any Cramer's V accompanying an
  untested sparse table is descriptive and unstable, not inferential evidence.
- For ordinal summaries, label the order assumptions and exclusions. Study
  hours treat the listed numeric brackets as ordered and exclude “Irregular
  preparation”; final-score ranks include declared score brackets only.
  Academic outcome ranks follow D, C, B, A, S; withheld outcomes are excluded.
  Report the fixed-seed permutation Spearman procedure and small sample.

## 3. Survey findings

- Report preferred-subject-category and academic-outcome counts.
- Cross-tabulate primary reason, course difficulty, study-hours response,
  preferred subject, and academic outcome. Compare final-score response with
  whether expectations were met.
- Keep “Not completed yet,” “Result not declared,” and “Did not appear for the
  examination” as explicit categories in descriptive tables; do not assign
  them an academic score or outcome rank.
- Report ordinal Spearman estimates only for pairwise-complete records with
  valid ordered categories. These are exploratory associations, not
  predictive or causal results.
- Summarize reported discussion frequency and the cross-tabulation with
  whether the respondent's best friend selected the same elective.
- Summarize best-friend choice reasons among those who reported discussion.
- Compare discussion status descriptively across preferred subject, student
  decision reason, academic outcome, final score response, and best-friend
  choice/marks responses. Report row and column denominators.
- Cross-tabulate the student's primary reason with the best friend's reported
  reason; treat the sparse table as descriptive unless assumptions support a
  test.
- Include denominators for percentages and avoid interpreting associations as
  causal.

## 4. Network findings

- Report node/edge counts, density, components, and isolates for each
  explicitly stated network definition and threshold.
- Present centrality rankings with a clear reminder that nodes are anonymous
  survey respondents and edges are profile similarities.
- Present community counts, sizes, and weighted modularity for each method and
  threshold; keep 0.50 as the primary engineering-only network.
- Compare partitions across methods/thresholds cautiously; with 24
  engineering respondents, community structure may be sensitive to modeling
  choices and small-sample instability.
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
- Note that profile similarity and attribute assortativity do not establish
  friendship, observed peer interaction, or influence. At higher similarity
  thresholds, matching on attributes used in the score is partly imposed by
  construction.
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
7. Engineering-only peer-discussion summary, crosstabs, and exact-test output.
8. Engineering-only academic crosstabs, statistical selection summary, and
   descriptive figure.

## Concise findings from the current engineering cohort

- **Profile similarity network:** 24 engineering respondents and 44 edges at
  the primary threshold 0.50 (density 0.159). Threshold checks yield 101 edges
  at 0.30 and 33 at 0.60.
- **Community structure:** At 0.50, both fixed-seed Louvain and greedy
  modularity returned 7 communities of sizes 8, 6, 4, 3, 1, 1, 1; weighted
  modularity was 0.617 for both. Higher thresholds split more nodes into
  communities. These partitions summarize this modeled graph only.
- **Self-reported peer discussion:** 19/24 (79.2%) reported discussion.
  14/24 (58.3%) said their best friend chose the same elective. That response
  was 13/19 among discussants and 1/5 among non-discussants; the two-sided
  Fisher test gave odds ratio 8.67 and p=0.122 (Cramer's V=0.399). The small
  non-discussion group and cross-sectional self-report limit interpretation.
- **Academic patterns:** The most frequent reported outcome was C — Good
  (8/24), followed by B — Very Good (6/24). Ordered final-score and outcome
  categories had Spearman rho=0.853 (n=20/24; 9,999-permutation p estimate
  0.0001, the minimum add-one estimate at that resolution); this compares
  overlapping self-reported academic measures and is not evidence of
  prediction or causation. Ordered study-hours and outcome
  ranks had rho=0.245 (n=18/24; p=0.322). Sparse categorical cross-tabs did
  not meet the expected-count criterion for chi-square testing.
- **Limitations:** This is a small convenience sample with categorical,
  self-reported measures and no partner identities. Chosen similarity
  weights, thresholding, and community algorithms affect the network results.
  Neither its edges, communities, mixing statistics, nor survey associations
  establish friendship, influence, or causal effects.
