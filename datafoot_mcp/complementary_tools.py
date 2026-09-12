"""Joueurs complementaires, base sur la logique de Scout.py."""

import pandas as pd
from sklearn.preprocessing import StandardScaler

from .data_access import load_dataset, normalize_text, search_rows


# Meme principe de ponderation que Scout.py, conserve ici pour que le serveur
# MCP reste independant de Streamlit.
WEIGHTS = {
    "CB": {"Non_Penalty_Goals": .1, "npxG_Non_Penalty_xG": .1, "Shots_Total": .2, "Assists": .2, "xAG_Exp_Assisted_Goals": .3, "Shot_Creating_Actions": .2, "Passes_Attempted": .4, "Pass_Completion_Percentage": .7, "Progressive_Passes": .5, "Progressive_Carries": .5, "Successful_Take_Ons": .3, "Touches_Att_Pen": .1, "Progressive_Passes_Rec": .2, "Tackles": .6, "Interceptions": .6, "Blocks": .7, "Clearances": .7, "Aerials_Won": .7},
    "FB": {"Non_Penalty_Goals": .1, "npxG_Non_Penalty_xG": .2, "Shots_Total": .3, "Assists": .4, "xAG_Exp_Assisted_Goals": .5, "Shot_Creating_Actions": .4, "Passes_Attempted": .4, "Pass_Completion_Percentage": .6, "Progressive_Passes": .5, "Progressive_Carries": .5, "Successful_Take_Ons": .4, "Touches_Att_Pen": .3, "Progressive_Passes_Rec": .5, "Tackles": .6, "Interceptions": .4, "Blocks": .4, "Clearances": .4, "Aerials_Won": .6},
    "MF": {"Non_Penalty_Goals": .4, "npxG_Non_Penalty_xG": .5, "Shots_Total": .5, "Assists": .5, "xAG_Exp_Assisted_Goals": .5, "Shot_Creating_Actions": .5, "Passes_Attempted": .7, "Pass_Completion_Percentage": .8, "Progressive_Passes": .7, "Progressive_Carries": .7, "Successful_Take_Ons": .5, "Touches_Att_Pen": .5, "Progressive_Passes_Rec": .6, "Tackles": .4, "Interceptions": .5, "Blocks": .4, "Clearances": .3, "Aerials_Won": .5},
    "AM": {"Non_Penalty_Goals": .7, "npxG_Non_Penalty_xG": .8, "Shots_Total": .7, "Assists": .7, "xAG_Exp_Assisted_Goals": .8, "Shot_Creating_Actions": .8, "Passes_Attempted": .5, "Pass_Completion_Percentage": .6, "Progressive_Passes": .6, "Progressive_Carries": .8, "Successful_Take_Ons": .8, "Touches_Att_Pen": .7, "Progressive_Passes_Rec": .7, "Tackles": .1, "Interceptions": .3, "Blocks": .2, "Clearances": .2, "Aerials_Won": .3},
    "FW": {"Non_Penalty_Goals": .9, "npxG_Non_Penalty_xG": .9, "Shots_Total": .7, "Assists": .7, "xAG_Exp_Assisted_Goals": .8, "Shot_Creating_Actions": .7, "Passes_Attempted": .4, "Pass_Completion_Percentage": .5, "Progressive_Passes": .4, "Progressive_Carries": .5, "Successful_Take_Ons": .6, "Touches_Att_Pen": .8, "Progressive_Passes_Rec": .7, "Tackles": .1, "Interceptions": .2, "Blocks": .2, "Clearances": .2, "Aerials_Won": .4},
}


def _standardize_data_like_scout(weights: dict, df: pd.DataFrame) -> pd.DataFrame:
    """Reproduire exactement la standardisation utilisée par views/Scout.py."""
    data = df.copy()
    scaler = StandardScaler()

    for position in data["Pos"].dropna().unique():
        position_data = data[data["Pos"] == position].copy()
        position_weights = weights.get(position, {})
        columns_to_scale = [
            column for column in position_data.columns
            if column in position_weights
        ]
        if not columns_to_scale:
            continue

        # Scout.py applique d'abord le poids, puis standardise chaque poste.
        for column in columns_to_scale:
            position_data[column] = pd.to_numeric(
                position_data[column], errors="coerce"
            ) * position_weights[column]

        scaled_features = scaler.fit_transform(position_data[columns_to_scale])
        scaled = pd.DataFrame(
            scaled_features,
            columns=columns_to_scale,
            index=position_data.index,
        )
        data.loc[position_data.index, columns_to_scale] = scaled

    return data


def find_complementary_players(
    player_name: str,
    dataset: str = "Liga",
    top_k: int = 5,
    team: str | None = None,
) -> dict:
    """Reproduire la logique de Scout.py pour trouver les complémentaires."""

    original_df = load_dataset(dataset).copy()
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
    standardized_data = _standardize_data_like_scout(WEIGHTS, original_df)

    # Scout.py identifie les faiblesses parmi toutes les colonnes numériques,
    # puis conserve les joueurs du même poste positifs sur ces faiblesses.
    target_standardized = standardized_data.loc[target.name]
    numeric_columns = standardized_data.select_dtypes(include=["number"]).columns.tolist()
    weaknesses = target_standardized[numeric_columns][
        target_standardized[numeric_columns] < 0
    ].index.tolist()

    if not weaknesses:
        return {
            "success": True,
            "target_player": {
                "player": target.get("PlayerName", target.get("Player")),
                "team": target.get("Team", target.get("Squad")),
                "position": target.get("Pos"),
                "age": target.get("Age"),
            },
            "method": "Scout.py : aucune faiblesse identifiee",
            "weakness_statistics": [],
            "players": [],
        }

    position = target["Pos"]
    same_position = standardized_data["Pos"] == position

    # Première règle de Scout.py : positif sur toutes les faiblesses.
    filter_mask = (standardized_data[weaknesses] > 0).all(axis=1)
    complementary_mask = filter_mask & same_position

    # Deuxième règle de Scout.py pour plus de cinq faiblesses.
    if len(weaknesses) > 5:
        weaknesses_needed = len(weaknesses) // 1.4
        filter_mask = (
            standardized_data[weaknesses] > 0
        ).sum(axis=1) >= weaknesses_needed
        complementary_mask = filter_mask & same_position

    indices = standardized_data.index[complementary_mask]
    indices = indices[indices != target.name]
    candidates = original_df.loc[indices].head(max(1, min(top_k, 50)))

    results = []
    for _, row in candidates.iterrows():
        # Le modèle n'a besoin que des informations utiles au classement.
        # Renvoyer toute la fiche statistique gonfle fortement son contexte,
        # surtout avec Ollama exécuté sur CPU.
        name_column = "PlayerName" if "PlayerName" in row.index else "Player"
        team_column = "Team" if "Team" in row.index else "Squad"
        result = {
            "player": row.get(name_column),
            "team": row.get(team_column),
            "position": row.get("Pos"),
            "age": row.get("Age"),
        }
        results.append(result)

    target_name_column = "PlayerName" if "PlayerName" in target.index else "Player"
    target_team_column = "Team" if "Team" in target.index else "Squad"
    target_summary = {
        "player": target.get(target_name_column),
        "team": target.get(target_team_column),
        "position": target.get("Pos"),
        "age": target.get("Age"),
    }
    return {
        "success": True,
        "target_player": target_summary,
        "method": "Scout : meme poste, forces sur les faiblesses standardisees",
        "weakness_statistics": weaknesses,
        "players": results,
    }
