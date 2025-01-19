import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

with st.sidebar:

    st.image("assets/images/logo.png", use_container_width=True)

    selected = option_menu(
        "", 
        ["Accueil", "Analyse intra-restaurant", "Analyse inter-restaurant", "Carte"],  # Options de menu
        icons=["house", "graph-up", "bar-chart-steps", "map-fill"],
        menu_icon="none",
    )

if selected == "Accueil":
    import accueil
    accueil.show_accueil()
elif selected == "Analyse intra-restaurant":
    import analyse_intra
    analyse_intra.show_analyse_intra_restaurant()
elif selected == "Analyse inter-restaurant":
    import analyse_inter
    analyse_inter.show_analyse_inter_restaurant()
elif selected == "Carte":
    import carte
    carte.show_carte()
