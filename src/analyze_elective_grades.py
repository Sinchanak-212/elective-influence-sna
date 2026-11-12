"""Explore engineering survey academic outcomes without causal claims."""

from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.survey_analysis_utils import (
    categorical_association,
    crosstab_matrix,
    crosstab_rows,
    frequency_rows,
    load_engineering_survey,
    ordered_academic_outcome,
    ordered_final_score,
    ordered_study_hours,
    spearman_permutation,
)


REPORT_DIR = ROOT / "outputs" / "reports"
GRAPH_DIR = ROOT / "outputs" / "graphs"
SUMMARY_PATH = REPORT_DIR / "engineering_academic_summary.csv"
CROSSTAB_PATH = REPORT_DIR / "engineering_academic_crosstabs.csv"
STATISTICS_PATH = REPORT_DIR / "engineering_academic_statistics.csv"
FIGURE_PATH = GRAPH_DIR / "engineering_academic_analysis.png"

REQUIRED_COLUMNS = (
    "respondent_id",
    "preferred_subject_category",
    "primary_reason",
    "academic_outcome",
    "course_difficulty",
    "final_score_range",
    "score_met_expectations",
    "study_hours_per_week",
)
CROSS_TABULATIONS = (
    (
        "preferred_subject_category",
        "academic_outcome",
        "preferred_subject_by_academic_outcome",
    ),
    (
        "primary_reason",
        "academic_outcome",
        "primary_reason_by_academic_outcome",
    ),
    (
        "course_difficulty",
        "academic_outcome",
        "course_difficulty_by_academic_outcome",
    ),
    (
        "final_score_range",
        "score_met_expectations",
        "final_score_by_expectations_met",
    ),
    (
        "study_hours_per_week",
        "academic_outcome",
        "study_hours_by_academic_outcome",
    ),
)
FREQUENCY_COLUMNS = (
    "preferred_subject_category",
    "primary_reason",
    "academic_outcome",
    "course_difficulty",
    "final_score_range",
    "score_met_expectations",
    "study_hours_per_week",
)


def _ordinal_statistics(respondents: pd.DataFrame) -> list[dict[str, object]]:
    outcomes = respondents["academic_outcome"].map(ordered_academic_outcome)
    test_specs = (
        (
            "study_hours_per_week",
            respondents["study_hours_per_week"].map(ordered_study_hours),
            "study_hours_by_ordered_academic_outcome",
        ),
        (
            "final_score_range",
            respondents["final_score_range"].map(ordered_final_score),
            "final_score_by_ordered_academic_outcome",
        ),
    )
    results = []
    for _, values, analysis in test_specs:
        paired = [
            (int(first), int(second))
            for first, second in zip(values, outcomes)
            if pd.notna(first) and pd.notna(second)
        ]
        result = spearman_permutation(
            [first for first, _ in paired],
            [second for _, second in paired],
            analysis,
            seed=42,
            permutations=9999,
            denominator=len(respondents),
        )
        result["excluded_count"] = len(respondents) - len(paired)
        results.append(result)
    return results


def analyze_academic_outcomes(
    respondents: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Create frequency, cross-tabulation and appropriately selected tests."""
    summaries = frequency_rows(
        respondents,
        FREQUENCY_COLUMNS,
        "academic",
    )
    cross_tab_rows = [
        row
        for row_variable, column_variable, analysis in CROSS_TABULATIONS
        for row in crosstab_rows(
            respondents,
            row_variable,
            column_variable,
            analysis,
        )
    ]

    statistical_rows = []
    for row_variable, column_variable, analysis in CROSS_TABULATIONS:
        _, _, table = crosstab_matrix(respondents, row_variable, column_variable)
        statistical_rows.append(
            categorical_association(
                table,
                analysis,
                denominator=len(respondents),
            )
        )
    statistical_rows.extend(_ordinal_statistics(respondents))

    return {
        "summary": pd.DataFrame(summaries),
        "crosstabs": pd.DataFrame(cross_tab_rows),
        "statistics": pd.DataFrame(statistical_rows),
    }


def _outcome_order(label: object) -> tuple[int, str]:
    prefix = str(label)[:1].upper()
    order = {"D": 0, "C": 1, "B": 2, "A": 3, "S": 4}
    if prefix in order:
        return order[prefix], str(label)
    return 99, str(label)


def _draw_stacked_crosstab(
    axis: plt.Axes,
    respondents: pd.DataFrame,
    row_variable: str,
    column_variable: str,
    title: str,
) -> None:
    rows, columns, matrix = crosstab_matrix(
        respondents,
        row_variable,
        column_variable,
    )
    table = pd.DataFrame(matrix, index=rows, columns=columns)
    if column_variable == "academic_outcome":
        table = table.reindex(
            columns=sorted(table.columns, key=_outcome_order),
            fill_value=0,
        )
    table = table.loc[table.sum(axis=1).sort_values(ascending=True).index]
    table.index = [textwrap.fill(str(label), 24) for label in table.index]
    table.plot(
        kind="barh",
        stacked=True,
        ax=axis,
        colormap="tab10",
        width=0.76,
    )
    axis.set_title(f"{title} (n={len(respondents)})", loc="left", fontsize=10)
    axis.set_xlabel("Respondents")
    axis.set_ylabel("")
    axis.legend(
        title=column_variable.replace("_", " "),
        fontsize=7,
        title_fontsize=7,
        loc="lower right",
    )
    axis.grid(axis="x", alpha=0.2)


def create_academic_figure(
    respondents: pd.DataFrame,
    output_path: Path = FIGURE_PATH,
) -> None:
    """Plot observed counts for academic outcomes and related survey variables."""
    fig, axes = plt.subplots(3, 2, figsize=(16, 17))
    _draw_stacked_crosstab(
        axes[0, 0],
        respondents,
        "preferred_subject_category",
        "academic_outcome",
        "Preferred subject by academic outcome",
    )
    _draw_stacked_crosstab(
        axes[0, 1],
        respondents,
        "primary_reason",
        "academic_outcome",
        "Primary decision reason by academic outcome",
    )
    _draw_stacked_crosstab(
        axes[1, 0],
        respondents,
        "course_difficulty",
        "academic_outcome",
        "Course difficulty response by academic outcome",
    )
    _draw_stacked_crosstab(
        axes[1, 1],
        respondents,
        "study_hours_per_week",
        "academic_outcome",
        "Study-hours response by academic outcome",
    )
    _draw_stacked_crosstab(
        axes[2, 0],
        respondents,
        "final_score_range",
        "score_met_expectations",
        "Final score response by expectations response",
    )

    outcome_counts = (
        respondents["academic_outcome"]
        .fillna("Missing response")
        .value_counts()
        .reindex(
            sorted(
                respondents["academic_outcome"].fillna("Missing response").unique(),
                key=_outcome_order,
            ),
            fill_value=0,
        )
    )
    outcome_counts.index = [
        textwrap.fill(str(label), 24) for label in outcome_counts.index
    ]
    outcome_counts.sort_values(ascending=True).plot(
        kind="barh",
        ax=axes[2, 1],
        color="#3B82A0",
    )
    axes[2, 1].set_title(
        f"Self-reported academic outcome distribution (n={len(respondents)})",
        loc="left",
        fontsize=10,
    )
    axes[2, 1].set_xlabel("Respondents")
    axes[2, 1].set_ylabel("")
    axes[2, 1].grid(axis="x", alpha=0.2)

    fig.suptitle(
        "Exploratory academic patterns among engineering respondents",
        fontsize=15,
        fontweight="bold",
        y=0.995,
    )
    fig.text(
        0.5,
        0.006,
        "Counts are descriptive. Unreported, unknown, and not-applicable categories "
        "are retained; cross-sectional associations are not causal.",
        ha="center",
        fontsize=9,
        color="#475467",
    )
    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.98))
    fig.savefig(output_path, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    respondents = load_engineering_survey(REQUIRED_COLUMNS)
    results = analyze_academic_outcomes(respondents)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    results["summary"].to_csv(SUMMARY_PATH, index=False)
    results["crosstabs"].to_csv(CROSSTAB_PATH, index=False)
    results["statistics"].to_csv(STATISTICS_PATH, index=False)
    create_academic_figure(respondents)

    print(f"Engineering respondents: {len(respondents)}")
    print("Academic outcomes:")
    print(respondents["academic_outcome"].value_counts().to_string())
    print("Summary:", SUMMARY_PATH)
    print("Cross-tabs:", CROSSTAB_PATH)
    print("Statistics:", STATISTICS_PATH)
    print("Figure:", FIGURE_PATH)
    print("\nStatistical analysis selection:")
    print(
        results["statistics"][
            [
                "analysis",
                "sample_size",
                "denominator",
                "test_used",
                "test_statistic",
                "p_value",
                "effect_size",
                "test_selection_reason",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
