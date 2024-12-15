import streamlit as st
from data_loader import load_data
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from PIL import Image
from mplsoccer import PyPizza, add_image, FontManager
from urllib.request import urlopen

df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga = load_data()

def get_logo_path(squad_name,ligue_select):
    # Remplacez ce chemin par le chemin où vous stockez vos logos
    if ligue_select == 'Ligue1':
        return f"image/{squad_name}.png" 
    else:
        return f"image_liga/{squad_name}.png" 


def plot_with_logos(x, y, names, ax,ligue_select):
    for x0, y0, name in zip(x, y, names):
        logo_path = get_logo_path(name,ligue_select)
        img = mpimg.imread(logo_path)
        imagebox = OffsetImage(img, zoom=0.8)  # Ajustez le zoom selon la taille des logos
        ab = AnnotationBbox(imagebox, (x0, y0), frameon=False, pad=0.5)
        ax.add_artist(ab)



def createPage():
    st.write("""# Welcome to the hub of soccer data""")
    dfligue = pd.DataFrame({'Ligue to show':["Liga","Ligue1"]})
    ligue_select = st.selectbox("Choix de la ligue a afficher :",dfligue['Ligue to show'],index=None)

    dfselect = pd.DataFrame({'choix':["GF & GA"]})
    graph_select = st.selectbox("Choix du graph a afficher:",dfselect['choix'],index=None)

    # Créer des colonnes pour afficher les graphiques côte à côte
    col1, col2 = st.columns(2)

    if ligue_select == 'Ligue1':
        if graph_select == "GF & GA":
            #courbe xG vs xGA
            x2 = df_teams_ligue1['xG']/12
            y2 = df_teams_ligue1['xGA']/12
            name = df_teams_ligue1['TeamName'] 
            # plot
            fig, ax = plt.subplots(figsize=(10,10))
            # Scatter plot
            sc2 = ax.scatter(x2, y2, color='grey')  # use a neutral color for points
            # Calculate mean values
            moyennex = x2.mean()
            moyenney = y2.mean()
            #x2_line = np.linspace(min(x2.min()-4, y2.min())-4, max(x2.max(), y2.max()), 100)
            #ax.plot(x2_line, x2_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennex, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyenney, color='blue', linestyle='--')  # Horizontal line at mean xGA

            #ax.fill_between(x=[0, moyennex], y1=moyenney, color='yellow', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_between(x=[moyennex, max(x2)+2], y1=moyenney, color='green', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_betweenx(y=[moyenney,max(y2)+6], x1=moyennex, color='red', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_betweenx(y=[moyenney,max(y2)+6], x1=moyennex,x2=max(x2)+2, color='blue', alpha=0.1)  # Below avg xG and xGA

            # Annotate each point
            plot_with_logos(x2, y2, name, ax,ligue_select)

            # Set labels and legend
            ax.set_xlabel('xG')
            ax.set_ylabel('xGA')
            ax.legend(['y = x', 'Mean xG', 'Mean xGA'], loc='upper left')
            ax.set_title('Visualisation des expected goals against VS expected goals)')
            with col1 :
                st.pyplot(fig)
        #elif graph_select == "Goals":
            x = df_teams_ligue1['xG']
            y= df_teams_ligue1['Gls']
            name = df_teams_ligue1['TeamName']
            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            sc = ax.scatter(x, y)
            x_line = np.linspace(min(x.min(), y.min()), max(x.max(), y.max()), 100)
            ax.plot(x_line, x_line, color='black')  # Line plot y=x
            

            plot_with_logos(x, y, name, ax,ligue_select)
            ax.legend()
            ax.set_xlabel('xG')
            ax.set_ylabel('Goals')
            ax.set_title('Visualisation de la sur ou sous-performance des equipes (But marque VS xG)')
            with col2:
                st.pyplot(fig)
    elif ligue_select == 'Liga':
        if graph_select == "GF & GA":
            #courbe xG vs xGA
            x2 = df_teams_liga['xG']/12
            y2 = df_teams_liga['xGA']/12
            name = df_teams_liga['TeamName'] 
            # plot
            fig, ax = plt.subplots(figsize=(10,10))
            # Scatter plot
            sc2 = ax.scatter(x2, y2, color='grey')  # use a neutral color for points
            # Calculate mean values
            moyennex = x2.mean()
            moyenney = y2.mean()
            #x2_line = np.linspace(min(x2.min()-4, y2.min())-4, max(x2.max(), y2.max()), 100)
            #ax.plot(x2_line, x2_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennex, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyenney, color='blue', linestyle='--')  # Horizontal line at mean xGA

            #ax.fill_between(x=[0, moyennex], y1=moyenney, color='yellow', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_between(x=[moyennex, max(x2)+2], y1=moyenney, color='green', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_betweenx(y=[moyenney,max(y2)+6], x1=moyennex, color='red', alpha=0.1)  # Below avg xG and xGA
            #ax.fill_betweenx(y=[moyenney,max(y2)+6], x1=moyennex,x2=max(x2)+2, color='blue', alpha=0.1)  # Below avg xG and xGA

            # Annotate each point
            plot_with_logos(x2, y2, name, ax, ligue_select)

            # Set labels and legend
            ax.set_xlabel('xG')
            ax.set_ylabel('xGA')
            ax.legend(['y = x', 'Mean xG', 'Mean xGA'], loc='upper left')
            ax.set_title('Visualisation des expected goals against VS expected goals)')
            with col1 :
                st.pyplot(fig)
        #elif graph_select == "Goals":
            x = df_teams_liga['xG']
            y= df_teams_liga['Gls']
            name = df_teams_liga['TeamName']
            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            sc = ax.scatter(x, y)
            x_line = np.linspace(min(x.min(), y.min()), max(x.max(), y.max()), 100)
            ax.plot(x_line, x_line, color='black')  # Line plot y=x
            

            plot_with_logos(x, y, name, ax, ligue_select)
            ax.legend()
            ax.set_xlabel('xG')
            ax.set_ylabel('Goals')
            ax.set_title('Visualisation de la sur ou sous-performance des equipes (But marque VS xG)')
            with col2:
                st.pyplot(fig)


     
    if ligue_select == 'Ligue1':
        posl1 = st.selectbox("Choix du poste a afficher :",df_players_stats_ligue1['Pos'].unique(),index=None)
        ages = st.selectbox("Choix de l'age inferieur à afficher :",df_players_stats_ligue1['Age'].sort_values().unique(),index=None)
    elif ligue_select == 'Liga':
        pos = st.selectbox("Choix du poste a afficher :",df_player_stats_per90_liga['Pos'].unique(),index=None)
        ages = st.selectbox("Choix de l'age inferieur à afficher :",df_player_stats_per90_liga['Age'].sort_values().unique(),index=None)
        if ages == None:
            ages=50
        

    col3, col4 = st.columns(2)
    if ligue_select == 'Ligue1':
        if posl1 == "FW" or posl1 == "AM" or posl1 == "FB" or posl1 == "MF" or posl1 == "CB":
            dfposte = df_players_stats_ligue1[(df_players_stats_ligue1['Pos'].str.contains(posl1))& (df_players_stats_ligue1['Age']<=ages)]
            goals = dfposte['Non_Penalty_Goals']
            xG = dfposte['npxG_Non_Penalty_xG']
            playername = dfposte['PlayerName']

            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            # Scatter plot
            sc2 = ax.scatter(xG, goals, color='grey')  # use a neutral color for points

            # Calculate mean values
            moyennegoals = goals.mean()
            moyennexG = xG.mean()

            x3_line = np.linspace(min(xG.min(), goals.min()), max(xG.max(), goals.max()), 100)
            ax.plot(x3_line, x3_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennexG, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyennegoals, color='blue', linestyle='--')  # Horizontal line at mean xGA

            # Annotate each point
            for i, txt in enumerate(playername):
                ax.annotate(txt, (xG.iloc[i], goals.iloc[i]))

            # Set labels and legend
            ax.set_xlabel('xG')
            ax.set_ylabel('Goals')
            ax.set_title('Visualisation de la sur ou sous-performance des Joueurs ayant joué au moins 400min (But marque(per90) VS xG(per90))')
            with col3:
                st.pyplot(fig)

            assists = dfposte['Assists']
            xGA = dfposte['xAG_Exp_Assisted_Goals']
            playername = dfposte['PlayerName']

            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            # Scatter plot
            sc2 = ax.scatter(xGA, assists, color='grey')  # use a neutral color for points

            # Calculate mean values
            moyennegoals = assists.mean()
            moyennexG = xGA.mean()

            x3_line = np.linspace(min(xGA.min(), assists.min()), max(xGA.max(), assists.max()), 100)
            ax.plot(x3_line, x3_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennexG, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyennegoals, color='blue', linestyle='--')  # Horizontal line at mean xGA

            # Annotate each point
            for i, txt in enumerate(playername):
                ax.annotate(txt, (xGA.iloc[i], assists.iloc[i]))

            # Set labels and legend
            ax.set_xlabel('xAG')
            ax.set_ylabel('assists')
            ax.set_title('Visualisation de la sur ou sous-performance des Joueurs ayant joué au moins 400min (Assists(per90) VS xAG(per90))')
            with col4:
                st.pyplot(fig)
    elif ligue_select == 'Liga':
        if pos == "FW" or pos == "AM" or pos == "FB" or pos == "MF" or pos == "CB":
            dfposte = df_player_stats_per90_liga[(df_player_stats_per90_liga['Pos'].str.contains(pos))& (df_player_stats_per90_liga['Age']<=ages)]
            goals = dfposte['Non_Penalty_Goals']
            xG = dfposte['npxG_Non_Penalty_xG']
            playername = dfposte['PlayerName']

            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            # Scatter plot
            sc2 = ax.scatter(xG, goals, color='grey')  # use a neutral color for points

            # Calculate mean values
            moyennegoals = goals.mean()
            moyennexG = xG.mean()

            x3_line = np.linspace(min(xG.min(), goals.min()), max(xG.max(), goals.max()), 100)
            ax.plot(x3_line, x3_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennexG, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyennegoals, color='blue', linestyle='--')  # Horizontal line at mean xGA

            # Annotate each point
            for i, txt in enumerate(playername):
                ax.annotate(txt, (xG.iloc[i], goals.iloc[i]))

            # Set labels and legend
            ax.set_xlabel('xG')
            ax.set_ylabel('Goals')
            ax.set_title('Visualisation de la sur ou sous-performance des Joueurs ayant joué au moins 400min (But marque(per90) VS xG(per90))')
            with col3:
                st.pyplot(fig)

            assists = dfposte['Assists']
            xGA = dfposte['xAG_Exp_Assisted_Goals']
            playername = dfposte['PlayerName']

            # plot
            fig, ax = plt.subplots(figsize=(10,10))

            # Scatter plot
            sc2 = ax.scatter(xGA, assists, color='grey')  # use a neutral color for points

            # Calculate mean values
            moyennegoals = assists.mean()
            moyennexG = xGA.mean()

            x3_line = np.linspace(min(xGA.min(), assists.min()), max(xGA.max(), assists.max()), 100)
            ax.plot(x3_line, x3_line, label='y = x', color='black')  # Line plot y=x

            # Add mean lines
            ax.axvline(x=moyennexG, color='red', linestyle='--')  # Vertical line at mean xG
            ax.axhline(y=moyennegoals, color='blue', linestyle='--')  # Horizontal line at mean xGA

            # Annotate each point
            for i, txt in enumerate(playername):
                ax.annotate(txt, (xGA.iloc[i], assists.iloc[i]))

            # Set labels and legend
            ax.set_xlabel('xAG')
            ax.set_ylabel('assists')
            ax.set_title('Visualisation de la sur ou sous-performance des Joueurs ayant joué au moins 400min (Assists(per90) VS xAG(per90))')
            with col4:
                st.pyplot(fig)

    return True
