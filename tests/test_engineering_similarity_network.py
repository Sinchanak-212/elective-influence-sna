import unittest
from pathlib import Path

import pandas as pd

from src.build_engineering_similarity_network import (
    analyze_similarity_graph,
    build_similarity_graph,
    load_engineering_population,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"


class EngineeringSimilarityNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.respondents = load_engineering_population(DATA_PATH)

    def test_population_excludes_law_and_keeps_engineering_cohort(self) -> None:
        self.assertEqual(len(self.respondents), 24)
        self.assertFalse(self.respondents["branch"].str.casefold().eq("law").any())

    def test_raw_data_threshold_edge_counts(self) -> None:
        expected_edges = {0.30: 101, 0.50: 44, 0.60: 33}
        for threshold, expected in expected_edges.items():
            with self.subTest(threshold=threshold):
                graph = build_similarity_graph(self.respondents, threshold)
                self.assertEqual(graph.number_of_nodes(), 24)
                self.assertEqual(graph.number_of_edges(), expected)

    def test_primary_analysis_exports_required_metrics_and_components(self) -> None:
        graph = build_similarity_graph(self.respondents)
        tables = analyze_similarity_graph(graph)

        self.assertEqual(len(tables["nodes"]), 24)
        self.assertEqual(len(tables["edges"]), 44)
        self.assertEqual(len(tables["components"]), 24)
        self.assertTrue(
            {
                "degree_centrality",
                "betweenness_centrality",
                "closeness_centrality",
                "weighted_degree_strength",
                "is_isolated",
            }.issubset(tables["nodes"].columns)
        )
        summary = tables["summary"].iloc[0]
        self.assertEqual(summary["connected_component_count"], 6)
        self.assertEqual(summary["isolated_node_count"], 3)
        self.assertAlmostEqual(summary["density"], 44 / (24 * 23 / 2))
        self.assertEqual(
            int(tables["nodes"]["is_isolated"].sum()),
            summary["isolated_node_count"],
        )

    def test_outputs_are_dataframes(self) -> None:
        tables = analyze_similarity_graph(
            build_similarity_graph(self.respondents)
        )
        self.assertTrue(all(isinstance(table, pd.DataFrame) for table in tables.values()))


if __name__ == "__main__":
    unittest.main()
