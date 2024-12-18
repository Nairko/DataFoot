import pandas as pd
import streamlit as st
from data_loader import load_data
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

def split_position(pos):
        positions = pos.split(',')
        if len(positions) == 1:
            return positions[0], 'None'
        else:
            return positions[0], positions[1]

def split_comp(compos):
        league = compos.split('+')
        if len(league) == 1:
            return league[0], 'None'
        else:
            return league[0], league[1]
        
df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()

def columns_to_display():
     columns_list = [
    "Goals_per90",
    "xG_per90",
    "npxG_per90",
    "Assists_per_90",
    "xAG_per_90",
    "Take_Ons_Attempted_per_90",
    "Take_Ons_Succ_per_90",
    "Touches_per_90",
    "Touches_Mid_3rd_per_90",
    "Touches_Att_3rd_per_90",
    "Touches_Att_Pen_per_90",
    "Carries_per_90",
    "Total_Distance_per_90",
    "Progressive_Distance_Carried_per_90",
    "Progressive_Carries_per_90",
    "1/3_Carries_per_90",
    "Carries_Penalty_Area_per_90",
    "Miscontrols_per_90",
    "Dispossessed_per_90",
    "Progressive_Passes_Received_per_90",
    "Shot_Creating_Action_per90",
    "Goal_Creating_Action_90",
    "Passes_Total_Cmp%",
    "Passes_Short_Cmp%",
    "Passes_Medium_Cmp%",
    "Passes_Long_Cmp%",
    "Key_Passes_per_90",
    "Passes_1/3_per_90",
    "Passes_Penalty_Area_per_90",
    "Progressive_Passes_per_90",
    "Passes_Attempted_per_90",
    "Through_Balls_per_90",
    "Passes_Cmp_per_90",
    "Shots_total_per90",
    "Shots_on_target_per90",
    "Goals_per_shot",
    "Goals_per_shot_on_target",
    "Npxg_per_shot",
    "Percentage_of_Aerials_Won",
    "Fouls_Committed_per_90",
    "Interceptions_per_90",
    "Tackles_Won_per_90",
    "Penalty_Kicks_Won_per_90",
    "Ball_Recoveries_per_90",
    "Blocks_per_90",
    "Shots_Blocked_per_90",
    "Clearances_per_90"]
     return columns_list

# Fonction pour tracer le graphique
def plot_forward_analysis(df,ligue,pos,agemin,agemax,abcisse,ord):
    # Filtrage des données pour les attaquants
    if ligue != None:
        dataligue=df[df['Actual_Comp'] == ligue]
        datapos = dataligue[dataligue['Main_Pos'] == pos]
    else:
        datapos = df[df['Main_Pos'] == pos]
    filtered_data = datapos[datapos['Age'].between(agemin,agemax)]
    # Création du graphique
    fig, ax = plt.subplots(figsize=(20, 10))
    scatter = sns.scatterplot(
        data=filtered_data,
        x=abcisse,
        y=ord,
        hue="Actual_Comp",
        s=150,
        alpha=0.6,
        ax=ax
    )

    # Annotation des points par le nom du joueur
    for _, row in filtered_data.iterrows():
        ax.text(
            row[abcisse],
            row[ord],
            row['Player'],
            fontsize=10,
            color='black',
            alpha=0.7
        )

    # Titre et ajustements
    ax.set_title(f'Performance Analysis of {pos}', fontsize=15)
    plt.subplots_adjust(top=0.9)
    plt.figtext(0.90, 0.07, 'created by Nairko with FBref data', ha='right', color='grey', fontsize=13)

    # Retourner la figure
    return fig

# Fonction principale Streamlit
def createPage():

    st.title("GraphPlot Top 5 Leagues")
    col1, col2 = st.columns(2)

    # Vérification et préparation des données
    if 'Main_Pos' not in df_big5.columns:
        df_big5[['Main_Pos', 'Secondary_Pos']] = df_big5['Pos'].apply(lambda x: pd.Series(split_position(x)))
    if 'Actual_Comp' not in df_big5.columns:
        df_big5[['Actual_Comp', 'Past_Comp']] = df_big5['Comp'].apply(lambda x: pd.Series(split_comp(x)))
    columns_display = columns_to_display()
    Championnat = st.selectbox("Choose the comp to display (empty = all comp) :",df_big5['Actual_Comp'].unique(),index=None,placeholder="Let empty if you want all comp... else choose one")

    posB5 = st.selectbox("Choose the position of the players to display :",df_big5['Main_Pos'].unique())

    abscisse = st.selectbox(
    "Choose the abs axe to display",
    columns_display,)

    ordonees= st.selectbox(
    "Choose the ord axe to display",
    columns_display,)

    start_age, end_age = st.select_slider(
    "Select a range of players' ages",
    options=sorted(df_big5['Age'].dropna().unique()),  # Tri et suppression des NaN
    value=(df_big5['Age'].min(), df_big5['Age'].max())  # Intervalle par défaut
)
    # Tracer et afficher le graphique
    #with col1:
    fig = plot_forward_analysis(df_big5,Championnat,posB5,start_age,end_age,abscisse,ordonees)
    st.pyplot(fig)
    return True