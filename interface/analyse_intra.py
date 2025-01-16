import streamlit as st
from analyse import load_restaurant_names  # Importer la fonction depuis analyse.py

# Fonction pour afficher l'interface
def show_analyse_intra_restaurant():
    # Ajouter du CSS pour styliser le header
    st.markdown("""
        <style>
            .header {
                background-color: #00e19f;
                font-family: "New Icon";
                padding: 10px;
                text-align: center;
                border-radius: 10px;
                color: white;
                font-size: 25px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Titre avec le style appliqué
    st.markdown('<div class="header">Analyse Intra-Restaurant</div>', unsafe_allow_html=True)

    # Créer trois colonnes horizontales
    col1, col2, col3 = st.columns([1, 1, 1])

    # Première colonne : Liste déroulante des restaurants
    with col1:
        st.subheader("Sélectionner un restaurant")
        restaurant_names = load_restaurant_names()  # Appeler la fonction depuis analyse.py
        selected_restaurant = st.selectbox("Choisissez un restaurant", restaurant_names)
        st.write(f"Restaurant sélectionné : {selected_restaurant}")

    # Deuxième colonne : Carte vide pour les KPI (ici, pour l'instant, juste une carte)
    with col2:
        st.subheader("KPI 1")


    # Troisième colonne : Carte vide pour le deuxième KPI
    with col3:
        st.subheader("KPI 2")



