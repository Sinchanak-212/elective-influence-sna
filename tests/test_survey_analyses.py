import unittest
from pathlib import Path

import pandas as pd

from src.analyze_elective_grades import (
    analyze_academic_outcomes,
    _ordinal_statistics,
)
from src.analyze_peer_discussion import analyze_peer_discussion
from src.survey_analysis_utils import (
    categorical_association,
    crosstab_rows,
    frequency_rows,
    load_engineering_survey,
    ordered_academic_outcome,
    ordered_final_score,
    ordered_study_hours,
    response_class,
    spearman_permutation,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"

PEER_COLUMNS = (
    "respondent_id",
    "discussed_elective_with_friends",
    "best_friend_same_elective",
    "best_friend_choice_reason",
    "best_friend_marks_range",
    "preferred_subject_category",
    "primary_reason",
    "academic_outcome",
    "final_score_range",
)
ACADEMIC_COLUMNS = (
    "respondent_id",
    "preferred_subject_category",
    "primary_reason",
    "academic_outcome",
    "course_difficulty",
    "final_score_range",
    "score_met_expectations",
    "study_hours_per_week",
)


class SurveyAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.respondents = load_engineering_survey(
            sorted(set(PEER_COLUMNS) | set(ACADEMIC_COLUMNS)),
            DATA_PATH,
        )
        cls.peer = analyze_peer_discussion(cls.respondents)
        cls.academic = analyze_academic_outcomes(cls.respondents)

    def test_engineering_filter_and_discussion_denominators(self) -> None:
        self.assertEqual(len(self.respondents), 24)
        self.assertFalse(
            self.respondents["branch"].str.strip().str.casefold().eq("law").any()
        )
        status = self.peer["summary"].query(
            "variable == 'discussed_elective_with_friends'"
        ).set_index("category")
        self.assertEqual(int(status.loc["Yes", "respondent_count"]), 19)
        self.assertEqual(int(status.loc["No", "respondent_count"]), 5)
        self.assertEqual(set(status["denominator"]), {24})
        self.assertAlmostEqual(status.loc["Yes", "percent_of_denominator"], 100 * 19 / 24)

    def test_best_friend_same_different_and_discussion_comparison(self) -> None:
        same = self.peer["summary"].query(
            "variable == 'best_friend_same_elective'"
        ).set_index("category")
        self.assertEqual(int(same.loc["Yes", "respondent_count"]), 14)
        self.assertEqual(int(same.loc["No", "respondent_count"]), 10)
        self.assertEqual(set(same["denominator"]), {24})

        result = self.peer["statistics"].set_index("analysis").loc[
            "discussion_status_by_best_friend_same_elective"
        ]
        self.assertEqual(result["test_used"], "Fisher exact (two-sided)")
        self.assertEqual(int(result["sample_size"]), 24)
        self.assertEqual(int(result["denominator"]), 24)
        self.assertAlmostEqual(result["test_statistic"], 8.666666666666666)
        self.assertAlmostEqual(result["p_value"], 0.12220026350461133)

        cross = self.peer["crosstabs"].query(
            "analysis == 'discussion_by_best_friend_same_elective'"
        )
        self.assertEqual(int(cross["respondent_count"].sum()), 24)
        self.assertEqual(set(cross["total_denominator"]), {24})

    def test_unknown_and_inapplicable_categories_are_not_negative_answers(self) -> None:
        self.assertEqual(response_class("best_friend_marks_range", "I don't know"), "unknown_or_withheld")
        self.assertEqual(response_class("academic_outcome", "Prefer not to say"), "unknown_or_withheld")
        self.assertEqual(response_class("course_difficulty", "Not completed yet"), "inapplicable")
        self.assertEqual(response_class("final_score_range", "Result not declared"), "inapplicable")
        self.assertEqual(response_class("discussed_elective_with_friends", pd.NA), "missing")

        summary = self.peer["summary"]
        marks = summary[
            (summary["variable"] == "best_friend_marks_range")
            & (summary["category"] == "I don't know")
        ].iloc[0]
        self.assertEqual(marks["response_class"], "unknown_or_withheld")
        self.assertEqual(int(marks["respondent_count"]), 4)
        difficulty = self.academic["summary"]
        not_completed = difficulty[
            (difficulty["variable"] == "course_difficulty")
            & (difficulty["category"] == "Not completed yet")
        ].iloc[0]
        self.assertEqual(not_completed["response_class"], "inapplicable")

    def test_missing_values_are_preserved_with_explicit_denominators(self) -> None:
        sample = pd.DataFrame(
            {
                "status": ["Yes", "No", None],
                "category": ["A", None, "B"],
            }
        )
        frequencies = frequency_rows(sample, ["status"], "test")
        missing_frequency = next(row for row in frequencies if row["category"] == "Missing response")
        self.assertEqual(missing_frequency["response_class"], "missing")
        self.assertEqual(missing_frequency["denominator"], 3)
        cross = crosstab_rows(sample, "status", "category", "missing_test")
        self.assertEqual(sum(row["respondent_count"] for row in cross), 3)
        self.assertTrue(any(row["row_category"] == "Missing response" for row in cross))
        self.assertTrue(any(row["column_category"] == "Missing response" for row in cross))

    def test_reason_comparison_is_reported_descriptively_when_sparse(self) -> None:
        result = self.peer["statistics"].set_index("analysis").loc[
            "student_reason_by_best_friend_choice_reason"
        ]
        self.assertEqual(result["test_used"], "not_performed")
        self.assertIn("expected cell count is below 5", result["test_selection_reason"])
        self.assertEqual(int(result["sample_size"]), 24)

    def test_statistical_test_selection_and_effect_sizes(self) -> None:
        fisher = categorical_association(
            [[1, 9], [11, 3]],
            "small_2x2",
        )
        self.assertEqual(fisher["test_used"], "Fisher exact (two-sided)")
        self.assertAlmostEqual(fisher["p_value"], 0.0027594561852200836)
        self.assertAlmostEqual(fisher["effect_size"], 0.6761234037828132)

        sparse = categorical_association(
            [[4, 0], [0, 4], [1, 1]],
            "sparse_table",
        )
        self.assertEqual(sparse["test_used"], "not_performed")
        self.assertTrue(pd.isna(sparse["p_value"]))

        eligible = categorical_association(
            [[10, 10], [10, 10], [10, 10]],
            "adequate_expected_counts",
        )
        self.assertEqual(eligible["test_used"], "Pearson chi-square")
        self.assertAlmostEqual(eligible["test_statistic"], 0.0)
        self.assertAlmostEqual(eligible["p_value"], 1.0)

    def test_academic_cross_tabs_keep_cohort_denominators(self) -> None:
        self.assertEqual(len(self.academic["summary"]), 41)
        self.assertIn(
            "preferred_subject_by_academic_outcome",
            set(self.academic["crosstabs"]["analysis"]),
        )
        for analysis in (
            "preferred_subject_by_academic_outcome",
            "primary_reason_by_academic_outcome",
            "course_difficulty_by_academic_outcome",
            "final_score_by_expectations_met",
            "study_hours_by_academic_outcome",
        ):
            table = self.academic["crosstabs"].query("analysis == @analysis")
            self.assertEqual(int(table["respondent_count"].sum()), 24)
            self.assertEqual(set(table["total_denominator"]), {24})

        stats = self.academic["statistics"]
        categorical = stats[stats["analysis"].isin(
            [
                "preferred_subject_by_academic_outcome",
                "primary_reason_by_academic_outcome",
                "course_difficulty_by_academic_outcome",
                "final_score_by_expectations_met",
                "study_hours_by_academic_outcome",
            ]
        )]
        self.assertTrue(categorical["test_used"].eq("not_performed").all())
        self.assertTrue(categorical["p_value"].isna().all())

    def test_ordinal_mappings_and_spearman_are_reproducible(self) -> None:
        self.assertEqual(ordered_study_hours("Less than 2 hours"), 1)
        self.assertIsNone(ordered_study_hours("Irregular preparation"))
        self.assertEqual(ordered_academic_outcome("S — Outstanding"), 5)
        self.assertIsNone(ordered_academic_outcome("Prefer not to say"))
        self.assertEqual(ordered_final_score("80–89"), 6)
        self.assertIsNone(ordered_final_score("Result not declared"))

        first = spearman_permutation(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            "reproducible",
            permutations=999,
        )
        second = spearman_permutation(
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            "reproducible",
            permutations=999,
        )
        self.assertEqual(first["test_statistic"], 1.0)
        self.assertEqual(first["p_value"], second["p_value"])

        undefined = spearman_permutation(
            [1, 1, 1],
            [1, 2, 3],
            "no_variation",
        )
        self.assertEqual(undefined["test_used"], "not_performed")
        self.assertTrue(pd.isna(undefined["p_value"]))

        ordinal = _ordinal_statistics(self.respondents)
        study = next(row for row in ordinal if row["analysis"].startswith("study_hours"))
        score = next(row for row in ordinal if row["analysis"].startswith("final_score"))
        self.assertEqual((study["sample_size"], study["denominator"]), (18, 24))
        self.assertEqual((score["sample_size"], score["denominator"]), (20, 24))

    def test_new_scripts_do_not_target_approved_network_artifacts(self) -> None:
        from src import analyze_elective_grades, analyze_peer_discussion

        protected_names = {
            "engineering_similarity_nodes.csv",
            "engineering_similarity_edges.csv",
            "engineering_similarity_components.csv",
            "engineering_network_summary.csv",
            "engineering_community_assignments.csv",
            "engineering_community_summary.csv",
            "engineering_attribute_mixing.csv",
            "engineering_threshold_sensitivity.csv",
            "engineering_community_comparison.png",
            "peer_discussion_summary.csv",
            "peer_discussion_summary.png",
            "subject_grade_distribution.csv",
            "subject_grade_network.png",
        }
        output_paths = {
            analyze_elective_grades.SUMMARY_PATH,
            analyze_elective_grades.CROSSTAB_PATH,
            analyze_elective_grades.STATISTICS_PATH,
            analyze_elective_grades.FIGURE_PATH,
            analyze_peer_discussion.SUMMARY_PATH,
            analyze_peer_discussion.CROSSTAB_PATH,
            analyze_peer_discussion.STATISTICS_PATH,
            analyze_peer_discussion.FIGURE_PATH,
        }
        self.assertTrue(protected_names.isdisjoint({path.name for path in output_paths}))
        self.assertTrue(all(path.parent.name in {"reports", "graphs"} for path in output_paths))


if __name__ == "__main__":
    unittest.main()
