"""Shared descriptive and small-sample statistical helpers for survey analyses."""

from itertools import product
from math import comb, exp, isfinite, lgamma, log, sqrt
from pathlib import Path
import random

import pandas as pd

from src.build_engineering_similarity_network import load_engineering_population


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"
MISSING_LABEL = "Missing response"

_INAPPLICABLE = {
    "course_difficulty": {"Not completed yet"},
    "final_score_range": {
        "Result not declared",
        "Did not appear for the examination",
    },
}
_UNKNOWN = {
    "best_friend_choice_reason": {"Not sure / Idk"},
    "best_friend_marks_range": {"I don't know"},
    "academic_outcome": {"Prefer not to say"},
}


def load_engineering_survey(
    required_columns: tuple[str, ...] | list[str],
    path: Path = DATA_PATH,
) -> pd.DataFrame:
    """Load the validated engineering cohort and check analysis-specific fields."""
    respondents = load_engineering_population(path)
    missing_columns = sorted(set(required_columns) - set(respondents.columns))
    if missing_columns:
        raise ValueError(f"Survey is missing required columns: {missing_columns}")
    return respondents


def response_class(column: str, value: object) -> str:
    """Classify missing, unknown and inapplicable categories without recoding them."""
    if pd.isna(value) or (isinstance(value, str) and not value.strip()):
        return "missing"
    text = str(value).strip()
    if text in _INAPPLICABLE.get(column, set()):
        return "inapplicable"
    if text in _UNKNOWN.get(column, set()):
        return "unknown_or_withheld"
    return "answered"


def _category_values(series: pd.Series) -> pd.Series:
    return series.astype("object").where(series.notna(), MISSING_LABEL)


def frequency_rows(
    frame: pd.DataFrame,
    columns: tuple[str, ...] | list[str],
    analysis_prefix: str,
) -> list[dict[str, object]]:
    """Return frequency and denominator rows, preserving response status."""
    rows = []
    for column in columns:
        values = _category_values(frame[column])
        counts = values.value_counts(dropna=False, sort=False)
        total = len(frame)
        for category, count in counts.items():
            rows.append(
                {
                    "analysis": f"{analysis_prefix}:{column}",
                    "variable": column,
                    "category": category,
                    "response_class": response_class(
                        column,
                        pd.NA if category == MISSING_LABEL else category,
                    ),
                    "respondent_count": int(count),
                    "denominator": total,
                    "percent_of_denominator": (
                        100 * int(count) / total if total else float("nan")
                    ),
                    "missing_count": int(frame[column].isna().sum()),
                }
            )
    return rows


def crosstab_rows(
    frame: pd.DataFrame,
    row_variable: str,
    column_variable: str,
    analysis: str,
) -> list[dict[str, object]]:
    """Return a long cross-tab with row and column denominators and percentages."""
    row_values = _category_values(frame[row_variable])
    column_values = _category_values(frame[column_variable])
    table = pd.crosstab(row_values, column_values, dropna=False)
    row_totals = table.sum(axis=1)
    column_totals = table.sum(axis=0)
    total = int(table.to_numpy().sum())
    rows = []

    for row_category, column_category in product(table.index, table.columns):
        count = int(table.loc[row_category, column_category])
        row_denominator = int(row_totals[row_category])
        column_denominator = int(column_totals[column_category])
        rows.append(
            {
                "analysis": analysis,
                "row_variable": row_variable,
                "row_category": row_category,
                "column_variable": column_variable,
                "column_category": column_category,
                "respondent_count": count,
                "row_denominator": row_denominator,
                "percent_within_row": (
                    100 * count / row_denominator if row_denominator else float("nan")
                ),
                "column_denominator": column_denominator,
                "percent_within_column": (
                    100 * count / column_denominator
                    if column_denominator
                    else float("nan")
                ),
                "total_denominator": total,
                "missing_row_count": int(frame[row_variable].isna().sum()),
                "missing_column_count": int(frame[column_variable].isna().sum()),
                "row_response_class": response_class(
                    row_variable,
                    pd.NA if row_category == MISSING_LABEL else row_category,
                ),
                "column_response_class": response_class(
                    column_variable,
                    pd.NA if column_category == MISSING_LABEL else column_category,
                ),
            }
        )
    return rows


def _regularized_gamma_q(shape: float, value: float) -> float:
    """Compute the upper regularized incomplete gamma function."""
    if shape <= 0 or value < 0:
        raise ValueError("Gamma shape must be positive and value nonnegative.")
    if value == 0:
        return 1.0
    log_scale = -value + shape * log(value) - lgamma(shape)
    epsilon = 1e-14
    tiny = 1e-300

    if value < shape + 1:
        term = 1.0 / shape
        total = term
        denominator = shape
        for _ in range(10000):
            denominator += 1
            term *= value / denominator
            total += term
            if abs(term) <= abs(total) * epsilon:
                break
        lower = total * exp(log_scale)
        return min(1.0, max(0.0, 1.0 - lower))

    b = value + 1 - shape
    c = 1 / tiny
    d = 1 / b
    fraction = d
    for index in range(1, 10000):
        coefficient = -index * (index - shape)
        b += 2
        d = coefficient * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + coefficient / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        fraction *= delta
        if abs(delta - 1) <= epsilon:
            break
    return min(1.0, max(0.0, exp(log_scale) * fraction))


def _fisher_exact_2x2(
    table: list[list[int]],
) -> tuple[float, float]:
    """Return conditional odds ratio and two-sided Fisher exact p-value."""
    a, b = table[0]
    c, d = table[1]
    row_one = a + b
    column_one = a + c
    total = a + b + c + d
    odds_ratio = (a * d / (b * c)) if b * c else (
        float("inf") if a * d else float("nan")
    )
    lower = max(0, row_one - (total - column_one))
    upper = min(row_one, column_one)

    def probability(value: int) -> float:
        return (
            comb(column_one, value)
            * comb(total - column_one, row_one - value)
            / comb(total, row_one)
        )

    observed_probability = probability(a)
    p_value = sum(
        probability(value)
        for value in range(lower, upper + 1)
        if probability(value) <= observed_probability + 1e-12
    )
    return odds_ratio, min(1.0, p_value)


def _expected_counts(table: list[list[int]]) -> list[list[float]]:
    row_totals = [sum(row) for row in table]
    column_totals = [
        sum(table[row][column] for row in range(len(table)))
        for column in range(len(table[0]))
    ]
    total = sum(row_totals)
    return [
        [
            row_total * column_total / total
            for column_total in column_totals
        ]
        for row_total in row_totals
    ]


def _cramers_v(table: list[list[int]]) -> float:
    rows = len(table)
    columns = len(table[0]) if rows else 0
    total = sum(sum(row) for row in table)
    if total == 0 or min(rows - 1, columns - 1) <= 0:
        return float("nan")
    expected = _expected_counts(table)
    chi_square = sum(
        (table[row][column] - expected[row][column]) ** 2 / expected[row][column]
        for row in range(rows)
        for column in range(columns)
        if expected[row][column] > 0
    )
    return sqrt(chi_square / (total * min(rows - 1, columns - 1)))


def categorical_association(
    table: list[list[int]],
    analysis: str,
    denominator: int | None = None,
) -> dict[str, object]:
    """Select a suitable categorical test and report its denominator/effect size."""
    if not table or not table[0]:
        raise ValueError("Contingency table must have at least one row and column.")
    if any(len(row) != len(table[0]) for row in table):
        raise ValueError("Contingency table rows must have equal lengths.")

    row_indices = [i for i, row in enumerate(table) if sum(row) > 0]
    column_indices = [
        j for j in range(len(table[0]))
        if sum(table[i][j] for i in range(len(table))) > 0
    ]
    reduced = [[table[i][j] for j in column_indices] for i in row_indices]
    sample_size = sum(sum(row) for row in reduced)
    result: dict[str, object] = {
        "analysis": analysis,
        "sample_size": sample_size,
        "denominator": denominator if denominator is not None else sample_size,
        "test_used": "not_performed",
        "test_statistic": float("nan"),
        "p_value": float("nan"),
        "p_value_method": "",
        "effect_size_name": "Cramer's V",
        "effect_size": _cramers_v(reduced) if reduced else float("nan"),
        "effect_size_interpretation": (
            "Descriptive only; sparse counts make this estimate unstable."
        ),
        "minimum_expected_count": float("nan"),
        "test_selection_reason": "",
    }

    if len(reduced) < 2 or len(column_indices) < 2:
        result["test_selection_reason"] = (
            "At least two nonempty categories are required on both dimensions."
        )
        return result

    expected = _expected_counts(reduced)
    minimum_expected = min(min(row) for row in expected)
    result["minimum_expected_count"] = minimum_expected

    if len(reduced) == 2 and len(column_indices) == 2:
        odds_ratio, p_value = _fisher_exact_2x2(reduced)
        result.update(
            {
                "test_used": "Fisher exact (two-sided)",
                "test_statistic": odds_ratio,
                "p_value": p_value,
                "p_value_method": "conditional exact, probability ordered",
                "effect_size_name": "Cramer's V",
                "effect_size_interpretation": (
                    "Descriptive effect size for a 2x2 exact test."
                ),
                "test_selection_reason": (
                    "A 2x2 table with small sample/expected counts uses an exact test."
                ),
            }
        )
        return result

    if minimum_expected < 5:
        result["test_selection_reason"] = (
            "Pearson chi-square not used: at least one expected cell count is below 5."
        )
        return result

    chi_square = sum(
        (reduced[i][j] - expected[i][j]) ** 2 / expected[i][j]
        for i in range(len(reduced))
        for j in range(len(column_indices))
    )
    degrees_freedom = (len(reduced) - 1) * (len(column_indices) - 1)
    p_value = _regularized_gamma_q(degrees_freedom / 2, chi_square / 2)
    result.update(
        {
            "test_used": "Pearson chi-square",
            "test_statistic": chi_square,
            "p_value": p_value,
            "p_value_method": "chi-square survival function",
            "effect_size_name": "Cramer's V",
            "effect_size": sqrt(
                chi_square / (sample_size * min(len(reduced) - 1, len(column_indices) - 1))
            ),
            "effect_size_interpretation": (
                "Cramer's V for a table meeting expected-count assumptions."
            ),
            "test_selection_reason": (
                "All expected cell counts are at least 5."
            ),
        }
    )
    return result


def _average_ranks(values: list[int]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        average_rank = (cursor + 1 + end) / 2
        for position in range(cursor, end):
            ranks[order[position]] = average_rank
        cursor = end
    return ranks


def _pearson_correlation(first: list[float], second: list[float]) -> float:
    first_mean = sum(first) / len(first)
    second_mean = sum(second) / len(second)
    covariance = sum(
        (a - first_mean) * (b - second_mean)
        for a, b in zip(first, second)
    )
    first_ss = sum((value - first_mean) ** 2 for value in first)
    second_ss = sum((value - second_mean) ** 2 for value in second)
    denominator = sqrt(first_ss * second_ss)
    return covariance / denominator if denominator else float("nan")


def spearman_permutation(
    first: list[int],
    second: list[int],
    analysis: str,
    seed: int = 42,
    permutations: int = 9999,
    denominator: int | None = None,
) -> dict[str, object]:
    """Calculate Spearman rho and a reproducible two-sided permutation p-value."""
    if len(first) != len(second) or len(first) < 3:
        raise ValueError("Spearman inputs must have equal lengths of at least 3.")
    if permutations < 1:
        raise ValueError("At least one permutation is required.")

    first_ranks = _average_ranks(first)
    second_ranks = _average_ranks(second)
    observed = _pearson_correlation(first_ranks, second_ranks)
    if not isfinite(observed):
        return {
            "analysis": analysis,
            "sample_size": len(first),
            "denominator": denominator if denominator is not None else len(first),
            "excluded_count": (
                denominator - len(first) if denominator is not None else 0
            ),
            "test_used": "not_performed",
            "test_statistic": float("nan"),
            "p_value": float("nan"),
            "p_value_method": "",
            "effect_size_name": "Spearman rho",
            "effect_size": float("nan"),
            "minimum_expected_count": float("nan"),
            "test_selection_reason": (
                "Spearman correlation is undefined because one variable has no variation."
            ),
        }

    rng = random.Random(seed)
    extreme = 0
    permuted = second_ranks.copy()
    for _ in range(permutations):
        rng.shuffle(permuted)
        value = _pearson_correlation(first_ranks, permuted)
        if abs(value) >= abs(observed) - 1e-12:
            extreme += 1
    return {
        "analysis": analysis,
        "sample_size": len(first),
        "denominator": denominator if denominator is not None else len(first),
        "excluded_count": (
            denominator - len(first) if denominator is not None else 0
        ),
        "test_used": "Spearman rank correlation",
        "test_statistic": observed,
        "p_value": (extreme + 1) / (permutations + 1),
        "p_value_method": (
            f"two-sided permutation, {permutations} shuffles, seed={seed}"
        ),
        "effect_size_name": "Spearman rho",
        "effect_size": observed,
        "minimum_expected_count": float("nan"),
        "test_selection_reason": (
            "Both variables are treated as ordered categorical ranks; "
            "unrankable response categories are excluded."
        ),
    }


def ordered_study_hours(value: object) -> int | None:
    """Map actual ordered study-hour brackets; irregular preparation is excluded."""
    labels = {
        "Less than 2 hours": 1,
        "2–4 hours": 2,
        "2-4 hours": 2,
        "4–6 hours": 3,
        "4-6 hours": 3,
        "More than 8 hours": 4,
    }
    return labels.get(str(value).strip())


def ordered_academic_outcome(value: object) -> int | None:
    """Map observed grade prefixes from D through S; non-grades are excluded."""
    if not isinstance(value, str):
        return None
    prefix = value.strip()[:1].upper()
    return {"D": 1, "C": 2, "B": 3, "A": 4, "S": 5}.get(prefix)


def ordered_final_score(value: object) -> int | None:
    """Map declared final score brackets in increasing order."""
    text = str(value).strip().replace("–", "-").replace("−", "-")
    labels = {
        "Below 40": 1,
        "40-49": 2,
        "50-59": 3,
        "60-69": 4,
        "70-79": 5,
        "80-89": 6,
        "90-100": 7,
    }
    return labels.get(text)


def crosstab_matrix(
    frame: pd.DataFrame,
    row_variable: str,
    column_variable: str,
) -> tuple[list[object], list[object], list[list[int]]]:
    """Return ordered labels and the integer matrix for a contingency table."""
    rows = _category_values(frame[row_variable])
    columns = _category_values(frame[column_variable])
    table = pd.crosstab(rows, columns, dropna=False)
    return list(table.index), list(table.columns), table.to_numpy(dtype=int).tolist()
