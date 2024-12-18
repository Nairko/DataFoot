import pandas as pd
import streamlit as st
from data_loader import load_data

from sklearn.preprocessing import StandardScaler

df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()

def get_weights():
    raw_weights= {
        'CB': {'Non_Penalty_Goals': 0.1, 'npxG_Non_Penalty_xG': 0.1, 'Shots_Total': 0.2, 'Assists': 0.2,
               'xAG_Exp_Assisted_Goals': 0.3, 'Shot_Creating_Actions': 0.2, 'Passes_Attempted': 0.4, 'Pass_Completion_Percentage': 0.7,
               'Progressive_Passes': 0.5, 'Progressive_Carries': 0.5, 'Successful_Take_Ons': 0.3, 'Touches_Att_Pen': 0.1,
               'Progressive_Passes_Rec': 0.2, 'Tackles': 0.6, 'Interceptions': 0.6, 'Blocks': 0.7,'Clearances':0.7,'Aerials_Won':0.7},
        'FB': {'Non_Penalty_Goals': 0.1, 'npxG_Non_Penalty_xG': 0.3, 'Shots_Total': 0.3, 'Assists': 0.5,
               'xAG_Exp_Assisted_Goals': 0.6, 'Shot_Creating_Actions': 0.4, 'Passes_Attempted': 0.5, 'Pass_Completion_Percentage': 0.7,
               'Progressive_Passes': 0.7, 'Progressive_Carries': 0.6, 'Successful_Take_Ons': 0.5, 'Touches_Att_Pen': 0.3,
               'Progressive_Passes_Rec': 0.5, 'Tackles': 0.5, 'Interceptions': 0.5, 'Blocks': 0.5,'Clearances':0.4,'Aerials_Won':0.6},
        'MF': {'Non_Penalty_Goals': 0.4, 'npxG_Non_Penalty_xG': 0.5, 'Shots_Total': 0.2, 'Assists': 0.5,
               'xAG_Exp_Assisted_Goals': 0.6, 'Shot_Creating_Actions': 0.7, 'Passes_Attempted': 0.6, 'Pass_Completion_Percentage': 0.7,
               'Progressive_Passes': 0.8, 'Progressive_Carries': 0.7, 'Successful_Take_Ons': 0.3, 'Touches_Att_Pen': 0.3,
               'Progressive_Passes_Rec': 0.7, 'Tackles': 0.4, 'Interceptions': 0.5, 'Blocks': 0.5,'Clearances':0.3,'Aerials_Won':0.4},
        'AM': {'Non_Penalty_Goals': 0.7, 'npxG_Non_Penalty_xG': 0.8, 'Shots_Total': 0.6, 'Assists': 0.7,
               'xAG_Exp_Assisted_Goals': 0.8, 'Shot_Creating_Actions': 0.8, 'Passes_Attempted': 0.5, 'Pass_Completion_Percentage': 0.6,
               'Progressive_Passes': 0.6, 'Progressive_Carries': 0.8, 'Successful_Take_Ons': 0.8, 'Touches_Att_Pen': 0.7,
               'Progressive_Passes_Rec': 0.7, 'Tackles': 0.1, 'Interceptions': 0.3, 'Blocks': 0.2,'Clearances':0.2,'Aerials_Won':0.3},
        'FW': {'Non_Penalty_Goals': 0.9, 'npxG_Non_Penalty_xG': 0.9, 'Shots_Total': 0.7, 'Assists': 0.7,
               'xAG_Exp_Assisted_Goals': 0.7, 'Shot_Creating_Actions': 0.7, 'Passes_Attempted': 0.4, 'Pass_Completion_Percentage': 0.6,
               'Progressive_Passes': 0.4, 'Progressive_Carries': 0.6, 'Successful_Take_Ons': 0.6, 'Touches_Att_Pen': 0.8,
               'Progressive_Passes_Rec': 0.7, 'Tackles': 0.1, 'Interceptions': 0.2, 'Blocks': 0.2,'Clearances':0.2,'Aerials_Won':0.4},

        # Ajoute d'autres postes et leurs poids ici
    }
    adjusted_weights = {pos: {stat: 1 + weight for stat, weight in pos_weights.items()} for pos, pos_weights in raw_weights.items()}
    return adjusted_weights


def standardize_data(weights, df):
    scaler = StandardScaler()

    # Identifiez toutes les colonnes à mettre à l'échelle en prenant l'union des clés de tous les poids
    all_scale_cols = set(col for pos_weights in weights.values() for col in pos_weights.keys() if col in df.columns)

    # Mise à l'échelle globale des caractéristiques
    if all_scale_cols:
        df[list(all_scale_cols)] = scaler.fit_transform(df[list(all_scale_cols)])

    # Création d'une colonne pour l'indice de performance pour éviter les erreurs lors de l'accès aux colonnes manquantes
    df['Performance Index'] = 0
    
    # Application des poids par poste aux caractéristiques normalisées
    for pos, pos_weights in weights.items():
        position_data = df[df['Pos'] == pos]
        cols_to_apply_weights = [col for col in pos_weights.keys() if col in position_data.columns]

        # Calcul de l'indice de performance pour chaque position en utilisant les caractéristiques normalisées
        for index, row in position_data.iterrows():
            df.at[index, 'Performance Index'] = sum(row[col] * weight for col, weight in pos_weights.items() if col in cols_to_apply_weights)

    # Normalisation globale de l'indice de performance entre 0 et 10
    global_min = df['Performance Index'].min()
    global_max = df['Performance Index'].max()
    if global_max > global_min:
        df['Performance Index'] = (6 * (df['Performance Index'] - global_min) / (global_max - global_min)+4)
    else:
        df['Performance Index'] = 10  # Cas où tous les indices sont identiques

    st.write("Global min:", global_min)
    st.write("Global max:", global_max)

    return df


def createPage():
    st.title("Player Score /!\ BETA")
    weights = get_weights()
    League_to_show = st.selectbox(
        "Choose the league you want :",
        ["Liga","Ligue1"],
        index=0,
        key="selectbox_league3"
    )
    # Sélection des données en fonction de la ligue
    if League_to_show == "Liga":
        df = df_player_stats_per90_liga.copy()
    elif League_to_show == "Ligue1":
        df = df_players_stats_ligue1.copy()
    data = standardize_data(weights,df)
    # Trier les données par la colonne 'Performance Index' (ordre décroissant, par exemple)
    sorted_data = data[['PlayerName', 'Team', 'Pos', 'Performance Index']].sort_values(by='Performance Index', ascending=False)

    # Afficher le DataFrame trié dans Streamlit
    st.dataframe(sorted_data)
    return True