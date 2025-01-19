import streamlit as st
import folium
from streamlit_folium import st_folium
from analyse import get_restaurants_with_coordinates, get_restaurant_details#, get_photos_for_restaurant

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

            # Ajout des marqueurs avec une interaction
            for _, row in restaurants.iterrows():
                icon = folium.Icon(icon="cutlery", prefix="fa", color="red")  # Utilise l'icône "cutlery" de FontAwesome
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row['RESTAURANT_NAME'],
                    icon=icon,
                    tooltip=row['RESTAURANT_NAME']  # Le tooltip contient le nom du restaurant
                ).add_to(m)

            # Intégration de la carte dans le left-block
            selected_marker = st_folium(m, width=700, height=500, key="map")

            # Vérification si un restaurant a été sélectionné
            if selected_marker and 'last_object_clicked_tooltip' in selected_marker:
                # Extraire le nom du restaurant à partir de 'last_object_clicked_tooltip'
                selected_restaurant_name = selected_marker['last_object_clicked_tooltip']
                if selected_restaurant_name:
                    restaurant_details = get_restaurant_details(selected_restaurant_name)
                    st.session_state.selected_restaurant = restaurant_details
                else:
                    st.write("Aucun restaurant sélectionné.")
        else:
            st.write("Aucune donnée géographique disponible.")

    with col_right:
        st.markdown("""
                    <h1 class="header-text" 
                    style="font-weight:bold;
                            font-size:20px;
                            font-family: New Icon;
                            text-align:center;">
                    📝 Informations du restaurant
                    </h1> 
            """, unsafe_allow_html=True)
        if 'selected_restaurant' in st.session_state:
            restaurant = st.session_state.selected_restaurant
            
            # HTML pour ajouter un bloc avec une couleur de fond et un peu de style
            restaurant_info = f"""
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: New Icon">
                <h3 style="color: #2a9d8f;">🏢 {restaurant['RESTAURANT_NAME']}</h3>
                <p style="font-size: 16px; color: #264653;">📍 Adresse: {restaurant['ADDRESS']}</p>
                <p style="font-size: 16px; color: #264653;">📮 Code postal: {restaurant['POSTAL_CODE']}</p>
                <p style="font-size: 16px; color: #264653;">⭐ Note moyenne: {restaurant['AVERAGE_RATING']} / 5</p>
                <p style="font-size: 16px; color: #264653;">🍽️ Cuisine: {restaurant['CUISINES']}</p>
                <p style="font-size: 16px; color: #264653;">📞 Téléphone: {restaurant.get('PHONE_NUMBER', "Non renseigné")}</p>
            </div>
            """
            # Afficher le bloc avec les informations du restaurant
            st.markdown(restaurant_info, unsafe_allow_html=True)
            

    # Nouveaux blocs en bas pour les photos
    st.markdown("<h3 style='font-weight:bold; text-align:center;'>📸 Photos du restaurant</h3>", unsafe_allow_html=True)
    photos = False
    # photos = get_photos_for_restaurant(restaurant['RESTAURANT_NAME']) if 'selected_restaurant' in st.session_state else []

    if photos:
        # Afficher les photos deux à deux horizontalement
        photo_pairs = [photos[i:i + 2] for i in range(0, len(photos), 2)]

        # Créer une ligne pour les photos
        for pair in photo_pairs:
            col1, col2 = st.columns(2)
            with col1:
                st.image(pair[0][0], caption=pair[0][1], use_container_width=True)
            if len(pair) > 1:
                with col2:
                    st.image(pair[1][0], caption=pair[1][1], use_container_width=True)
    else:
        st.write("Aucune photo disponible pour ce restaurant.")
