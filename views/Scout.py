import streamlit as st
from data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from sklearn.preprocessing import StandardScaler

df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga = load_data()
def get_weights():
    return {
        'CB': {'Non_Penalty_Goals': 0.1, 'npxG_Non_Penalty_xG': 0.1, 'Shots_Total': 0.2, 'Assists': 0.2,
               'xAG_Exp_Assisted_Goals': 0.3, 'Shot_Creating_Actions': 0.2, 'Passes_Attempted': 0.4, 'Pass_Completion_Percentage': 0.7,
               'Progressive_Passes': 0.5, 'Progressive_Carries': 0.5, 'Successful_Take_Ons': 0.3, 'Touches_Att_Pen': 0.1,
               'Progressive_Passes_Rec': 0.2, 'Tackles': 0.6, 'Interceptions': 0.6, 'Blocks': 0.7,'Clearances':0.7,'Aerials_Won':0.7},
        'FB': {'Non_Penalty_Goals': 0.1, 'npxG_Non_Penalty_xG': 0.2, 'Shots_Total': 0.3, 'Assists': 0.4,
               'xAG_Exp_Assisted_Goals': 0.5, 'Shot_Creating_Actions': 0.4, 'Passes_Attempted': 0.4, 'Pass_Completion_Percentage': 0.6,
               'Progressive_Passes': 0.5, 'Progressive_Carries': 0.5, 'Successful_Take_Ons': 0.4, 'Touches_Att_Pen': 0.3,
               'Progressive_Passes_Rec': 0.5, 'Tackles': 0.6, 'Interceptions': 0.4, 'Blocks': 0.4,'Clearances':0.4,'Aerials_Won':0.6},
        'MF': {'Non_Penalty_Goals': 0.4, 'npxG_Non_Penalty_xG': 0.5, 'Shots_Total': 0.5, 'Assists': 0.5,
               'xAG_Exp_Assisted_Goals': 0.5, 'Shot_Creating_Actions': 0.5, 'Passes_Attempted': 0.7, 'Pass_Completion_Percentage': 0.8,
               'Progressive_Passes': 0.7, 'Progressive_Carries': 0.7, 'Successful_Take_Ons': 0.5, 'Touches_Att_Pen': 0.5,
               'Progressive_Passes_Rec': 0.6, 'Tackles': 0.4, 'Interceptions': 0.5, 'Blocks': 0.4,'Clearances':0.3,'Aerials_Won':0.5},
        'AM': {'Non_Penalty_Goals': 0.7, 'npxG_Non_Penalty_xG': 0.8, 'Shots_Total': 0.7, 'Assists': 0.7,
               'xAG_Exp_Assisted_Goals': 0.8, 'Shot_Creating_Actions': 0.8, 'Passes_Attempted': 0.5, 'Pass_Completion_Percentage': 0.6,
               'Progressive_Passes': 0.6, 'Progressive_Carries': 0.8, 'Successful_Take_Ons': 0.8, 'Touches_Att_Pen': 0.7,
               'Progressive_Passes_Rec': 0.7, 'Tackles': 0.1, 'Interceptions': 0.2, 'Blocks': 0.2,'Clearances':0.2,'Aerials_Won':0.3},
        'FW': {'Non_Penalty_Goals': 0.9, 'npxG_Non_Penalty_xG': 0.9, 'Shots_Total': 0.7, 'Assists': 0.7,
               'xAG_Exp_Assisted_Goals': 0.8, 'Shot_Creating_Actions': 0.8, 'Passes_Attempted': 0.4, 'Pass_Completion_Percentage': 0.5,
               'Progressive_Passes': 0.4, 'Progressive_Carries': 0.5, 'Successful_Take_Ons': 0.6, 'Touches_Att_Pen': 0.8,
               'Progressive_Passes_Rec': 0.7, 'Tackles': 0.1, 'Interceptions': 0.2, 'Blocks': 0.2,'Clearances':0.2,'Aerials_Won':0.4},

        # Ajoute d'autres postes et leurs poids ici
    }

def standardize_data(weights,df):
    
    data = df
    positions = data['Pos'].unique()
    
    scaler = StandardScaler()
    
    for pos in positions:
        position_data = data[data['Pos'] == pos]
        position_weights = weights.get(pos, {})
        
        cols_to_scale = [col for col in position_data.columns if col in position_weights]  # Seules les colonnes à pondérer
        
        # Appliquer les poids aux colonnes pertinentes
        for col in cols_to_scale:
            position_data[col] *= position_weights[col]
        
        # S'assurer que seules les colonnes à échelle sont transformées
        scaled_features = scaler.fit_transform(position_data[cols_to_scale])
        scaled_df = pd.DataFrame(scaled_features, columns=cols_to_scale, index=position_data.index)  # Utiliser cols_to_scale ici
        
        data.loc[position_data.index, cols_to_scale] = scaled_df  # Mettre à jour seulement les colonnes échelonnées
    
    return data

def find_complementary_players(data, player_name):
    player_data = data[data['PlayerName'] == player_name].iloc[0]
    # Sélectionner uniquement les colonnes numériques pour la comparaison
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    # Identifier les faiblesses (valeur < 0 après normalisation)
    weaknesses = player_data[numeric_cols][player_data[numeric_cols] < 0].index.tolist()
    st.write("### Weaknesses of the player:")
    st.write("* " + "\n* ".join(weaknesses))  # Affichage sous forme de liste à puces

    # Filtrer les joueurs qui sont forts là où le joueur spécifié est faible
    #filter_mask = data[weaknesses].apply(lambda x: x > 0).sum(axis=1) >= num_weaknesses_needed

    filters = (data[weaknesses] > 0).all(axis=1) & (data['Pos'] == player_data['Pos'])
    complementary_players = data[filters]
    if len(weaknesses)>5:
        # Définir un seuil pour le nombre de faiblesses que le joueur complémentaire doit exceller
        num_weaknesses_needed = len(weaknesses) // 1.4  # Au moins la moitié des faiblesses
        print(num_weaknesses_needed)

        # Filtrer les joueurs qui sont meilleurs dans au moins 'num_weaknesses_needed' des faiblesses
        filter_mask = data[weaknesses].apply(lambda x: x > 0).sum(axis=1) >= num_weaknesses_needed
        complementary_players = data[filter_mask & (data['Pos'] == player_data['Pos'])]
    else:
        filters = (data[weaknesses] > 0).all(axis=1) & (data['Pos'] == player_data['Pos'])
        complementary_players = data[filters]
    return complementary_players, complementary_players.index


def createPage():
    st.write("""
    # Scout Page 🔎
    """)
    League_to_show = st.selectbox(
        "Choose the league you want :",
        ["Liga","Ligue1"],
        index=0,
        key="selectbox_league2"
    )
    # Sélection des données en fonction de la ligue
    if League_to_show == "Liga":
        original_df = df_player_stats_per90_liga.copy()
    elif League_to_show == "Ligue1":
        original_df = df_players_stats_ligue1.copy()

    # Obtention des poids et standardisation des données
    weights = get_weights()
    standardized_data = standardize_data(weights, original_df.copy())  # Utiliser une copie pour la standardisation

    # Sélection du joueur
    Player = st.selectbox("Player 1 :", original_df['PlayerName'].sort_values().unique(), index=None)
    if Player is not None:
        st.write("### DataFrame of Your Player (Original):")
        st.dataframe(original_df[original_df['PlayerName'] == Player])  # Afficher les données originales du joueur

        complementary_players, indices = find_complementary_players(standardized_data, Player)
        st.write("### Complementary Players (Original Data):")
        original_complementary_players = original_df.loc[indices]
        st.dataframe(original_complementary_players)

    return True