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

df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()
df_xg_permatch_ligue1 = df_teams_ligue1.copy()
df_xg_permatch_liga = df_teams_liga.copy()

df_xg_permatch_ligue1['xG_per_match']= df_xg_permatch_ligue1['xG']/df_xg_permatch_ligue1['MP']
df_xg_permatch_ligue1['xGA_per_match']= df_xg_permatch_ligue1['xGA']/df_xg_permatch_ligue1['MP']
df_xg_permatch_liga['xG_per_match']= df_xg_permatch_liga['xG']/df_xg_permatch_liga['MP']
df_xg_permatch_liga['xGA_per_match']= df_xg_permatch_liga['xGA']/df_xg_permatch_liga['MP']
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
    st.markdown("**The site is in BETA.**")
    st.markdown("**Dont forget to give me feedback with the stars on the left or dm me on X : nathan_crgr**")
    st.markdown("**Here are the different menus:**")
    multi = """
    **GraphPlot📈:** You will find a scatter plot representing players' performance based on certain statistics that you can select. The stats correspond to those of the domestic leagues in the 5 major championships(at least 630min played).

    **PizzaPlot🕸️:** Displays percentile statistics in a radar chart. You can choose different stats to display as well as the player's role. Available only in 2 leagues (La Liga and Ligue 1).

    **PercentileRank:** Discover the player's top percentile stats. Is he the best in the Big 5 major championships (at least 630min played) ?

    **Scout🔎:** Enter the name of the player you want to scout; it will provide you with their weaknesses and complementary players. Available only in 2 leagues (La Liga and Ligue 1).

    **Score🥇:** Players' scores in their league (under development). Available only in 2 leagues (La Liga and Ligue 1).

    **PassingMap⚽️:** Displays passes and players' average positioning during the Strasbourg - Reims match.
    """
    st.markdown(multi)

    st.markdown("**You can try a Squad graph plot here:**")
    dfligue = pd.DataFrame({'Ligue to show':["Liga","Ligue1"]})
    ligue_select = st.selectbox("Choose the graph to display :",dfligue['Ligue to show'],index=None)

    dfselect = pd.DataFrame({'choix':["GF & GA"]})
    graph_select = st.selectbox("Choose the graph to display :",dfselect['choix'],index=None)

    # Créer des colonnes pour afficher les graphiques côte à côte
    col1, col2 = st.columns(2)

    if ligue_select == 'Ligue1':
        if graph_select == "GF & GA":
            #courbe xG vs xGA
            x2 = df_xg_permatch_ligue1['xG_per_match']
            y2 = df_xg_permatch_ligue1['xGA_per_match']
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
            x2 = df_xg_permatch_liga['xG_per_match']
            y2 = df_xg_permatch_liga['xGA_per_match']
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



    return True
