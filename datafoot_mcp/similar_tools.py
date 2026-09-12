"""Recherche de joueurs au profil statistique similaire."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from .data_access import load_dataset, normalize_text, search_rows
from .percentile_tools import DEFAULT_PERCENTILE_STATS


def _summary(row: pd.Series) -> dict:
    name_column = "PlayerName" if "PlayerName" in row.index else "Player"
    team_column = "Team" if "Team" in row.index else "Squad"
    return {
        "player": row.get(name_column),
        "team": row.get(team_column),
        "position": row.get("Pos"),
        "age": row.get("Age"),
    }


def find_similar_players(
    player_name: str,
    dataset: str = "Big5",
    top_k: int = 5,
    same_position: bool = True,
    team: str | None = None,
) -> dict:
    """Trouver les joueurs les plus proches statistiquement d'un joueur.

    Les statistiques disponibles sont standardisées dans le groupe de
    comparaison, puis une distance euclidienne est calculée entre le joueur
    cible et chaque candidat. Une distance faible signifie un profil proche.
    """
    df = load_dataset(dataset).copy()
    matching_rows = search_rows(player_name, dataset)
    if team:
        team_column = "Team" if "Team" in matching_rows.columns else "Squad"
        team_key = normalize_text(team)
        team_aliases = {
            "psg": ["paris s-g", "paris saint-germain", "paris sg"],
        }
        team_keys = team_aliases.get(team_key, [team_key])
        matching_rows = matching_rows[
            matching_rows[team_column]
            .map(normalize_text)
            .apply(lambda value: any(key in value for key in team_keys))
        ]
    if matching_rows.empty:
        return {
            "success": False,
            "error": f"Aucun joueur '{player_name}' trouvé dans l'équipe '{team}'.",
        }
    if len(matching_rows) > 1:
        names = matching_rows.apply(
            lambda row: f"{row.get('PlayerName', row.get('Player'))} ({row.get('Team', row.get('Squad'))})",
            axis=1,
        ).tolist()
        return {
            "success": False,
            "error": "Joueur ambigu. Précisez l'équipe : " + ", ".join(names[:10]),
        }
    target = matching_rows.iloc[0]

    peers = df.copy()
    if same_position and "Pos" in peers.columns:
        peers = peers[peers["Pos"].astype(str) == str(target["Pos"])]

    available_stats = [
        stat
        for stat in DEFAULT_PERCENTILE_STATS
        if stat in peers.columns and stat in target.index
    ]
    if not available_stats:
        return {
            "success": False,
            "error": "Aucune statistique commune disponible pour calculer la similarité.",
        }

    numeric = peers[available_stats].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    numeric = numeric.fillna(numeric.median()).fillna(0)

    target_values = pd.to_numeric(
        pd.Series([target[stat] for stat in available_stats], index=available_stats),
        errors="coerce",
    ).fillna(numeric.median()).fillna(0)

    scaler = StandardScaler()
    standardized = scaler.fit_transform(numeric)
    target_standardized = scaler.transform(target_values.to_frame().T)[0]
    distances = np.linalg.norm(standardized - target_standardized, axis=1)

    ranked = peers.copy()
    ranked["_similarity_distance"] = distances
    ranked = ranked[ranked.index != target.name]
    ranked = ranked.sort_values("_similarity_distance", ascending=True)
    ranked = ranked.head(max(1, min(top_k, 50)))

    players = []
    for _, row in ranked.iterrows():
        distance = float(row["_similarity_distance"])
        item = _summary(row)
        item["similarity_distance"] = round(distance, 3)
        item["similarity_score"] = round(100 / (1 + distance), 1)
        players.append(item)

    return {
        "success": True,
        "target_player": _summary(target),
        "comparison_group": {
            "dataset": dataset,
            "position": str(target["Pos"]) if same_position else "all",
            "players_count": len(peers),
            "statistics_count": len(available_stats),
        },
        "method": "Distance euclidienne sur statistiques standardisées",
        "players": players,
    }
