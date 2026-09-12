"""Classements de joueurs par statistique."""

import pandas as pd

from .data_access import load_dataset, normalize_position, normalize_text, position_matches
from .errors import UnsupportedStatisticError
from .player_tools import _filter_record


STATISTIC_ALIASES = {
    "but": "Non_Penalty_Goals",
    "buts": "Non_Penalty_Goals",
    "goals": "Non_Penalty_Goals",
    "non penalty goals": "Non_Penalty_Goals",
    "occasions": "Shot_Creating_Actions",
    "occasions creees": "Shot_Creating_Actions",
    "occasions créées": "Shot_Creating_Actions",
    "shot creating actions": "Shot_Creating_Actions",
    "passes decisives": "Assists",
    "passes décisives": "Assists",
    "assists": "Assists",
}


def _resolve_statistic(statistic: str, columns: pd.Index) -> str:
    if statistic in columns:
        return statistic
    normalized = normalize_text(statistic)
    resolved = STATISTIC_ALIASES.get(normalized)
    if resolved and resolved in columns:
        return resolved
    raise UnsupportedStatisticError(
        f"Statistique '{statistic}' indisponible. Statistiques de classement "
        f"courantes : Non_Penalty_Goals, Shot_Creating_Actions, Assists."
    )


def rank_players(
    dataset: str = "Ligue1",
    statistic: str = "Non_Penalty_Goals",
    team: str | None = None,
    position: str | None = None,
    minutes_min: float | None = 400,
    top_k: int = 10,
    ascending: bool = False,
) -> dict:
    """Classer les joueurs selon une statistique, du plus haut au plus bas."""
    df = load_dataset(dataset).copy()
    resolved_statistic = _resolve_statistic(statistic, df.columns)

    if team:
        team_column = "Team" if "Team" in df.columns else "Squad"
        df = df[
            df[team_column]
            .map(normalize_text)
            .str.contains(normalize_text(team), regex=False, na=False)
        ]
    if position:
        df = df[df["Pos"].map(lambda value: position_matches(value, position))]
    if minutes_min is not None and "Min" in df.columns:
        df = df[pd.to_numeric(df["Min"], errors="coerce") >= minutes_min]

    df[resolved_statistic] = pd.to_numeric(df[resolved_statistic], errors="coerce")
    df = df.dropna(subset=[resolved_statistic])
    df = df.sort_values(resolved_statistic, ascending=ascending).head(max(1, min(top_k, 200)))

    return {
        "success": True,
        "ranking": {
            "dataset": dataset,
            "statistic_requested": statistic,
            "statistic_used": resolved_statistic,
            "team": team,
            "position": normalize_position(position) if position else None,
            "minutes_min": minutes_min,
            "order": "ascending" if ascending else "descending",
        },
        "count_returned": len(df),
        "players": [_filter_record(row, resolved_statistic) for _, row in df.iterrows()],
    }
