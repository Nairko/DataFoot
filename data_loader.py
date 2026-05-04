from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    data_dir = Path(__file__).parent / "data_csv"

    df_players_stats_ligue1 = pd.read_csv(data_dir / "ligue1_playerper90allstats.csv")
    df_teams_ligue1 = pd.read_csv(data_dir / "ligue1_stats.csv")
    df_player_stats_per90_liga = pd.read_csv(data_dir / "liga_playerper90allstats.csv")
    df_teams_liga = pd.read_csv(data_dir / "liga_stats.csv")
    df_big5 = pd.read_csv(data_dir / "player_2025_big5.csv")

    df_players_stats_ligue1 = df_players_stats_ligue1[df_players_stats_ligue1["Min"] > 400]
    df_player_stats_per90_liga = df_player_stats_per90_liga[df_player_stats_per90_liga["Min"] > 400]

    df_teams_ligue1 = df_teams_ligue1.sort_values(by="Rank")
    df_teams_liga = df_teams_liga.sort_values(by="Rank")

    return df_players_stats_ligue1, df_teams_ligue1, df_player_stats_per90_liga, df_teams_liga, df_big5