import streamlit as st
import folium
from streamlit_folium import st_folium
from analyse import get_restaurants_with_coordinates

def show_carte():
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
            .container {
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }
            .left-block {
                background-color: #f0f8ff;
                width: 70%;
                height: 500px;  /* Ajusté pour la hauteur de la carte */
                border-radius: 10px;
                padding: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }
            .right-block {
                background-color: #ffe4e1;
                width: 28%;
                height: 500px;  /* Aligné avec la hauteur du bloc gauche */
                border-radius: 10px;
                padding: 10px;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    # Titre avec le style appliqué
    st.markdown('<div class="header">Carte interactive</div>', unsafe_allow_html=True)

    # Ajouter un espacement entre le header et la carte
    st.markdown('</br>', unsafe_allow_html=True)  # Ajoute un double saut de ligne pour créer de l'espace


    # Utiliser des colonnes pour diviser la page
    col_left, col_right = st.columns([2, 1])  # 2/3 pour la carte, 1/3 pour l'autre contenu

    with col_left:
        # Carte interactive
        restaurants = get_restaurants_with_coordinates()
        if not restaurants.empty:
            map_center = [restaurants['latitude'].mean(), restaurants['longitude'].mean()]
            m = folium.Map(location=map_center, zoom_start=12)

            # Ajouter des marqueurs avec des icônes personnalisées
            for _, row in restaurants.iterrows():
                icon = folium.Icon(icon="cutlery", prefix="fa", color="red")  # Utilise l'icône "cutlery" de FontAwesome
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=f"<b>{row['RESTAURANT_NAME']}</b>",
                    icon=icon
                ).add_to(m)

            # Intégration de la carte dans le left-block
            st_folium(m, width=700, height=500)
        else:
            st.write("Aucune donnée géographique disponible.")

    with col_right:
        st.markdown("""

            <div style="background-color:#e6e6e6; height:300px;">
                <h1 class="header-text" 
                style="font-weight:bold;
                        font-size:20px;
                        font-family: New Icon;
                        text-align:center;">
                📝 Informations du restaurant
                </h1> 
            </div>
        """, unsafe_allow_html=True)

        
