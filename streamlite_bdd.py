import streamlit as st
st.set_page_config(layout="wide", page_title="Datafoot App", page_icon="⚽")
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from PIL import Image
from mplsoccer import PyPizza, add_image, FontManager
from urllib.request import urlopen
import mysql.connector
from streamlit_option_menu import option_menu
from views.PizzaPlot import createPage as createPizzaPage
from views.home import createPage as createHomePage
from views.Scout import createPage as createScoutPage
from views.score import createPage as createScorePage
from views.PassingMap import createPage as createPassingMapPage
from views.GraphPlot import createPage as createPlotPage
from data_loader import load_data
from datetime import datetime
import time
import uuid
#import streamlit_authenticator as stauth
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())
    
user_id = st.session_state["user_id"]

if "last_insert_time" not in st.session_state:
    st.session_state["last_insert_time"] = None

def can_insert(delay=300):
    """
    Vérifie si une nouvelle insertion est autorisée.
    - delay : Temps d'attente minimum entre deux insertions en secondes (par défaut : 300s = 5 minutes)
    """
    current_time = time.time()
    last_time = st.session_state["last_insert_time"]

    # Autorise l'insertion si aucune n'a été faite ou si le délai est dépassé
    if last_time is None or (current_time - last_time > delay):
        st.session_state["last_insert_time"] = current_time
        return True
    return False

df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()
v_menu=["Home", "GraphPlot📈", "PizzaPlot🕸️", "Scout🔎", "Score🥇", "PassingMap⚽️"]

with st.sidebar:
    selected_menu = option_menu(
        menu_title="Main Menu",
        options=v_menu,
        icons=None,
        menu_icon="dribbble",
        default_index=0,
    )
    sentiment_mapping = [1, 2, 3, 4, 5]
    st.markdown("Give me a feedback:")
    feedback_selected = st.feedback("stars")
    if feedback_selected is not None:
        note = sentiment_mapping[feedback_selected]
        print(note)
        if can_insert(delay=300):  # Délai de 5 minutes
            conn = mysql.connector.connect(
                host="scoutfootdb.cd82ma8imdy4.eu-west-3.rds.amazonaws.com",
                user=st.secrets["db_username"],
                password=st.secrets["db_password"],
                database="SoccerDB"
            )
            try:
                cursor = conn.cursor()

                # Requête d'insertion
                insert_query = "INSERT INTO feedback (uuid, Note) VALUES (%s,%s)"
                cursor.execute(insert_query, (user_id, note,))  # Insère uniquement la note

                # Valider la transaction
                conn.commit()

                print(f"Valeur insérée avec succès : Note = {note}")

            except mysql.connector.Error as err:
                print(f"Erreur : {err}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            st.markdown(f"You selected {sentiment_mapping[feedback_selected]} star(s).")
        else:
            st.warning("Veuillez attendre avant de donner un autre feedback.")
    st.markdown("My linkedIn link:")
    """
    [![LinkedIn](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/nathan-correger-b99140263)
    """,
    unsafe_allow_html=True
    

if selected_menu=="Home":
    createHomePage()

if selected_menu=="GraphPlot📈":
    createPlotPage()

if selected_menu=="PizzaPlot🕸️":
    createPizzaPage()

if selected_menu=="Scout🔎":
    createScoutPage()

if selected_menu=="Score🥇":
    createScorePage()

if selected_menu=="PassingMap⚽️":
    createPassingMapPage()


