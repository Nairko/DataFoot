"""Outils MCP de statistiques globales et de comparaison."""

from .data_access import get_one_player, public_record
from .errors import UnsupportedStatisticError


def get_player_stats(player_name: str, dataset: str = "Big5", statistics: list[str] | None = None) -> dict:
    """Retourner les statistiques disponibles d'un joueur."""

    row = get_one_player(player_name, dataset)
    record = public_record(row)
    if statistics:
        unknown = [stat for stat in statistics if stat not in row.index]
        if unknown:
            raise UnsupportedStatisticError(f"Statistiques inconnues dans {dataset} : {', '.join(unknown)}.")
        keep = {"Player", "PlayerName", "Team", "Squad", "Pos", "Age", "Min", "90s", "dataset", *statistics}
        record = {key: value for key, value in record.items() if key in keep}
    return {"success": True, "player": record}


def compare_players(player_a: str, player_b: str, dataset: str = "Big5", statistics: list[str] | None = None) -> dict:
    """Comparer deux joueurs sur des statistiques numeriques communes."""

    first = get_one_player(player_a, dataset)
    second = get_one_player(player_b, dataset)
    if statistics is None:
        excluded = {"Age", "MP", "Starts", "Min", "90s"}
        statistics = [column for column in first.index if column in second.index and not str(column).startswith("_") and column not in excluded]
    unknown = [stat for stat in statistics if stat not in first.index or stat not in second.index]
    if unknown:
        raise UnsupportedStatisticError(f"Statistiques absentes pour la comparaison : {', '.join(unknown)}.")
    comparison = []
    for stat in statistics:
        try:
            value_a, value_b = float(first[stat]), float(second[stat])
        except (TypeError, ValueError):
            continue
        comparison.append({"statistic": stat, "player_a": value_a, "player_b": value_b, "difference_a_minus_b": value_a - value_b})
    return {"success": True, "player_a": public_record(first), "player_b": public_record(second), "comparison": comparison}
