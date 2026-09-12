"""Outils MCP de recherche et de filtrage de joueurs."""

import pandas as pd

from .data_access import normalize_position, load_dataset, normalize_text, position_matches, public_record, search_rows
from .errors import InvalidFilterError, UnsupportedStatisticError


def search_player(player_name: str, dataset: str = "Big5", max_results: int = 10) -> dict:
    """Rechercher un joueur par nom exact ou partiel."""

    rows = search_rows(player_name, dataset).head(max(1, min(max_results, 50)))
    return {"success": True, "query": player_name, "dataset": dataset, "count": len(rows), "players": [public_record(row) for _, row in rows.iterrows()]}


def _filter_record(row: pd.Series, statistic: str | None) -> dict:
    """Retourne un resume compact, adapte a la consommation par un LLM."""

    name_column = "PlayerName" if "PlayerName" in row.index else "Player"
    team_column = "Team" if "Team" in row.index else "Squad"
    fields = [name_column, team_column, "Pos", "Age", "Min"]
    if statistic and statistic in row.index:
        fields.append(statistic)
    return {field: row.get(field) for field in fields if field in row.index}


def filter_players(
    dataset: str = "Liga",
    position: str | None = None,
    age_max: float | None = None,
    age_min: float | None = None,
    minutes_min: float | None = None,
    team: str | None = None,
    statistic: str | None = None,
    operator: str | None = None,
    value: float | None = None,
    max_results: int = 20,
) -> dict:
    """Filtrer par championnat, poste, age, minutes, equipe ou statistique."""

    df = load_dataset(dataset).copy()
    if position:
        df = df[df["Pos"].map(lambda item: position_matches(item, position))]
    if age_min is not None:
        df = df[pd.to_numeric(df["Age"], errors="coerce") >= age_min]
    if age_max is not None:
        # Borne exclusive : "moins de 22 ans" signifie Age < 22.
        df = df[pd.to_numeric(df["Age"], errors="coerce") < age_max]
    if minutes_min is not None:
        df = df[pd.to_numeric(df["Min"], errors="coerce") >= minutes_min]
    if team:
        team_column = "Team" if "Team" in df.columns else "Squad"
        df = df[df[team_column].map(normalize_text).str.contains(normalize_text(team), regex=False, na=False)]
    if statistic is not None:
        if statistic not in df.columns:
            raise UnsupportedStatisticError(f"La statistique '{statistic}' n'existe pas dans {dataset}.")
        if operator not in {">", ">=", "<", "<=", "=="} or value is None:
            raise InvalidFilterError("Un filtre statistique doit fournir operator et value.")
        series = pd.to_numeric(df[statistic], errors="coerce")
        masks = {">": series > value, ">=": series >= value, "<": series < value, "<=": series <= value, "==": series == value}
        df = df[masks[operator]]
    df = df.head(max(1, min(max_results, 200)))
    return {
        "success": True,
        "filters": {"dataset": dataset, "position": normalize_position(position) if position else None, "age_min": age_min, "age_max_exclusive": age_max, "minutes_min": minutes_min, "team": team, "statistic": statistic, "operator": operator, "value": value},
        "count_returned": len(df),
        "players": [_filter_record(row, statistic) for _, row in df.iterrows()],
    }
