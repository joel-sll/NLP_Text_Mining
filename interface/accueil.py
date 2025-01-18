

import streamlit as st
from PIL import Image
from analyse import get_average_rating_per_restaurant, get_top_5_restaurants, get_restaurant_details

def generate_stars(rating):
    full_stars = int(rating)  # Nombre d'étoiles pleines
    return "⭐" * full_stars  # Seulement des étoiles pleines

def show_accueil():
    # Lien vers le fichier CSS externe
    st.markdown("""
    <link rel="stylesheet" href="assets/css/style_accueil.css">
    """, unsafe_allow_html=True)

    # Chargement des images
    image_path1 = 'assets/images/lyon1.jpg'
    image1 = Image.open(image_path1)

    image_path2 = 'assets/images/lyon3.jpg'
    image2 = Image.open(image_path2)

    image_path3 = 'assets/images/lyon4.jpg'
    image3 = Image.open(image_path3)
    
    # Affichage du texte avec un style de header
    st.markdown("""
    <h1 class="header-text" 
        style="color:#00e19f; 
                font-size:30px;
                font-family: New Icon;
                text-align:center;">
        Découvrez les meilleurs restaurants de Lyon à travers les avis des clients
    </h1>
    """, unsafe_allow_html=True)

    # Affichage des images côte à côte
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(image1, use_container_width=True)
        st.caption("Vieux Lyon")
    with col2:
        st.image(image2, use_container_width=True)
        st.caption("Basilique de Fourvière")
    with col3:
        st.image(image3, use_container_width=True)
        st.caption("Hôtel de ville")

    # Texte en dessous du titre
    st.write("""
    Bienvenue sur l'application d'analyse des restaurants.
    Sélectionnez une option dans le menu de la barre latérale pour commencer.
    """)

    # Deux blocs horizontaux
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
            <h1 class="header-text" 
                style=" font-weight:bold;
                        font-size:20px;
                        font-family: New Icon;">
                <span style="color:black;">&#x1F374;</span> Restaurants disponibles
            </h1>
            """, unsafe_allow_html=True)

        # Utiliser la fonction importée pour récupérer les données
        average_ratings = get_average_rating_per_restaurant()

        # Création d'une liste HTML pour afficher uniquement le nom, étoiles et note
        ratings_html = "<ul>"
        for rating in average_ratings:
            stars = generate_stars(rating['Average Rating'])
            ratings_html += f"<li><strong>{rating['Restaurant Name']}</strong>: {stars} ({rating['Average Rating']}/5)</li>"
        ratings_html += "</ul>"

        # Affichage des résultats dans le div
        col_left.markdown(f"""
        <div class="bloc-gauche" style="background-color: #e6e5e5; height:1040px; padding:10px; overflow-y: auto; border-radius:10px">
            {ratings_html}
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <h1 class="header-text" 
                style=" font-weight:bold;
                        font-size:20px;
                        font-family: New Icon;">
                <span style="color:black;">&#x1F374;</span> Top 5 des Restaurants
            </h1>
        """, unsafe_allow_html=True)

        # Récupérer les 5 meilleurs restaurants
        top_5_restaurants = get_top_5_restaurants()

        for restaurant in top_5_restaurants:
            # Récupérer les détails complets du restaurant
            restaurant_details = get_restaurant_details(restaurant['Restaurant Name'])
            stars = generate_stars(restaurant['Average Rating'])
            cuisine_type = restaurant_details['CUISINES'] if len(restaurant_details['CUISINES']) != 0 else "Non renseigné"
            address = restaurant_details['ADDRESS']
            postal_code = restaurant_details['POSTAL_CODE']
            average_rating = restaurant_details['AVERAGE_RATING']

            # Création d'une carte simple
            col_right.markdown(f"""
            <div style="background-color: #e6e6e6; border-radius: 10px; padding: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px;">
                <h3 style="font-size: 18px; color: #00e19f;"><span>🍽️</span>{restaurant['Restaurant Name']}</h3>
                <p style="font-size: 14px;">Note: {average_rating}/5 {stars}</p>
                <p style="font-size: 14px;">📍 {address}, {postal_code}</p>
                <p style="font-size: 14px;">🧑‍🍳 Type de cuisine: {cuisine_type}</p>
            </div>
            """, unsafe_allow_html=True)
