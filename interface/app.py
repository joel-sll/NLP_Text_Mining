import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

# Sidebar menu avec personnalisation
with st.sidebar:

    st.image("assets/images/logo.png", use_container_width=True)

    selected = option_menu(
        "", 
        ["Accueil", "Scrapping et Parsing", "Analyse intra-restaurant", "Analyse inter-restaurant", "Carte"],  # Options de menu
        icons=["house","terminal", "graph-up", "bar-chart-steps", "map-fill"],
        menu_icon="none",  # Icône du menu
        #default_index=0,  # Option par défaut
    )



# Afficher la page correspondant à l'option sélectionnée
if selected == "Accueil":
    import accueil
    accueil.show_accueil()
elif selected == "Scrapping et Parsing":
    import scrapping_parsing
    scrapping_parsing.show_scrapping()
elif selected == "Analyse intra-restaurant":
    import analyse_intra
    analyse_intra.show_analyse_intra_restaurant()
elif selected == "Analyse inter-restaurant":
    import analyse_inter
    analyse_inter.show_analyse_inter_restaurant()
elif selected == "Carte":
    import carte
    carte.show_carte()
