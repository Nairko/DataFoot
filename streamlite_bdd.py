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
#import streamlit_authenticator as stauth


df_players_stats_ligue1,df_teams_ligue1,df_player_stats_per90_liga,df_teams_liga,df_big5 = load_data()
v_menu=["Home", "GraphPlot📈", "PizzaPlot🕸️", "Scout🔎", "Score", "PassingMap"]

with st.sidebar:
    

    #st.header("MULTPAGE WITH OPTION MENU")

    selected = option_menu(
        menu_title="Main Menu",  # required
        options=v_menu,  # required
        icons=None,  # optional
        menu_icon="dribbble",  # optional
        default_index=0,  # optional
    )
    """
    [![LinkedIn](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/nathan-correger-b99140263)
    """,
    unsafe_allow_html=True
    

if selected=="Home":
    createHomePage()

if selected=="GraphPlot📈":
    createPlotPage()

if selected=="PizzaPlot🕸️":
    createPizzaPage()

if selected=="Scout🔎":
    createScoutPage()

if selected=="Score":
    createScorePage()

if selected=="PassingMap":
    createPassingMapPage()


