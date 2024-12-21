import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from data_loader import load_data


df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()


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
        
def percentil_col():   
    stats_list = [
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
    return stats_list

def columns_to_display():
    colonnes_a_garder = [
    "Player", "Nation", "Main_Pos", "Squad", "Actual_Comp", "Age", "MP", "Starts", "Min", "90s",
    "Goals_per90_percentile",
    "xG_per90_percentile",
    "npxG_per90_percentile",
    "Assists_per_90_percentile",
    "xAG_per_90_percentile",
    "Take_Ons_Attempted_per_90_percentile",
    "Take_Ons_Succ_per_90_percentile",
    "Touches_per_90_percentile",
    "Touches_Mid_3rd_per_90_percentile",
    "Touches_Att_3rd_per_90_percentile",
    "Touches_Att_Pen_per_90_percentile",
    "Carries_per_90_percentile",
    "Total_Distance_per_90_percentile",
    "Progressive_Distance_Carried_per_90_percentile",
    "Progressive_Carries_per_90_percentile",
    "1/3_Carries_per_90_percentile",
    "Carries_Penalty_Area_per_90_percentile",
    "Miscontrols_per_90_percentile",
    "Dispossessed_per_90_percentile",
    "Progressive_Passes_Received_per_90_percentile",
    "Shot_Creating_Action_per90_percentile",
    "Goal_Creating_Action_90_percentile",
    "Passes_Total_Cmp%_percentile",
    "Passes_Short_Cmp%_percentile",
    "Passes_Medium_Cmp%_percentile",
    "Passes_Long_Cmp%_percentile",
    "Key_Passes_per_90_percentile",
    "Passes_1/3_per_90_percentile",
    "Passes_Penalty_Area_per_90_percentile",
    "Progressive_Passes_per_90_percentile",
    "Passes_Attempted_per_90_percentile",
    "Through_Balls_per_90_percentile",
    "Passes_Cmp_per_90_percentile",
    "Shots_total_per90_percentile",
    "Shots_on_target_per90_percentile",
    "Goals_per_shot_percentile",
    "Goals_per_shot_on_target_percentile",
    "Npxg_per_shot_percentile",
    "Percentage_of_Aerials_Won_percentile",
    "Fouls_Committed_per_90_percentile",
    "Interceptions_per_90_percentile",
    "Tackles_Won_per_90_percentile",
    "Penalty_Kicks_Won_per_90_percentile",
    "Ball_Recoveries_per_90_percentile",
    "Blocks_per_90_percentile",
    "Shots_Blocked_per_90_percentile",
    "Clearances_per_90_percentile"]
    return colonnes_a_garder

def bar_graph(df, Joueur, Pos):
    # Créer un graphique en barres horizontales
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = [
        'gold' if classement == 1 else 
        'silver' if classement == 2 else 
        'chocolate' if classement == 3 else 
        'skyblue'
        for classement in df['Classement']
    ]
    bars = ax.barh(df['Statistique'], df['Valeur_percentile'], color=colors, height=0.3)

    for bar, col_name in zip(bars, df['Statistique']):
        ax.text(0, bar.get_y() + bar.get_height(), 
                col_name, ha='left', va='bottom', fontsize=10, color='black')
    # Ajouter le classement sur chaque barre
    for bar, classement in zip(bars, df['Classement']):
        ax.text(bar.get_width()+0.5 , bar.get_y() + bar.get_height() / 2, 
                f'#{int(classement)}', va='center', fontsize=10)

    # Ajouter les labels et le titre
    ax.set_xlabel('Percentile Value')
    ax.set_yticks([])
    # add title
    fig.text(
        0.47, 0.999999, Joueur, size=14,
        ha="center",color="black"
    )

    # add subtitle
    fig.text(
        0.47, 0.97,
        f"Percentile Rank vs Big5 Leagues same position ({Pos}) | Season 2024-25",
        size=11,
        ha="center",color="black"
    )
    #ax.set_title(f'Top 7 best percentile values of {Joueur} for {Pos} ')
    ax.set_xlim(0, 110)  # Étendre légèrement la limite pour que les textes soient visibles
    ax.invert_yaxis()  # Inverser l'axe des ordonnées pour avoir le meilleur en haut
    
    # Ajuster les marges
    plt.tight_layout()
    plt.figtext(0.99, 0.05, 'created by Nathan with FBref data', ha='right', color='grey', fontsize=10)
    plt.figtext(0.99, 0.01, 'X : @nathan.crgr', ha='right', color='grey', fontsize=10)
    # Afficher le graphique dans Streamlit
    st.pyplot(fig)

def createPage():
    st.title("Percentile Rank per pos, big 5 leagues ")
    if 'Main_Pos' not in df_big5.columns:
            df_big5[['Main_Pos', 'Secondary_Pos']] = df_big5['Pos'].apply(lambda x: pd.Series(split_position(x)))
    if 'Actual_Comp' not in df_big5.columns:
        df_big5[['Actual_Comp', 'Past_Comp']] = df_big5['Comp'].apply(lambda x: pd.Series(split_comp(x)))

    stats_list = percentil_col()
    df_player_stats_perpos= {}
    for Pos in df_big5['Main_Pos'].unique():
        df_pos = df_big5[df_big5['Main_Pos'] == Pos].copy()  
        for stat in stats_list:     
            if stat in df_pos.columns:  # Vérifier que le paramètre existe dans les colonnes
                df_pos[f"{stat}_percentile"] = df_pos[stat].rank(pct=True)*100       
            # Ajouter le DataFrame filtré avec les percentiles au dictionnaire
        df_player_stats_perpos[Pos] = df_pos

    
    Pos = st.selectbox("Choose the position of the players to display :",df_big5['Main_Pos'].unique())
    df_percentille_Posi = df_player_stats_perpos[Pos]
    colonnes_a_garder = columns_to_display()
    df_percentille_Posi = df_percentille_Posi[colonnes_a_garder]
    Playerr= st.selectbox("Choose the players to display :",df_percentille_Posi['Player'].unique())
    # Filtrer uniquement les joueurs du même poste que Yamal (exemple : FW)
    same_pos = df_percentille_Posi.loc[df_percentille_Posi['Player'] == Playerr, 'Main_Pos'].iloc[0]
    df_joueurs_meme_poste = df_percentille_Posi[df_percentille_Posi['Main_Pos'] == same_pos]

    # Extraire les colonnes percentiles
    colonnes_percentile = [col for col in df_joueurs_meme_poste.columns if col.endswith('percentile')]

    # Créer un dataframe vide pour stocker les résultats
    resultats = []

    # Calculer le classement pour chaque colonne percentile
    for col in colonnes_percentile:
        # Trier par percentile décroissant pour obtenir le classement
        df_joueurs_meme_poste['Classement'] = df_joueurs_meme_poste[col].rank(ascending=False, method='min')
        
        # Extraire la valeur percentile et le classement pour le joueur choisis
        valeur_player = df_joueurs_meme_poste.loc[df_joueurs_meme_poste['Player'] == Playerr, col].iloc[0]
        classement_player= df_joueurs_meme_poste.loc[df_joueurs_meme_poste['Player'] == Playerr, 'Classement'].iloc[0]
        
        # Ajouter les résultats dans la liste
        resultats.append({
            'Statistique': col,
            'Valeur_percentile': valeur_player,
            'Classement': classement_player
        })

    # Convertir en DataFrame
    resultat_final = pd.DataFrame(resultats)
    # Trier par classement croissant pour afficher les meilleures performances en premier
    resultat_final = resultat_final.sort_values(by='Classement')
    top_10_resultats = resultat_final.nlargest(7,'Valeur_percentile')
    bar_graph(top_10_resultats, Playerr, Pos)
    return True