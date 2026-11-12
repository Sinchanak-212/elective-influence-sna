import json
import unittest
from pathlib import Path

import networkx as nx
import pandas as pd

from src.analyze_engineering_similarity_communities import (
    METHODS,
    PRIMARY_THRESHOLD,
    THRESHOLDS,
    analyze_communities,
    detect_communities,
    summarize_attribute_mixing,
)
from src.build_engineering_similarity_network import (
    build_similarity_graph,
    load_engineering_population,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"


class EngineeringSimilarityCommunityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.respondents = load_engineering_population(DATA_PATH)
        cls.results = analyze_communities(cls.respondents)

    def test_population_and_threshold_edge_counts(self) -> None:
        expected = {0.30: 101, 0.50: 44, 0.60: 33}
        for threshold, edge_count in expected.items():
            with self.subTest(threshold=threshold):
                graph = build_similarity_graph(self.respondents, threshold)
                self.assertEqual(graph.number_of_nodes(), 24)
                self.assertEqual(graph.number_of_edges(), edge_count)
                self.assertEqual(
                    int(
                        self.results["threshold_sensitivity"]
                        .query("threshold == @threshold")
                        .iloc[0]["edge_count"]
                    ),
                    edge_count,
                )

    def test_assignments_cover_every_student_for_every_method_and_threshold(self) -> None:
        assignments = self.results["assignments"]
        respondent_ids = set(self.respondents["respondent_id"])
        self.assertEqual(len(assignments), len(THRESHOLDS) * len(METHODS) * 24)
        for threshold in THRESHOLDS:
            for method in METHODS:
                with self.subTest(threshold=threshold, method=method):
                    rows = assignments.query(
                        "threshold == @threshold and algorithm == @method"
                    )
                    self.assertEqual(set(rows["respondent_id"]), respondent_ids)
                    self.assertEqual(rows["respondent_id"].nunique(), 24)
                    self.assertFalse(rows["community_id"].isna().any())
                    self.assertTrue(rows["community_id"].str.match(r"^C\d{2}$").all())
                    observed_sizes = rows.groupby("community_id").size()
                    reported_sizes = rows.groupby("community_id")[
                        "community_size"
                    ].first()
                    self.assertEqual(
                        observed_sizes.to_dict(),
                        reported_sizes.to_dict(),
                    )

    def test_louvain_reproducibility_and_modularity(self) -> None:
        graph = build_similarity_graph(self.respondents, PRIMARY_THRESHOLD)
        first = detect_communities(graph, seed=42)
        second = detect_communities(graph, seed=42)
        for method in METHODS:
            self.assertEqual(
                {frozenset(group) for group in first[method]},
                {frozenset(group) for group in second[method]},
            )
            expected_modularity = nx.community.modularity(
                graph,
                first[method],
                weight="weight",
            )
            observed = self.results["threshold_sensitivity"].query(
                "threshold == @PRIMARY_THRESHOLD and algorithm == @method"
            )["weighted_modularity"].iloc[0]
            self.assertAlmostEqual(observed, expected_modularity)

    def test_algorithm_outputs_are_compared_without_assuming_superiority(self) -> None:
        primary = self.results["threshold_sensitivity"].query(
            "threshold == @PRIMARY_THRESHOLD"
        )
        self.assertEqual(set(primary["algorithm"]), set(METHODS))
        self.assertTrue(primary["community_count"].gt(0).all())
        self.assertTrue(primary["weighted_modularity"].between(-1, 1).all())

    def test_community_profiles_have_observed_counts(self) -> None:
        summary = self.results["community_summary"]
        self.assertTrue(summary["community_size"].gt(0).all())
        self.assertTrue(summary["dominant_subject_count"].le(summary["community_size"]).all())
        self.assertTrue(summary["dominant_branch_count"].le(summary["community_size"]).all())
        for counts, size in zip(
            summary["preferred_subject_category_counts"],
            summary["community_size"],
        ):
            self.assertEqual(sum(json.loads(counts).values()), size)

    def test_constant_attribute_assortativity_is_marked_undefined(self) -> None:
        graph = nx.Graph()
        graph.add_edge("A", "B", weight=0.8)
        graph.add_edge("B", "C", weight=0.7)
        nx.set_node_attributes(graph, "same", "attribute")
        nx.set_node_attributes(graph, "same", "preferred_subject_category")
        nx.set_node_attributes(graph, "same", "branch")
        nx.set_node_attributes(graph, "same", "primary_reason")

        results = summarize_attribute_mixing(graph, 0.5)
        self.assertEqual(len(results), 3)
        for row in results:
            self.assertFalse(row["assortativity_defined"])
            self.assertTrue(pd.isna(row["weighted_categorical_assortativity"]))
            self.assertEqual(
                row["assortativity_undefined_reason"],
                "fewer_than_two_edge_endpoint_categories",
            )

    def test_primary_threshold_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "primary threshold"):
            analyze_communities(self.respondents, thresholds=(0.30, 0.60))


if __name__ == "__main__":
    unittest.main()
