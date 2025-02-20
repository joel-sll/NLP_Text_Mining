import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from analyse import load_restaurant_names, get_restaurant_details, get_total_reviews_for_restaurant, get_top_reviews_for_restaurant, get_sentiment_distribution_for_restaurant, get_sentiment_distribution_by_visit_context, get_monthly_review_trends, update_restaurant_coordinates
from scraping_utils import is_URL, restaurant_scraper, headers, page_parser2, parse_reviews, flatten_restaurant
import sqlite_utils

ordered_months = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]


# Fonction pour afficher les étoiles pleines en fonction de la note
def generate_stars(rating):
    full_stars = int(rating)  # Nombre d'étoiles pleines
    empty_stars = 5 - full_stars  # Compléter jusqu'à 5 étoiles
    
    stars = "⭐" * full_stars  # Afficher les étoiles pleines
    return stars


# Fonction pour afficher l'interface
def show_analyse_intra_restaurant():
    # Ajouter du CSS pour styliser le header et les informations du restaurant
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
            .restaurant-info {
                background-color: #f0f8ff;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
                color: #333;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                height:250px;
            }
            .restaurant-info p {
                margin: 5px 0;
            }
            .restaurant-info-header {
                font-size: 16px;
                color: #00e19f;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .info-icon {
                color: #00e19f;
                margin-right: 10px;
            }
            .info-label {
                font-weight: bold;
            }
            .tendance-bloc{
                background-color: #e6e6e6;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                font-family: 'New Icon';
                height: 200px;
            }
            .avis-selected-bloc{
                background-color: #e6e6e6;
                font-family: 'New Icon';
                height: 200px;
            }
            .kpi-block {
                background: linear-gradient(145deg, #e6e6e6, #ffffff);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); 
                margin-top:100px;
                text-align: center;
                color: #333;
                font-family: ''New Icon';
                width: 300px;
                height: 180px;
                overflow: hidden;
                box-sizing: border-box;
            }
            .kpi-text {
                font-size: 18px;
                font-weight: bold;
                color: #00e19f;
                margin-bottom: 10px;
            }
            .kpi-number {
                font-size: 30px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            .kpi-stars {
                font-size: 25px;
                color: #f1c40f;
            }
            .kpi-like {
                font-size: 16px;
            }

            .comments-header {
                font-size: 20px;
                font-weight: bold;
                color: #e75480;
                margin-bottom: 15px;
            }
            .comment {
                font-size: 16px;
                margin-top:10px;
                margin-bottom: 10px;
                padding: 10px;
                background-color: #e6e6e6;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .comment strong {
                font-size: 1.2em;
                color: #333;
            }
            .comment i {
                color: #ffba08; /* Jaune pour la note */
                font-style: normal;
                margin-top: 10px;
                display: inline-block;
        </style>
    """, unsafe_allow_html=True)

    # Titre avec le style appliqué
    st.markdown('<div class="header">Analyse Intra-Restaurant</div>', unsafe_allow_html=True)

    # Créer trois colonnes horizontales
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # Première colonne : Liste déroulante des restaurants
    with col1:
        restaurant_names = load_restaurant_names()  # Appeler la fonction depuis analyse.py

        st.markdown('</br>', unsafe_allow_html=True)

        selected_restaurant_name = st.selectbox("Choisissez un restaurant", restaurant_names)

        # Récupérer les détails du restaurant sélectionné
        restaurant_details = get_restaurant_details(selected_restaurant_name)
        
        type_cuisines = restaurant_details['CUISINES'] if len(restaurant_details['CUISINES']) != 0 else "Non renseigné"

        # Afficher les détails sous le restaurant sélectionné
        col1.markdown(f"""
        <div class="restaurant-info">
            <div class="restaurant-info-header">{restaurant_details['RESTAURANT_NAME']}</div>
            <p><span class="info-icon">📍</span><span class="info-label">Adresse :</span> {restaurant_details['ADDRESS']}</p>
            <p><span class="info-icon">📮</span><span class="info-label">Code Postal :</span> {restaurant_details['POSTAL_CODE']}</p>
            <p><span class="info-icon">🍽️</span><span class="info-label">Type de Cuisine :</span> {type_cuisines}</p>
        </div>
        """, unsafe_allow_html=True)

    # Deuxième colonne : Bloc KPI 1 (affichage de la note moyenne avec étoiles)
    with col2:
        # Affichage du KPI 1 avec un style amélioré
        st.markdown('</br>', unsafe_allow_html=True)
        url_to_scrape = st.text_input("URL to scrape", placeholder="http://www.tripadvisor.com")
        col2.markdown(f"""
            <div class="restaurant-info">
                <div class="kpi-text">Note moyenne</div>
                <div class="kpi-number">{restaurant_details['AVERAGE_RATING']}</div>
                <div class="kpi-stars">{generate_stars(restaurant_details['AVERAGE_RATING'])}</div>
            </div>
        """, unsafe_allow_html=True)


    # Troisième colonne : Bloc KPI 2 (affichage du nombre total d'avis)
    with col3:
        # Récupérer le nombre total d'avis pour le restaurant
        total_reviews = get_total_reviews_for_restaurant(selected_restaurant_name)

        # Récupérer la distribution des sentiments
        sentiment_distribution = get_sentiment_distribution_for_restaurant(selected_restaurant_name)
        positif = sentiment_distribution['Positif']
        neutre = sentiment_distribution['Neutre']
        negatif = sentiment_distribution['Négatif']
        
        col3_1, col3_2 = st.columns(2)
        with col3_1:
            st.markdown('<div style="height: 36px;"></div>', unsafe_allow_html=True)
            start_scraping = st.button("start scraping")
        with col3_2:
            scraping_status = st.empty()
        # Affichage du KPI 2
        st.markdown('</br>', unsafe_allow_html=True)
        
        #st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        col3.markdown(f"""
            <div class="restaurant-info">
                <div class="kpi-text">Nombre total d'avis</div>
                <div class="kpi-number">{total_reviews}</div>
                <div class="kpi-like">
                    <span class="info-icon" style="color: #2ecc71;">🟢</span>{positif}
                    <span class="info-icon" style="color: #f39c12;">⚪</span>{neutre}
                    <span class="info-icon" style="color: #e74c3c;">🔴</span>{negatif}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        # Affichage du KPI 3 avec un style amélioré
        st.markdown('</br>', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 84px;"></div>', unsafe_allow_html=True)
        col4.markdown(f"""
            <div class="restaurant-info">
                <div class="kpi-text">Fourchette de prix</div>
                <div class="kpi-number">{restaurant_details["PRICE_RANGE"]}</div>
            </div>
        """, unsafe_allow_html=True)



    # Ajouter les blocs horizontaux
    left_col, right_col = st.columns([1, 1])

    # Bloc gauche : Meilleurs commentaires
    with left_col:
        st.markdown(""" 
                <div class="comments-header">Meilleurs Commentaires</div>
        """, unsafe_allow_html=True)
        
        # Récupérer les top 3 des commentaires
        top_reviews = get_top_reviews_for_restaurant(restaurant_details['ID_RESTAURANT'])
        
        for review in top_reviews:
            st.markdown(f"""
            <div class="comment">
                <strong>🗨️ {review['title']}</strong><br>
                {review['body']}<br>
                <i>{generate_stars(review['score'])}</i>
            </div>
            """, unsafe_allow_html=True)
   
    # Bloc droit : Distribution des sentiments
    with right_col:
        st.markdown(""" 
            <div class="comments-header">Distribution des Commentaires par Sentiment</div>
        """, unsafe_allow_html=True)

        # Données pour le graphique
        sentiment_distribution = get_sentiment_distribution_for_restaurant(selected_restaurant_name)
        labels = ['Positif', 'Neutre', 'Négatif']
        sizes = [sentiment_distribution['Positif'], sentiment_distribution['Neutre'], sentiment_distribution['Négatif']]
        colors = ['#28a745', '#ffc107', '#dc3545']  # Couleurs plus douces : vert clair, orange clair, rouge clair

        # Créer le graphique interactif
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=sizes,
            marker=dict(colors=colors),  # Définir les couleurs
            hoverinfo="label+value",  # Affiche le label et la valeur au survol
            textinfo="percent",  # Affiche le pourcentage sur le graphique
            hole=0.4  # Ajoute un trou pour créer un graphique en anneau
        )])

        # Ajouter un titre dans la zone du graphique (à l'intérieur de la zone du graphique)
        fig.update_layout(
        title=f"<span>🍽️</span>{restaurant_details['RESTAURANT_NAME']}",
        title_x=0.5,  # Centrer le titre horizontalement
        title_y=0.95,  # Placer le titre un peu plus haut dans la zone
        title_xanchor='center',  # Ancrer le titre au centre horizontalement
        title_yanchor='top',  # Ancrer le titre en haut verticalement
        title_font=dict(
            size=24,
            color="#333",  # Couleur du titre
            family="New Icon"
        ),
        margin=dict(t=60)  # Ajouter un peu d'espace pour le titre
        )

        st.plotly_chart(fig, use_container_width=True)

    

 
    # Ajouter le bloc de tendance des avis par année et par mois

    with st.container():
        st.markdown("""
                    <br>
                    <div class="comments-header" style="text-align:center;">Analyse des Tendances des Avis</div>

        """, unsafe_allow_html=True)
        # Filtres pour l'année et le mois
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Année", options=list(range(2015, 2026)), index=2)  # 2017 est à l'index 2 (index 0 = 2015)
        with col2:
                month = None  # Mois est fixé à "Tous"
                st.selectbox("Mois", options=["Tous"], index=0, disabled=True)
        # Appeler la fonction pour récupérer les données
        trends_data = get_monthly_review_trends(selected_restaurant_name, year, month)
        for month in ordered_months:
            if month not in trends_data["REVIEW_MONTH"].values:
                trends_data = pd.concat([trends_data, pd.DataFrame({"REVIEW_MONTH": [month], "average_score": [0], "n_review": [0]})], ignore_index=True)
        
        trends_data["month_idx"] = trends_data["REVIEW_MONTH"].apply(lambda x:ordered_months.index(x))
        trends_data = trends_data.sort_values("month_idx")       
        
        #print(trends_data.head())


        # Afficher le graphique
        if not trends_data.empty:
            fig = go.Figure()

            # Add number of reviews as bar trace
            fig.add_trace(go.Bar(
                x=trends_data['REVIEW_MONTH'].astype(str),
                y=trends_data['n_review'],
                name='Number of Reviews',
                yaxis='y1',  # Associate this trace with the first y-axis
                marker_color='blue'
            ))

            # Add average score as line trace
            fig.add_trace(go.Scatter(
                x=trends_data['REVIEW_MONTH'].astype(str),
                y=trends_data['average_score'],
                name='Average Score',
                mode='lines+markers',
                line=dict(color='orange'),
                yaxis='y2'  # Associate this trace with the second y-axis
            ))

            # Update layout to include two y-axes
            fig.update_layout(
                title='Number of Reviews and Average Score per Month',
                xaxis_title='Month',
                yaxis_title='Number of Reviews',
                yaxis2=dict(
                    title='Average Score',
                    overlaying='y',
                    side='right',
                    range=[0,5]
                ),
                barmode='group',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour les filtres sélectionnés.")
    






    
    if url_to_scrape and start_scraping:
        if is_URL(url_to_scrape):
            # restaurant_scraper(url_to_scrape, "./data", headers=headers)
            scraping_status.markdown("Scraping in progress...")
            restaurant = page_parser2(url_to_scrape, header=headers, review_parsing= True)
            flattened_restaurant = flatten_restaurant(restaurant)
            df = pd.DataFrame.from_dict(flattened_restaurant, orient='index').transpose()
            db_tripadvisor = sqlite_utils.DButils(path="./", filename="tripadvisor.db", exists_ok=True)
            db_tripadvisor.insert_restaurant(df)
            update_restaurant_coordinates()
            scraping_status.markdown(f"Scraping done.")