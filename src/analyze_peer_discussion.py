import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
REPORT_DIR = ROOT / "outputs" / "reports"
GRAPH_PATH = ROOT / "outputs" / "graphs" / "peer_discussion_summary.png"
TABLE_PATH = REPORT_DIR / "peer_discussion_summary.csv"

REQUIRED_COLUMNS = [
    "respondent_id",
    "discussed_elective_with_friends",
    "best_friend_same_elective",
    "best_friend_choice_reason",
    "preferred_subject_category",
]


def _append_summary(
    rows: list[dict[str, object]],
    frame: pd.DataFrame,
    analysis: str,
    category_column: str,
) -> None:
    for (discussion_status, category), count in (
        frame.groupby(
            ["discussed_elective_with_friends", category_column],
            sort=True,
            dropna=False,
        )
        .size()
        .items()
    ):
        group_total = int(
            (frame["discussed_elective_with_friends"] == discussion_status).sum()
        )
        rows.append(
            {
                "analysis": analysis,
                "discussion_status": discussion_status,
                "category": category,
                "respondent_count": int(count),
                "percent_within_discussion_status": round(
                    100 * int(count) / group_total, 1
                ),
                "group_total": group_total,
            }
        )


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Survey is missing required columns: {missing_columns}")
    if df["respondent_id"].isna().any() or not df["respondent_id"].is_unique:
        raise ValueError("Respondent IDs must be present and unique.")
    if df[REQUIRED_COLUMNS].isna().any().any():
        raise ValueError("Required peer-discussion fields contain missing values.")

    status_columns = [
        "discussed_elective_with_friends",
        "best_friend_same_elective",
    ]
    for column in status_columns:
        df[column] = df[column].astype(str).str.strip()
        invalid = sorted(set(df[column]) - {"Yes", "No"})
        if invalid:
            raise ValueError(f"Unexpected responses in {column}: {invalid}")

    status_counts = (
        df["discussed_elective_with_friends"].value_counts().reindex(["Yes", "No"], fill_value=0)
    )
    rows: list[dict[str, object]] = []
    for status, count in status_counts.items():
        rows.append(
            {
                "analysis": "discussion_status",
                "discussion_status": "All respondents",
                "category": status,
                "respondent_count": int(count),
                "percent_within_discussion_status": round(
                    100 * int(count) / len(df), 1
                ),
                "group_total": len(df),
            }
        )

    _append_summary(
        rows,
        df,
        "discussion_by_best_friend_same_elective",
        "best_friend_same_elective",
    )
    _append_summary(
        rows,
        df,
        "discussion_by_best_friend_choice_reason",
        "best_friend_choice_reason",
    )
    _append_summary(
        rows,
        df,
        "discussion_by_preferred_subject_category",
        "preferred_subject_category",
    )

    summary = pd.DataFrame(rows)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLE_PATH, index=False)

    status_order = ["Yes", "No"]
    friend_order = ["Yes", "No"]
    friend_crosstab = pd.crosstab(
        df["discussed_elective_with_friends"],
        df["best_friend_same_elective"],
    ).reindex(index=status_order, columns=friend_order, fill_value=0)
    reason_counts = (
        df.loc[df["discussed_elective_with_friends"] == "Yes", "best_friend_choice_reason"]
        .value_counts()
        .sort_values()
    )

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].bar(status_counts.index, status_counts.values, color=["#4C78A8", "#F58518"])
    axes[0].set_title("Discussed elective with friends")
    axes[0].set_ylabel("Respondents")
    axes[0].grid(axis="y", alpha=0.25)

    friend_crosstab.plot(
        kind="bar",
        ax=axes[1],
        color=["#4C78A8", "#F58518"],
        rot=0,
    )
    axes[1].set_title("Best friend chose same elective")
    axes[1].set_xlabel("Reported discussion")
    axes[1].set_ylabel("Respondents")
    axes[1].legend(title="Same elective")
    axes[1].grid(axis="y", alpha=0.25)

    axes[2].barh(reason_counts.index, reason_counts.values, color="#54A24B")
    axes[2].set_title("Best friend's reported choice reason\n(discussion = Yes)")
    axes[2].set_xlabel("Respondents")
    axes[2].tick_params(axis="y", labelsize=8)
    axes[2].grid(axis="x", alpha=0.25)

    fig.suptitle(
        "Self-reported peer discussion (survey responses; not observed social ties)",
        fontsize=14,
    )
    fig.tight_layout()
    fig.savefig(GRAPH_PATH, dpi=250, bbox_inches="tight")
    plt.close(fig)

    print("Respondents:", len(df))
    print("Discussed with friends:", int(status_counts["Yes"]))
    print("Did not discuss with friends:", int(status_counts["No"]))
    print("Aggregate table saved:", TABLE_PATH)
    print("Chart saved:", GRAPH_PATH)


if __name__ == "__main__":
    main()
