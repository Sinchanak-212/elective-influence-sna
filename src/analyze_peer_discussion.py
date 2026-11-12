"""Summarize engineering students' self-reported elective discussions."""

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
    crosstab_rows,
    frequency_rows,
    load_engineering_survey,
)


REPORT_DIR = ROOT / "outputs" / "reports"
GRAPH_DIR = ROOT / "outputs" / "graphs"
SUMMARY_PATH = REPORT_DIR / "engineering_peer_discussion_summary.csv"
CROSSTAB_PATH = REPORT_DIR / "engineering_peer_discussion_crosstabs.csv"
STATISTICS_PATH = REPORT_DIR / "engineering_peer_discussion_statistics.csv"
FIGURE_PATH = GRAPH_DIR / "engineering_peer_discussion_analysis.png"

REQUIRED_COLUMNS = (
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
DISCUSSION = "discussed_elective_with_friends"
FRIEND_SAME = "best_friend_same_elective"
CROSS_TABULATIONS = (
    (DISCUSSION, "preferred_subject_category", "discussion_by_preferred_subject"),
    (DISCUSSION, "primary_reason", "discussion_by_primary_reason"),
    (DISCUSSION, "academic_outcome", "discussion_by_academic_outcome"),
    (DISCUSSION, "final_score_range", "discussion_by_final_score_range"),
    (DISCUSSION, FRIEND_SAME, "discussion_by_best_friend_same_elective"),
    (DISCUSSION, "best_friend_choice_reason", "discussion_by_best_friend_reason"),
    (DISCUSSION, "best_friend_marks_range", "discussion_by_best_friend_marks"),
    ("primary_reason", "best_friend_choice_reason", "student_reason_by_friend_reason"),
)


def analyze_peer_discussion(
    respondents: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Create frequency, cross-tabulation and cautious test outputs."""
    for column in (DISCUSSION, FRIEND_SAME):
        observed = set(respondents[column].dropna().astype(str).str.strip())
        invalid = sorted(observed - {"Yes", "No"})
        if invalid:
            raise ValueError(f"Unexpected responses in {column}: {invalid}")

    distributions = frequency_rows(
        respondents,
        (
            DISCUSSION,
            FRIEND_SAME,
            "best_friend_choice_reason",
            "best_friend_marks_range",
        ),
        "peer_discussion",
    )
    cross_tabs = [
        row
        for first, second, name in CROSS_TABULATIONS
        for row in crosstab_rows(respondents, first, second, name)
    ]

    friend_table = pd.crosstab(
        respondents[DISCUSSION].fillna("Missing response"),
        respondents[FRIEND_SAME].fillna("Missing response"),
        dropna=False,
    ).reindex(
        index=["Yes", "No"],
        columns=["Yes", "No"],
        fill_value=0,
    )
    discussion_test = categorical_association(
        friend_table.to_numpy(dtype=int).tolist(),
        "discussion_status_by_best_friend_same_elective",
        denominator=len(respondents),
    )

    reason_table = pd.crosstab(
        respondents["primary_reason"].fillna("Missing response"),
        respondents["best_friend_choice_reason"].fillna("Missing response"),
        dropna=False,
    )
    reason_test = categorical_association(
        reason_table.to_numpy(dtype=int).tolist(),
        "student_reason_by_best_friend_choice_reason",
        denominator=len(respondents),
    )
    statistics = pd.DataFrame([discussion_test, reason_test])

    return {
        "summary": pd.DataFrame(distributions),
        "crosstabs": pd.DataFrame(cross_tabs),
        "statistics": statistics,
    }


def _draw_stacked_counts(
    axis: plt.Axes,
    frame: pd.DataFrame,
    category: str,
    title: str,
) -> None:
    table = pd.crosstab(
        frame[category].fillna("Missing response"),
        frame[DISCUSSION].fillna("Missing response"),
        dropna=False,
    )
    discussion_columns = ["Yes", "No"] + [
        column for column in table.columns if column not in {"Yes", "No"}
    ]
    table = table.reindex(columns=discussion_columns, fill_value=0)
    table = table.loc[table.sum(axis=1).sort_values(ascending=True).index]
    table.index = [textwrap.fill(str(label), 25) for label in table.index]
    table.plot(
        kind="barh",
        stacked=True,
        ax=axis,
        color={"Yes": "#3B82A0", "No": "#F2A65A"},
        width=0.76,
    )
    axis.set_title(f"{title} (n={len(frame)})", loc="left", fontsize=10)
    axis.set_xlabel("Respondents")
    axis.set_ylabel("")
    axis.legend(title="Discussed", fontsize=8, title_fontsize=8)
    axis.grid(axis="x", alpha=0.2)


def create_peer_figure(frame: pd.DataFrame, output_path: Path = FIGURE_PATH) -> None:
    """Create a count-based overview with group sizes shown in panel titles."""
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    status_counts = frame[DISCUSSION].value_counts().reindex(["Yes", "No"], fill_value=0)
    axes[0, 0].bar(
        status_counts.index,
        status_counts.values,
        color=["#3B82A0", "#F2A65A"],
    )
    axes[0, 0].set_title(f"Self-reported discussion status (n={len(frame)})", loc="left")
    axes[0, 0].set_ylabel("Respondents")
    axes[0, 0].grid(axis="y", alpha=0.2)
    for index, value in enumerate(status_counts.values):
        axes[0, 0].text(index, value + 0.15, str(int(value)), ha="center", fontsize=9)

    friend_counts = frame[FRIEND_SAME].fillna("Missing response").value_counts()
    friend_counts = friend_counts.reindex(
        ["Yes", "No"] + [
            value for value in friend_counts.index if value not in {"Yes", "No"}
        ],
        fill_value=0,
    )
    friend_labels = [
        {"Yes": "Same elective", "No": "Different elective"}.get(
            str(value), str(value)
        )
        for value in friend_counts.index
    ]
    friend_colors = [
        {"Yes": "#3B82A0", "No": "#F2A65A"}.get(str(value), "#98A2B3")
        for value in friend_counts.index
    ]
    axes[0, 1].bar(friend_labels, friend_counts.values, color=friend_colors)
    axes[0, 1].set_title(
        f"Best friend's elective choice (n={len(frame)})",
        loc="left",
    )
    axes[0, 1].set_ylabel("Respondents")
    axes[0, 1].grid(axis="y", alpha=0.2)
    for index, value in enumerate(friend_counts.values):
        axes[0, 1].text(index, value + 0.15, str(int(value)), ha="center", fontsize=9)

    _draw_stacked_counts(
        axes[1, 0],
        frame,
        "preferred_subject_category",
        "Discussion by preferred subject",
    )
    _draw_stacked_counts(
        axes[1, 1],
        frame,
        "primary_reason",
        "Discussion by student's primary reason",
    )
    same_table = pd.crosstab(
        frame[DISCUSSION].fillna("Missing response"),
        frame[FRIEND_SAME].fillna("Missing response"),
        dropna=False,
    )
    same_table = same_table.reindex(
        index=["Yes", "No"] + [
            value for value in same_table.index if value not in {"Yes", "No"}
        ],
        columns=["Yes", "No"] + [
            value for value in same_table.columns if value not in {"Yes", "No"}
        ],
        fill_value=0,
    )
    same_table.plot(
        kind="bar",
        ax=axes[2, 0],
        color=["#3B82A0", "#F2A65A"],
        rot=0,
    )
    axes[2, 0].set_title("Friend chose same elective by discussion status (n=24)", loc="left", fontsize=10)
    axes[2, 0].set_xlabel("Reported discussion")
    axes[2, 0].set_ylabel("Respondents")
    axes[2, 0].legend(title="Same elective", fontsize=8, title_fontsize=8)
    axes[2, 0].grid(axis="y", alpha=0.2)

    _draw_stacked_counts(
        axes[2, 1],
        frame,
        "academic_outcome",
        "Discussion by academic outcome",
    )
    _draw_stacked_counts(
        axes[3, 0],
        frame,
        "final_score_range",
        "Discussion by final score response",
    )
    _draw_stacked_counts(
        axes[3, 1],
        frame,
        "best_friend_marks_range",
        "Discussion by best-friend marks response",
    )

    fig.suptitle(
        "Engineering students: self-reported peer discussion and friend responses",
        fontsize=15,
        fontweight="bold",
        y=0.995,
    )
    fig.text(
        0.5,
        0.006,
        "Counts are shown. Unknown, withheld and inapplicable answers remain distinct; "
        "no discussion partners or observed social ties are inferred.",
        ha="center",
        fontsize=9,
        color="#475467",
    )
    fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.98))
    fig.savefig(output_path, dpi=250, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    respondents = load_engineering_survey(REQUIRED_COLUMNS)
    results = analyze_peer_discussion(respondents)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    results["summary"].to_csv(SUMMARY_PATH, index=False)
    results["crosstabs"].to_csv(CROSSTAB_PATH, index=False)
    results["statistics"].to_csv(STATISTICS_PATH, index=False)
    create_peer_figure(respondents)

    print(f"Engineering respondents: {len(respondents)}")
    print("Discussion status:")
    print(respondents[DISCUSSION].value_counts().to_string())
    print("Best-friend same-elective responses:")
    print(respondents[FRIEND_SAME].value_counts().to_string())
    print("Summary:", SUMMARY_PATH)
    print("Cross-tabs:", CROSSTAB_PATH)
    print("Statistics:", STATISTICS_PATH)
    print("Figure:", FIGURE_PATH)


if __name__ == "__main__":
    main()
