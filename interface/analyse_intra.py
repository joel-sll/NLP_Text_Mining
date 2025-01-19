import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from analyse import load_restaurant_names, get_restaurant_details, get_total_reviews_for_restaurant, get_top_reviews_for_restaurant, get_sentiment_distribution_for_restaurant, get_sentiment_distribution_by_visit_context, get_monthly_review_trends, update_restaurant_coordinates, generate_wordcloud
from scraping_utils import is_URL, restaurant_scraper, headers, page_parser2, parse_reviews, flatten_restaurant
import sqlite_utils

ordered_months = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]

# Function to generate star ratings based on the given rating value
def generate_stars(rating):
    full_stars = int(rating)
    stars = "⭐" * full_stars
    return stars

def show_analyse_intra_restaurant():
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
            .kpi-block{
                background-color: #f0f8ff;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
                color: #333;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                height:180px;
                margin-top:150px;
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

            .kpi-text {
                font-size: 18px;
                font-weight: bold;
                color: #00e19f;
                margin-bottom: 10px;
                text-align:center;
            }
            .kpi-number {
                font-size: 30px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
                text-align:center;
            }
            .kpi-stars {
                font-size: 25px;
                color: #f1c40f;
                text-align:center;
            }
            .kpi-like {
                font-size: 16px;
                text-align:center;
            }

            .comments-header {
                font-size: 20px;
                font-weight: bold;
                color: #e75480;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .comments-header-bis {
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

    st.markdown('<div class="header">Analyse Intra-Restaurant</div>', unsafe_allow_html=True)

    # Container for scrapping new restaurant
    with st.container():
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown(""" <div class="comments-header-bis">Ajouter un nouveau restaurant</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 1, 2])
        with col1:
            url_to_scrape = st.text_input("Veuillez enter un URL", placeholder="http://www.tripadvisor.com")
        with col2:
            st.markdown('<br>', unsafe_allow_html=True)
            start_scraping = st.button("Start Scraping")
        with col3:
            scraping_status = st.empty()



    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        restaurant_names = load_restaurant_names()

        st.markdown('</br>', unsafe_allow_html=True)
        st.markdown(""" <div class="comments-header-bis">Tous les restaurants</div>""", unsafe_allow_html=True)

        selected_restaurant_name = st.selectbox("Choisissez un restaurant", restaurant_names)

        restaurant_details = get_restaurant_details(selected_restaurant_name)
        type_cuisines = restaurant_details['CUISINES'] if len(restaurant_details['CUISINES']) != 0 else "Non renseigné"

        col1.markdown(f"""
        <div class="restaurant-info">
            <div class="restaurant-info-header">{restaurant_details['RESTAURANT_NAME']}</div>
            <p><span class="info-icon">📍</span><span class="info-label">Adresse :</span> {restaurant_details['ADDRESS']}</p>
            <p><span class="info-icon">📮</span><span class="info-label">Code Postal :</span> {restaurant_details['POSTAL_CODE']}</p>
            <p><span class="info-icon">🍽️</span><span class="info-label">Type de Cuisine :</span> {type_cuisines}</p>
        </div>
        """, unsafe_allow_html=True)

    # KPI Average rating
    with col2:
        st.markdown('</br>', unsafe_allow_html=True)
        col2.markdown(f"""
            <div class="kpi-block">
                <div class="kpi-text">Note moyenne</div>
                <div class="kpi-number">{restaurant_details['AVERAGE_RATING']}</div>
                <div class="kpi-stars">{generate_stars(restaurant_details['AVERAGE_RATING'])}</div>
            </div>
        """, unsafe_allow_html=True)


    # KPI Number of reviews
    with col3:
        total_reviews = get_total_reviews_for_restaurant(selected_restaurant_name)

        sentiment_distribution = get_sentiment_distribution_for_restaurant(selected_restaurant_name)
        positif = sentiment_distribution['Positif']
        neutre = sentiment_distribution['Neutre']
        negatif = sentiment_distribution['Négatif']
        
        st.markdown('</br>', unsafe_allow_html=True)
        col3.markdown(f"""
            <div class="kpi-block">
                <div class="kpi-text">Nombre total d'avis</div>
                <div class="kpi-number">{total_reviews}</div>
                <div class="kpi-like">
                    <span class="info-icon" style="color: #2ecc71;">🟢</span>{positif}
                    <span class="info-icon" style="color: #f39c12;">⚪</span>{neutre}
                    <span class="info-icon" style="color: #e74c3c;">🔴</span>{negatif}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # KPI Price Range
    with col4:
        st.markdown('</br>', unsafe_allow_html=True)
        col4.markdown(f"""
            <div class="kpi-block">
                <div class="kpi-text">Fourchette de prix</div>
                <div class="kpi-number">{restaurant_details["PRICE_RANGE"]}</div>
            </div>
        """, unsafe_allow_html=True)


    left_col, right_col = st.columns([1, 1])

    # Top 3 best comments
    with left_col:
        st.markdown(""" <div class="comments-header-bis">Meilleurs Commentaires</div>""", unsafe_allow_html=True)
    
        top_reviews = get_top_reviews_for_restaurant(restaurant_details['ID_RESTAURANT'])
        
        for review in top_reviews:
            st.markdown(f"""
            <div class="comment">
                <strong>🗨️ {review['title']}</strong><br>
                {review['body']}<br>
                <i>{generate_stars(review['score'])}</i>
            </div>
            """, unsafe_allow_html=True)
   
    # Plot sentiment distribution
    with right_col:
        st.markdown("""<div class="comments-header">Distribution des Commentaires par Sentiment</div>""", unsafe_allow_html=True)

        sentiment_distribution = get_sentiment_distribution_for_restaurant(selected_restaurant_name)
        labels = ['Positif', 'Neutre', 'Négatif']
        sizes = [sentiment_distribution['Positif'], sentiment_distribution['Neutre'], sentiment_distribution['Négatif']]
        colors = ['#28a745', '#ffc107', '#dc3545']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=sizes,
            marker=dict(colors=colors),
            hoverinfo="label+value",
            textinfo="percent",
        )])

        fig.update_layout(
        title=f"<span>🍽️</span>{restaurant_details['RESTAURANT_NAME']}",
        title_x=0.5,
        title_y=0.95,
        title_xanchor='center',
        title_yanchor='top',
        title_font=dict(
            size=24,
            color="#333",
            family="New Icon"
        ),
        margin=dict(t=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Tendance analysis
    with st.container():
        st.markdown("""<br><div class="comments-header" style="text-align:center;">Analyse des Tendances des Avis</div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Année", options=list(range(2015, 2026)), index=2)
        with col2:
                month = None
                st.selectbox("Mois", options=["Tous"], index=0, disabled=True)

        trends_data = get_monthly_review_trends(selected_restaurant_name, year, month)
        for month in ordered_months:
            if month not in trends_data["REVIEW_MONTH"].values:
                trends_data = pd.concat([trends_data, pd.DataFrame({"REVIEW_MONTH": [month], "average_score": [0], "n_review": [0]})], ignore_index=True)
        
        trends_data["month_idx"] = trends_data["REVIEW_MONTH"].apply(lambda x:ordered_months.index(x))
        trends_data = trends_data.sort_values("month_idx")       

        if not trends_data.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=trends_data['REVIEW_MONTH'].astype(str),
                y=trends_data['n_review'],
                name='Number of Reviews',
                yaxis='y1', 
                marker_color='blue'
            ))

            # Add average score as line trace
            fig.add_trace(go.Scatter(
                x=trends_data['REVIEW_MONTH'].astype(str),
                y=trends_data['average_score'],
                name='Average Score',
                mode='lines+markers',
                line=dict(color='orange'),
                yaxis='y2'
            ))

            # Add number of reviews
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
    
    # Scraping logic (initiated when the button is clicked)
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


    # Sentiment by visit context analysis
    with st.container():
        st.markdown(""" <div class="comments-header">Distribution des Sentiments des Avis par Contexte</div>""", unsafe_allow_html=True)

        sentiment_distribution_by_context = get_sentiment_distribution_by_visit_context(selected_restaurant_name)

        fig = go.Figure()

        for context, sentiment_data in sentiment_distribution_by_context.items():
            fig.add_trace(go.Bar(
                y=['Positif', 'Neutre', 'Négatif'],
                x=[sentiment_data['Positif'], sentiment_data['Neutre'], sentiment_data['Négatif']],
                name=context.capitalize(),
                orientation='h',
                marker=dict(color='#4da8da' if context == 'couples' else 
                        '#376fa2' if context == 'friends' else 
                        '#ffcb4d' if context == 'family' else 
                        '#6cd4b4' if context == 'business' else 
                        '#9ea9b8'),
            ))

        fig.update_layout(
            title=f"<span>🍽️</span>{restaurant_details['RESTAURANT_NAME']}",
            title_x=0.4,
            barmode='stack',
            xaxis_title="Nombre d'Avis",
            yaxis_title="Sentiment",
            title_font=dict(size=20, color="black", family="New Icon"),
            plot_bgcolor='#e6e6e6',
            paper_bgcolor='#e6e6e6',
            margin=dict(t=60, b=30, l=30, r=30),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown(""" <div class="comments-header-bis">Wordcloud pour les avis positifs</div>""", unsafe_allow_html=True)
        if st.button("Afficher le wordcloud"):
            st.markdown(f"""
                <div style="font-size: 24px;  font-weight: bold; font-family: New Icon">
                    🍽️ {selected_restaurant_name}
                </div>
            """, unsafe_allow_html=True)
            generate_wordcloud(selected_restaurant_name)


    