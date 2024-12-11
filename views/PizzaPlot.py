import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from PIL import Image
from mplsoccer import PyPizza, add_image, FontManager
from urllib.request import urlopen
import mysql.connector
from data_loader import load_data


df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga = load_data()



def PizzaColor(sorted_params,values,player,order_col):
        # Définir les catégories avec les statistiques correspondantes
    categories = {
        "offensif": [
            '90s','Non_Penalty_Goals', 'npxG_Non_Penalty_xG', 'Shots_Total',
            'Assists', 'xAG_Exp_Assisted_Goals','Touches_Att_Pen'
        ],
        "defensif": [
            'Tackles', 'Interceptions', 'Blocks', 'Clearances', 'Aerials_Won'
        ],
        "créateur": [
            'Shot_Creating_Actions', 'Passes_Attempted', 'Progressive_Passes',
            'Progressive_Carries', 'Successful_Take_Ons','Progressive_Passes_Rec', 'Pass_Completion_Percentage'
        ],
    }

    # Créer des dictionnaires pour chaque catégorie sélectionnée
    selected_categories = {category: [] for category in categories}

    # Trier les paramètres sélectionnés dans les catégories correspondantes
    for param in sorted_params:
        for category, stats in categories.items():
            if param in stats:
                selected_categories[category].append(param)

    # color for the slices and text
    slice_colors = ["#1A78CF"] * len(selected_categories['offensif'])  + ["#FF9300"] * len(selected_categories['créateur'])  + ["#D70232"] * len(selected_categories['defensif']) 
    text_colors = ["#000000"] * (len(selected_categories['offensif'])+len(selected_categories['créateur'])) + ["#F2F2F2"] * len(selected_categories['defensif']) 

    # instantiate PyPizza class
    baker = PyPizza(
        params=sorted_params,                  # list of parameters
        background_color="#222222",     # background color
        straight_line_color="#000000",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_color="#000000",    # color for last line
        last_circle_lw=1,               # linewidth of last circle
        other_circle_lw=0,              # linewidth for other circles
        inner_circle_size=20            # size of inner circle
    )

    # plot pizza
    fig, ax = baker.make_pizza(
        values,                          # list of values
        figsize=(8, 8.5),                # adjust the figsize according to your need
        color_blank_space="same",        # use the same color to fill blank space
        slice_colors=slice_colors,       # color for individual slices
        value_colors=text_colors,        # color for the value-text
        value_bck_colors=slice_colors,   # color for the blank spaces
        blank_alpha=0.4,                 # alpha for blank-space colors
        kwargs_slices=dict(
            edgecolor="#000000", zorder=2, linewidth=1
        ),                               # values to be used when plotting slices
        kwargs_params=dict(
            color="#F2F2F2", fontsize=11,
            va="center"
        ),                               # values to be used when adding parameter labels
        kwargs_values=dict(
            color="#F2F2F2", fontsize=11,
            zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        )                                # values to be used when adding parameter-values labels
    )

    # add title
    fig.text(
        0.515, 0.975, player, size=16,
        ha="center",color="#F2F2F2"
    )

    # add subtitle
    fig.text(
        0.515, 0.952,
        "Percentile Rank vs Current League same position | Season 2024-25",
        size=13,
        ha="center",color="#F2F2F2"
    )

    # add credits
    CREDIT_1 = "data: viz fbref"
    CREDIT_2 = "inspired by: Nathan"

    fig.text(
        0.99, 0.02, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        color="#F2F2F2",
        ha="right"
    )

    # add text
    fig.text(
        0.34, 0.925, "Attacking     Possession     Defending", size=14,
        color="#F2F2F2"
    )

    # add rectangles
    fig.patches.extend([
        plt.Rectangle(
            (0.31, 0.9225), 0.025, 0.021, fill=True, color="#1a78cf",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.462, 0.9225), 0.025, 0.021, fill=True, color="#ff9300",
            transform=fig.transFigure, figure=fig
        ),
        plt.Rectangle(
            (0.632, 0.9225), 0.025, 0.021, fill=True, color="#d70232",
            transform=fig.transFigure, figure=fig
        ),
    ])

    with order_col:
        st.pyplot(fig)
        
def createPage():
    Player1, Player2, values_p1, values_p2 = None, None, None, None
    st.write("""
    # PIZZAPLOT 🕸️
    """)
    League_to_show = st.selectbox(
        "Choose the league you want :",
        ["Liga","Ligue1"],
        index=0,
        key="selectbox_league"
    )
    if League_to_show == "Liga":
        df = df_player_stats_per90_liga
    elif League_to_show == "Ligue1":
        df = df_players_stats_ligue1

    stats_list = [
            '90s','Non_Penalty_Goals','npxG_Non_Penalty_xG','Shots_Total','Assists','xAG_Exp_Assisted_Goals',
            'Shot_Creating_Actions','Passes_Attempted','Pass_Completion_Percentage','Progressive_Passes',
            'Progressive_Carries','Successful_Take_Ons','Touches_Att_Pen','Progressive_Passes_Rec',
            'Tackles','Interceptions','Blocks','Clearances','Aerials_Won'
        ]
    params = st.multiselect("Choose the stats you whant to show",[
            '90s','Non_Penalty_Goals','npxG_Non_Penalty_xG','Shots_Total','Assists','xAG_Exp_Assisted_Goals',
            'Shot_Creating_Actions','Passes_Attempted','Pass_Completion_Percentage','Progressive_Passes',
            'Progressive_Carries','Successful_Take_Ons','Touches_Att_Pen','Progressive_Passes_Rec',
            'Tackles','Interceptions','Blocks','Clearances','Aerials_Won'
        ])
    
    sorted_params = sorted(params, key=lambda x: stats_list.index(x))


    df_player_stats_perpos= {}
    for Pos in df['Pos'].unique():
        df_pos = df[df['Pos'] == Pos].copy()  
        for param in sorted_params:     
            if param in df_pos.columns:  # Vérifier que le paramètre existe dans les colonnes
                df_pos[f"{param}_percentile"] = df_pos[param].rank(pct=True)*100       
        # Ajouter le DataFrame filtré avec les percentiles au dictionnaire
        df_player_stats_perpos[Pos] = df_pos


    position = st.selectbox(
        "Choose the role to show :",
        df['Pos'].unique(),
        index=None,
        key="selectbox_poste"  # Ajout d'une clé unique
    )
    if position == "FW" or position == "AM" or position == "FB" or position == "MF" or position == "CB":
        df_percentille_pos = df_player_stats_perpos[position]
        columns_to_keeppercentille = [col for col in df_percentille_pos.columns if '_percentile' in col]
        columns_to_keep = ['PlayerName'] + columns_to_keeppercentille
        df_filtered = df_percentille_pos[columns_to_keep]
        Player1 = st.selectbox("Player 1 :",df_percentille_pos['PlayerName'].sort_values().unique(),index=None)
        Player2 = st.selectbox("Player 2 :",df_percentille_pos['PlayerName'].sort_values().unique(),index=None)
        print(Player2)
        col5, col6 = st.columns(2)
        if Player1 is not None:
            df_percentille_Player1 = df_filtered[df_filtered['PlayerName'] == Player1]
            values_p1 = df_percentille_Player1[columns_to_keeppercentille].iloc[0].round(1).tolist()
            PizzaColor(sorted_params,values_p1,Player1,col5)
        if Player2 is not None:
            df_percentille_Player2 = df_filtered[df_filtered['PlayerName'] == Player2]
            values_p2 = df_percentille_Player2[columns_to_keeppercentille].iloc[0].round(1).tolist()  # Convertir en liste
            PizzaColor(sorted_params,values_p2,Player2,col6)

    return True

