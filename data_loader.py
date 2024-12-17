import mysql.connector
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
    host="scoutfootdb.cd82ma8imdy4.eu-west-3.rds.amazonaws.com",      # Hôte de la base de données
    user=st.secrets["db_username"],           # Nom d'utilisateur MySQL
    password=st.secrets["db_password"],  # Mot de passe MySQL
    database="SoccerDB"        # Nom de la base de données
    )

    cursor = conn.cursor()

    # Récupérer les données
    query = "SELECT * FROM ligue1_playerper90allstats where Min > 400"
    df_players_stats_ligue1 = pd.read_sql(query, conn)

    query2 = "SELECT * FROM ligue1_stats order by `Rank`"
    df_teams_ligue1 = pd.read_sql(query2, conn)

    query3 = "SELECT * FROM liga_playerper90allstats where Min > 400"
    df_player_stats_per90_liga = pd.read_sql(query3, conn)

    query4 = "SELECT * FROM liga_stats order by `Rank`"
    df_teams_liga = pd.read_sql(query4, conn)

    query5 = "SELECT * FROM player_2025_big5"
    df_big5 = pd.read_sql(query5, conn)

    # Fermer la connexion
    conn.close()
    return df_players_stats_ligue1, df_teams_ligue1, df_player_stats_per90_liga, df_teams_liga,df_big5
