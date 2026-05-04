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
from streamlit_option_menu import option_menu

from views.PizzaPlot import createPage as createPizzaPage
from views.home import createPage as createHomePage
from views.Scout import createPage as createScoutPage
from views.score import createPage as createScorePage
from views.PassingMap import createPage as createPassingMapPage
from views.GraphPlot import createPage as createPlotPage
from views.percentile_rank import createPage as createPercentilePage

from data_loader import load_data


df_players_stats_ligue1, df_teams_ligue1, df_player_stats_per90_liga, df_teams_liga, df_big5 = load_data()

v_menu = [
    "Home",
    "GraphPlot📈",
    "PizzaPlot🕸️",
    "PercentileRank",
    "Scout🔎",
    "Score🥇",
    "PassingMap⚽️"
]

with st.sidebar:
    selected_menu = option_menu(
        menu_title="Main Menu",
        options=v_menu,
        icons=None,
        menu_icon="dribbble",
        default_index=0,
    )

    st.markdown("My linkedIn link:")
    st.markdown(
        """
        [![LinkedIn](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/nathan-correger-b99140263)
        """,
        unsafe_allow_html=True
    )


if selected_menu == "Home":
    createHomePage()

if selected_menu == "GraphPlot📈":
    createPlotPage()

if selected_menu == "PizzaPlot🕸️":
    createPizzaPage()

if selected_menu == "Scout🔎":
    createScoutPage()

if selected_menu == "Score🥇":
    createScorePage()

if selected_menu == "PassingMap⚽️":
    createPassingMapPage()

if selected_menu == "PercentileRank":
    createPercentilePage()