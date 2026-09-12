"""Calcul de percentiles sans dependance a l'interface Streamlit."""

import pandas as pd

from .data_access import get_one_player, load_dataset, normalize_text, search_rows
from .errors import UnsupportedStatisticError


DEFAULT_PERCENTILE_STATS = [
    "Goals_per90", "xG_per90", "npxG_per90", "Assists_per_90", "xAG_per_90", "Take_Ons_Attempted_per_90", "Take_Ons_Succ_per_90", "Touches_per_90", "Touches_Mid_3rd_per_90", "Touches_Att_3rd_per_90", "Touches_Att_Pen_per_90", "Carries_per_90", "Progressive_Carries_per_90", "Progressive_Passes_Received_per_90", "Shot_Creating_Action_per90", "Goal_Creating_Action_90", "Passes_Total_Cmp%", "Key_Passes_per_90", "Passes_1/3_per_90", "Progressive_Passes_per_90", "Passes_Attempted_per_90", "Through_Balls_per_90", "Shots_total_per90", "Shots_on_target_per90", "Goals_per_shot", "Percentage_of_Aerials_Won", "Fouls_Committed_per_90", "Interceptions", "Tackles_Won_per_90", "Ball_Recoveries_per_90", "Blocks_per_90", "Clearances_per_90",
]


def get_player_percentiles(
    player_name: str,
    dataset: str = "Big5",
    statistics: list[str] | None = None,
    top_k: int = 5,
    include_all: bool = False,
    team: str | None = None,
) -> dict:
    """Comparer un joueur aux joueurs du meme poste via des percentiles."""

    df = load_dataset(dataset).copy()
    matching_rows = search_rows(player_name, dataset)
    if team:
        team_column = "Team" if "Team" in matching_rows.columns else "Squad"
        team_key = normalize_text(team)
        team_aliases = {"psg": ["paris s-g", "paris saint-germain", "paris sg"]}
        team_keys = team_aliases.get(team_key, [team_key])
        matching_rows = matching_rows[
            matching_rows[team_column]
            .map(normalize_text)
            .apply(lambda value: any(key in value for key in team_keys))
        ]
    if matching_rows.empty:
        return {"success": False, "error": f"Aucun joueur '{player_name}' trouvé dans l'équipe '{team}'."}
    if len(matching_rows) > 1:
        names = matching_rows.apply(
            lambda row: f"{row.get('PlayerName', row.get('Player'))} ({row.get('Team', row.get('Squad'))})",
            axis=1,
        ).tolist()
        return {"success": False, "error": "Joueur ambigu. Précisez l'équipe : " + ", ".join(names[:10])}
    target = matching_rows.iloc[0]
    position = str(target["Pos"])
    peers = df[df["Pos"].astype(str) == position].copy()
    stats = statistics or [stat for stat in DEFAULT_PERCENTILE_STATS if stat in peers.columns]
    unknown = [stat for stat in stats if stat not in peers.columns]
    if unknown:
        raise UnsupportedStatisticError(f"Statistiques indisponibles pour les percentiles : {', '.join(unknown)}.")
    rows = []
    for stat in stats:
        values = pd.to_numeric(peers[stat], errors="coerce")
        target_value = pd.to_numeric(pd.Series([target[stat]]), errors="coerce").iloc[0]
        if pd.isna(target_value):
            continue
        rows.append({"statistic": stat, "value": float(target_value), "percentile": round(float((values <= target_value).mean() * 100), 1)})
    rows.sort(key=lambda item: item["percentile"], reverse=True)

    # Ne pas envoyer toute la fiche du joueur ni tous les percentiles au LLM
    # par défaut : cela alourdit fortement le contexte, notamment avec Ollama
    # en mode CPU. La logique de calcul ci-dessus reste inchangée.
    name_column = "PlayerName" if "PlayerName" in target.index else "Player"
    team_column = "Team" if "Team" in target.index else "Squad"
    player_summary = {
        key: target.get(key)
        for key in (name_column, team_column, "Pos", "Age", "Min")
        if key in target.index
    }

    result = {
        "success": True,
        "player": player_summary,
        "comparison_group": {
            "dataset": dataset,
            "position": position,
            "players_count": len(peers),
        },
        "percentiles": rows[:max(1, min(top_k, len(rows)))],
        "percentiles_count": len(rows),
    }
    if include_all:
        result["all_percentiles_available"] = rows
    return result
