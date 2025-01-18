# # import streamlit as st
# # import pandas as pd
# # import matplotlib.pyplot as plt
# # import seaborn as sns
# # from nltk.corpus import stopwords
# # from nltk.sentiment import SentimentIntensityAnalyzer
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from collections import Counter
# # import re
# # import os
# # import spacy

# # # Load spaCy French model
# # nlp = spacy.load('fr_core_news_sm')

# # # Stopword setup
# # french_stopwords = set(stopwords.words('french'))
# # additional_stopwords = {'et', 'de', 'un', 'le', 'la', 'les', 'des', 'est', 'très', 'pour'}
# # french_stopwords.update(additional_stopwords)

# # @st.cache_data
# # def advanced_preprocess(text):
# #     if not isinstance(text, str):
# #         return ''
# #     text = text.lower()
# #     text = re.sub(r'http\\S+|www\\S+|https\\S+', '', text)
# #     text = re.sub(r'[^a-zA-ZÀ-ÿ\\s]', ' ', text)
# #     text = ' '.join(text.split())
# #     doc = nlp(text)
# #     tokens = [token.text for token in doc if not token.is_stop and token.text.strip()]
# #     return ' '.join(tokens)

# # def preprocess_and_save_data(input_file, output_file):
# #     """Load data, preprocess if needed, and save preprocessed results."""
# #     if os.path.exists(output_file):
# #         # Load preprocessed data
# #         return pd.read_excel(output_file)

# #     # Load original data
# #     df = pd.read_excel(input_file)
# #     if 'processed_review' not in df.columns:
# #         # Preprocess data
# #         st.info("Prétraitement des données en cours, veuillez patienter...")
# #         df['processed_review'] = df['REVIEW_BODY'].apply(advanced_preprocess)

# #         # Save preprocessed data
# #         df.to_excel(output_file, index=False)

# #     return df

# # def analyze_restaurant(restaurant_data):
# #     n_reviews = len(restaurant_data)
# #     avg_score = restaurant_data['REVIEW_SCORE'].mean()
# #     sia = SentimentIntensityAnalyzer()
# #     sentiments = restaurant_data['REVIEW_BODY'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
# #     tfidf = TfidfVectorizer(max_features=100, stop_words=list(french_stopwords))
# #     tfidf_matrix = tfidf.fit_transform(restaurant_data['processed_review'])
# #     word_freq = Counter(' '.join(restaurant_data['processed_review']).split())
# #     most_common_words = dict(word_freq.most_common(15))
# #     aspects = {
# #         'nourriture': ['plat', 'cuisine', 'nourriture', 'repas', 'menu'],
# #         'service': ['service', 'personnel', 'équipe', 'accueil'],
# #         'ambiance': ['ambiance', 'décor', 'cadre', 'atmosphère']
# #     }
# #     aspect_mentions = {aspect: 0 for aspect in aspects}
# #     for review in restaurant_data['processed_review']:
# #         for aspect, keywords in aspects.items():
# #             if any(keyword in str(review).lower() for keyword in keywords):
# #                 aspect_mentions[aspect] += 1
# #     return {
# #         'stats': {'n_reviews': n_reviews, 'avg_score': avg_score, 'aspect_mentions': aspect_mentions},
# #         'sentiments': sentiments,
# #         'word_frequencies': most_common_words
# #     }

# # def compare_restaurants(restaurant_analyses):
# #     comparison_data = {}
# #     for restaurant_name, analysis in restaurant_analyses.items():
# #         comparison_data[restaurant_name] = {
# #             'Average Score': analysis['stats']['avg_score'],
# #             'Number of Reviews': analysis['stats']['n_reviews'],
# #             'Aspect Mentions': analysis['stats']['aspect_mentions']
# #         }
# #     comparison_df = pd.DataFrame.from_dict(comparison_data, orient='index')
# #     return comparison_df

# # def visualize_restaurant_comparison(comparison_df):
# #     fig, ax = plt.subplots(figsize=(10, 6))
# #     comparison_df['Average Score'].sort_values().plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
# #     ax.set_title('Average Scores Across Restaurants')
# #     ax.set_ylabel('Average Score')
# #     ax.set_xticklabels(comparison_df.index, rotation=45)
# #     st.pyplot(fig)

# # # Streamlit App
# # def show_analyse_inter_restaurant():
# #     st.markdown("""
# #         <style>
# #             .header {
# #                 background-color: #00e19f;
# #                 padding: 10px;
# #                 text-align: center;
# #                 border-radius: 10px;
# #                 color: white;
# #                 font-size: 25px;
# #             }
# #             .section-title {
# #                 font-size: 20px;
# #                 font-weight: bold;
# #                 margin-top: 20px;
# #                 color: #00e19f;
# #             }
# #         </style>
# #     """, unsafe_allow_html=True)
# #     st.markdown('<div class="header">Analyse Inter-Restaurant</div>', unsafe_allow_html=True)

# #     # File paths
# #     data_file = "merged_data_final.xlsx"
# #     processed_file = "processed_data.xlsx"

# #     try:
# #         # Load preprocessed data or preprocess if not available
# #         df = preprocess_and_save_data(data_file, processed_file)
# #     except FileNotFoundError:
# #         st.error(f"Le fichier '{data_file}' est introuvable. Assurez-vous qu'il est placé au bon endroit.")
# #         return

# #     st.write("### Aperçu des Données Chargées")
# #     st.dataframe(df.head())

# #     if 'REVIEW_BODY' not in df.columns or 'REVIEW_SCORE' not in df.columns:
# #         st.error("Le fichier doit contenir les colonnes 'REVIEW_BODY' et 'REVIEW_SCORE'.")
# #         return

# #     restaurant_groups = df.groupby('RESTAURANT_NAME')

# #     st.write("### Sélectionnez les restaurants à comparer")
# #     selected_restaurants = st.multiselect("Restaurants disponibles", restaurant_groups.groups.keys())

# #     if len(selected_restaurants) < 2:
# #         st.warning("Veuillez sélectionner au moins deux restaurants pour effectuer une comparaison.")
# #         return

# #     restaurant_analyses = {name: analyze_restaurant(restaurant_groups.get_group(name)) for name in selected_restaurants}
# #     comparison_df = compare_restaurants(restaurant_analyses)

# #     st.write("### Table de Comparaison")
# #     st.dataframe(comparison_df)

# #     st.write("### Visualisations")
# #     visualize_restaurant_comparison(comparison_df)



# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from nltk.corpus import stopwords
# from nltk.sentiment import SentimentIntensityAnalyzer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from collections import Counter
# import re
# import os
# import spacy

# # Load spaCy French model
# nlp = spacy.load('fr_core_news_sm')

# # Stopword setup
# french_stopwords = set(stopwords.words('french'))
# additional_stopwords = {'et', 'de', 'un', 'le', 'la', 'les', 'des', 'est', 'très', 'pour'}
# french_stopwords.update(additional_stopwords)

# @st.cache_data
# def advanced_preprocess(text):
#     if not isinstance(text, str):
#         return ''
#     text = text.lower()
#     text = re.sub(r'http\\S+|www\\S+|https\\S+', '', text)
#     text = re.sub(r'[^a-zA-ZÀ-ÿ\\s]', ' ', text)
#     text = ' '.join(text.split())
#     doc = nlp(text)
#     tokens = [token.text for token in doc if not token.is_stop and token.text.strip()]
#     return ' '.join(tokens)

# def preprocess_and_save_data(input_file, output_file):
#     """Load data, preprocess if needed, and save preprocessed results."""
#     if os.path.exists(output_file):
#         return pd.read_excel(output_file)

#     df = pd.read_excel(input_file)
#     if 'processed_review' not in df.columns:
#         st.info("Prétraitement des données en cours, veuillez patienter...")
#         df['processed_review'] = df['REVIEW_BODY'].apply(advanced_preprocess)
#         df.to_excel(output_file, index=False)

#     return df

# def analyze_restaurant(restaurant_data):
#     n_reviews = len(restaurant_data)
#     avg_score = restaurant_data['REVIEW_SCORE'].mean()
#     sia = SentimentIntensityAnalyzer()
#     sentiments = restaurant_data['REVIEW_BODY'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
#     tfidf = TfidfVectorizer(max_features=100, stop_words=list(french_stopwords))
#     tfidf_matrix = tfidf.fit_transform(restaurant_data['processed_review'])
#     word_freq = Counter(' '.join(restaurant_data['processed_review']).split())
#     most_common_words = dict(word_freq.most_common(15))
#     aspects = {
#         'nourriture': ['plat', 'cuisine', 'nourriture', 'repas', 'menu'],
#         'service': ['service', 'personnel', 'équipe', 'accueil'],
#         'ambiance': ['ambiance', 'décor', 'cadre', 'atmosphère']
#     }
#     aspect_mentions = {aspect: 0 for aspect in aspects}
#     for review in restaurant_data['processed_review']:
#         for aspect, keywords in aspects.items():
#             if any(keyword in str(review).lower() for keyword in keywords):
#                 aspect_mentions[aspect] += 1
#     return {
#         'stats': {'n_reviews': n_reviews, 'avg_score': avg_score, 'aspect_mentions': aspect_mentions},
#         'sentiments': sentiments,
#         'word_frequencies': most_common_words
#     }

# def compare_restaurants(restaurant_analyses):
#     comparison_data = {}
#     for restaurant_name, analysis in restaurant_analyses.items():
#         comparison_data[restaurant_name] = {
#             'Average Score': analysis['stats']['avg_score'],
#             'Number of Reviews': analysis['stats']['n_reviews'],
#             'Aspect Mentions': analysis['stats']['aspect_mentions']
#         }
#     comparison_df = pd.DataFrame.from_dict(comparison_data, orient='index')
#     return comparison_df

# def visualize_restaurant_comparison(comparison_df):
#     fig, ax = plt.subplots(figsize=(10, 6))
#     comparison_df['Average Score'].sort_values().plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
#     ax.set_title('Average Scores Across Restaurants')
#     ax.set_ylabel('Average Score')
#     ax.set_xticklabels(comparison_df.index, rotation=45)
#     st.pyplot(fig)

# def plot_sentiment_distribution(sentiments, restaurant_name):
#     plt.figure(figsize=(8, 5))
#     plt.hist(sentiments, bins=30, color='blue', alpha=0.7)
#     plt.title(f'Sentiment Distribution for {restaurant_name}')
#     plt.xlabel('Sentiment Score')
#     plt.ylabel('Frequency')
#     st.pyplot(plt)

# def plot_word_frequencies(word_frequencies, restaurant_name):
#     words, counts = zip(*word_frequencies.items())
#     plt.figure(figsize=(8, 5))
#     plt.barh(words, counts, color='green')
#     plt.title(f'Top Words in Reviews for {restaurant_name}')
#     plt.xlabel('Frequency')
#     plt.ylabel('Words')
#     st.pyplot(plt)

# def plot_aspect_mentions(aspect_mentions, restaurant_name):
#     aspects, counts = zip(*aspect_mentions.items())
#     plt.figure(figsize=(8, 5))
#     plt.bar(aspects, counts, color='purple')
#     plt.title(f'Aspect Mentions for {restaurant_name}')
#     plt.xlabel('Aspect')
#     plt.ylabel('Mentions')
#     st.pyplot(plt)

# # Streamlit App
# def show_analyse_inter_restaurant():
#     st.markdown("""
#         <style>
#             .header {
#                 background-color: #00e19f;
#                 padding: 10px;
#                 text-align: center;
#                 border-radius: 10px;
#                 color: white;
#                 font-size: 25px;
#             }
#             .section-title {
#                 font-size: 20px;
#                 font-weight: bold;
#                 margin-top: 20px;
#                 color: #00e19f;
#             }
#         </style>
#     """, unsafe_allow_html=True)
#     st.markdown('<div class="header">Analyse Inter-Restaurant</div>', unsafe_allow_html=True)

#     data_file = "merged_data_final.xlsx"
#     processed_file = "processed_data.xlsx"

#     try:
#         df = preprocess_and_save_data(data_file, processed_file)
#     except FileNotFoundError:
#         st.error(f"Le fichier '{data_file}' est introuvable.")
#         return

#     st.write("### Aperçu des Données Chargées")
#     st.dataframe(df.head())

#     if 'REVIEW_BODY' not in df.columns or 'REVIEW_SCORE' not in df.columns:
#         st.error("Le fichier doit contenir les colonnes 'REVIEW_BODY' et 'REVIEW_SCORE'.")
#         return

#     restaurant_groups = df.groupby('RESTAURANT_NAME')

#     st.write("### Sélectionnez les restaurants à comparer")
#     selected_restaurants = st.multiselect("Restaurants disponibles", restaurant_groups.groups.keys())

#     if len(selected_restaurants) < 2:
#         st.warning("Veuillez sélectionner au moins deux restaurants pour effectuer une comparaison.")
#         return

#     restaurant_analyses = {name: analyze_restaurant(restaurant_groups.get_group(name)) for name in selected_restaurants}
#     comparison_df = compare_restaurants(restaurant_analyses)

#     st.write("### Comparaison des Restaurants")
#     st.dataframe(comparison_df)

#     st.write("### Visualisations des Scores Moyens")
#     visualize_restaurant_comparison(comparison_df)

#     for name in selected_restaurants:
#         st.write(f"### Insights pour {name}")
#         analysis = restaurant_analyses[name]
#         plot_sentiment_distribution(analysis['sentiments'], name)
#         plot_word_frequencies(analysis['word_frequencies'], name)
#         plot_aspect_mentions(analysis['stats']['aspect_mentions'], name)



import streamlit as st
import pandas as pd
import plotly.express as px
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# Streamlit App
def show_analyse_inter_restaurant():
    st.markdown(""" 
        <style>
            .header {
                background-color: #00e19f;
                padding: 10px;
                text-align: center;
                border-radius: 10px;
                color: white;
                font-size: 25px;
            }
            .section-title {
                font-size: 20px;
                font-weight: bold;
                margin-top: 20px;
                color: #00e19f;
            }
            .plot-container {
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            .st-table {
                border-radius: 10px;
                background-color: #ffffff;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="header">Analyse Inter-Restaurant</div>', unsafe_allow_html=True)

    # Load preprocessed dataset
    processed_file = "processed_data.xlsx"  # Preprocessed data file

    if not os.path.exists(processed_file):
        st.error(f"Le fichier prétraité '{processed_file}' est introuvable.")
        return

    # Load processed data
    df = pd.read_excel(processed_file)
    st.write("### Aperçu des Données Chargées")
    st.dataframe(df.head(), use_container_width=True)

    if 'processed_review' not in df.columns or 'REVIEW_SCORE' not in df.columns:
        st.error("Le fichier doit contenir les colonnes 'processed_review' et 'REVIEW_SCORE'.")
        return

    # Group by restaurant name and calculate the total number of reviews
    restaurant_groups = df.groupby('RESTAURANT_NAME')
    total_reviews = restaurant_groups['REVIEW_SCORE'].count().reset_index()

    # Horizontal bar plot for total reviews by restaurant with different style
    st.write("### Nombre Total d'Avis pour Chaque Restaurant")

    fig_bar_reviews_horizontal = px.bar(
        total_reviews,
        x='REVIEW_SCORE',
        y='RESTAURANT_NAME',
        orientation='h',
        title='Nombre Total d\'Avis pour Chaque Restaurant',
        labels={'RESTAURANT_NAME': 'Restaurant', 'REVIEW_SCORE': 'Nombre d\'Avis'},
        color='REVIEW_SCORE',  # Colorier en fonction du nombre d'avis
        color_continuous_scale='RdYlGn',  # Palette de couleurs plus vive (Rouge - Jaune - Vert)
        text='REVIEW_SCORE',  # Affiche le nombre d'avis sur chaque barre
    )

    # Personnalisation du graphique
    fig_bar_reviews_horizontal.update_layout(
        xaxis_title='Nombre d\'Avis',
        yaxis_title='Restaurant',
        xaxis_tickangle=0,
        yaxis_tickangle=0,  # Ajuste les labels des restaurants pour qu'ils ne se chevauchent pas
        plot_bgcolor='#f4f4f9',  # Fond clair
        paper_bgcolor='#f4f4f9',  # Papier du graphique
        margin=dict(t=60, b=30, l=30, r=30),
        showlegend=False,  # Cache la légende pour plus de lisibilité
    )

    # Personnalisation des barres (ajout d'un arrondi, espacement plus large)
    fig_bar_reviews_horizontal.update_traces(
        texttemplate='%{text}',  # Afficher le nombre d'avis sur les barres
        textposition='inside',  # Position du texte à l'intérieur des barres
    )

    st.plotly_chart(fig_bar_reviews_horizontal, use_container_width=True)

    # Ajout du filtre année
    years = df['REVIEW_YEAR'].unique()
    selected_year = st.selectbox('Sélectionner une année', years)

    # Filtrer les données selon l'année sélectionnée
    df_year_filtered = df[df['REVIEW_YEAR'] == selected_year]

    # Group by restaurant name and calculate average scores for the selected year
    restaurant_groups = df_year_filtered.groupby('RESTAURANT_NAME')
    avg_scores = restaurant_groups['REVIEW_SCORE'].mean().reset_index()

    # Graphique en barres des scores moyens par restaurant
    st.write(f"### Scores Moyens des Restaurants pour l'Année {selected_year}")
    fig_avg_scores_year = px.bar(
        avg_scores,
        x='RESTAURANT_NAME',
        y='REVIEW_SCORE',
        color='REVIEW_SCORE',
        color_continuous_scale='Teal',
        title=f'Scores Moyens des Restaurants ({selected_year})',
        labels={'RESTAURANT_NAME': 'Restaurant', 'REVIEW_SCORE': 'Score Moyen'}
    )
    fig_avg_scores_year.update_layout(
        xaxis_title='Restaurant',
        yaxis_title='Score Moyen',
        xaxis_tickangle=45,  # Pour incliner les labels sur l'axe des X
        plot_bgcolor='#f9f9f9',
        paper_bgcolor='#f9f9f9',
        margin=dict(t=60, b=60, l=30, r=30),
    )
    st.plotly_chart(fig_avg_scores_year, use_container_width=True)

    # Select restaurants
    st.write("### Sélectionnez les restaurants à comparer")
    selected_restaurants = st.multiselect("Restaurants disponibles", restaurant_groups.groups.keys())

    if len(selected_restaurants) < 2:
        st.warning("Veuillez sélectionner au moins deux restaurants pour effectuer une comparaison.")
        return

    # Analyze restaurants
    restaurant_analyses = {}
    for name in selected_restaurants:
        group_data = restaurant_groups.get_group(name)
        n_reviews = len(group_data)
        avg_score = group_data['REVIEW_SCORE'].mean()
        sia = SentimentIntensityAnalyzer()
        sentiments = group_data['REVIEW_BODY'].apply(lambda x: sia.polarity_scores(str(x))['compound'])

        word_freq = Counter(' '.join(group_data['processed_review']).split())
        most_common_words = dict(word_freq.most_common(15))

        aspects = {
            'nourriture': ['plat', 'cuisine', 'nourriture', 'repas', 'menu'],
            'service': ['service', 'personnel', 'équipe', 'accueil'],
            'ambiance': ['ambiance', 'décor', 'cadre', 'atmosphère']
        }
        aspect_mentions = {aspect: 0 for aspect in aspects}
        for review in group_data['processed_review']:
            for aspect, keywords in aspects.items():
                if any(keyword in str(review).lower() for keyword in keywords):
                    aspect_mentions[aspect] += 1

        restaurant_analyses[name] = {
            'stats': {'n_reviews': n_reviews, 'avg_score': avg_score, 'aspect_mentions': aspect_mentions},
            'sentiments': sentiments,
            'word_frequencies': most_common_words
        }

    # Compare restaurants
    comparison_data = {}
    for restaurant_name, analysis in restaurant_analyses.items():
        comparison_data[restaurant_name] = {
            'Average Score': analysis['stats']['avg_score'],
            'Number of Reviews': analysis['stats']['n_reviews'],
            'Aspect Mentions': analysis['stats']['aspect_mentions']
        }
    comparison_df = pd.DataFrame.from_dict(comparison_data, orient='index')

    st.write("### Comparaison des Restaurants")
    st.dataframe(comparison_df.style.set_properties(
        **{'background-color': 'white', 'border': '1px solid #ddd', 'color': '#333'}).set_table_styles(
        [{'selector': 'thead th', 'props': [('background-color', '#00e19f'), ('color', 'white')]}], 
        overwrite=True
    ))

    # Visualisation des Scores Moyens
    st.write("### Visualisations des Scores Moyens")
    fig_avg_scores = px.bar(
        comparison_df.reset_index(),
        x='index',
        y='Average Score',
        color='Average Score',
        text='Average Score',
        color_continuous_scale='Teal',
        title='Scores Moyens des Restaurants'
    )
    fig_avg_scores.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_avg_scores.update_layout(
        xaxis_title='Restaurant',
        yaxis_title='Score Moyen',
        xaxis_tickangle=45,
        showlegend=False
    )
    fig_avg_scores.update_layout(
        plot_bgcolor='#f9f9f9',
        paper_bgcolor='#f9f9f9',
        margin=dict(t=60, b=30, l=30, r=30),
    )
    st.plotly_chart(fig_avg_scores, use_container_width=True)

    # Visualisation par restaurant
    for name in selected_restaurants:
        analysis = restaurant_analyses[name]

        # Distribution des Sentiments
        st.markdown(f"### Distribution des Sentiments pour {name}")
        with st.container():
            fig_sentiments = px.histogram(
                analysis['sentiments'],
                nbins=30,
                title=f'Distribution des Sentiments pour {name}',
                labels={'value': 'Score du Sentiment'},
                color_discrete_sequence=['#00e19f']
            )
            fig_sentiments.update_layout(
                xaxis_title='Score du Sentiment',
                yaxis_title='Fréquence',
                plot_bgcolor='#f9f9f9',
                paper_bgcolor='#f9f9f9',
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig_sentiments)

        # Fréquences des mots
        st.markdown(f"### Top Mots dans les Avis pour {name}")
        with st.container():
            words, counts = zip(*analysis['word_frequencies'].items())
            fig_word_freq = px.bar(
                x=counts,
                y=words,
                orientation='h',
                title=f'Top Mots dans les Avis pour {name}',
                labels={'x': 'Fréquence', 'y': 'Mots'},
                color=counts,
                color_continuous_scale='YlGnBu'
            )
            fig_word_freq.update_layout(
                xaxis_title='Fréquence',
                yaxis_title='Mots',
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor='#f9f9f9',
                paper_bgcolor='#f9f9f9',
                margin=dict(t=30, b=30, l=30, r=30),
                showlegend=False
            )
            st.plotly_chart(fig_word_freq)

            # Génération du WordCloud
            st.markdown(f"### Nuage de Mots pour {name}")
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white', 
                colormap='YlGnBu'
            ).generate_from_frequencies(analysis['word_frequencies'])

            # Affichage du WordCloud
            fig_wc = plt.figure(figsize=(8, 4))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(fig_wc)

        # Mentions des Aspects
        st.markdown(f"### Mentions des Aspects pour {name}")
        with st.container():
            aspects, counts = zip(*analysis['stats']['aspect_mentions'].items())
            fig_aspects = px.bar(
                x=aspects,
                y=counts,
                title=f'Mentions des Aspects pour {name}',
                labels={'x': 'Aspect', 'y': 'Mentions'},
                color=counts,
                color_continuous_scale='Purples'
            )
            fig_aspects.update_layout(
                xaxis_title='Aspect',
                yaxis_title='Mentions',
                plot_bgcolor='#f9f9f9',
                paper_bgcolor='#f9f9f9',
                margin=dict(t=30, b=30, l=30, r=30),
                showlegend=False
            )
            st.plotly_chart(fig_aspects)
