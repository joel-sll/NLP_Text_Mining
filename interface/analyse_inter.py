
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
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
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
    st.dataframe(df.head())

    if 'processed_review' not in df.columns or 'REVIEW_SCORE' not in df.columns:
        st.error("Le fichier doit contenir les colonnes 'processed_review' et 'REVIEW_SCORE'.")
        return

    restaurant_groups = df.groupby('RESTAURANT_NAME')

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
    st.dataframe(comparison_df)

    # Visualizations
    st.write("### Visualisations des Scores Moyens")
    fig, ax = plt.subplots(figsize=(10, 6))
    comparison_df['Average Score'].sort_values().plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
    ax.set_title('Average Scores Across Restaurants')
    ax.set_ylabel('Average Score')
    ax.set_xticklabels(comparison_df.index, rotation=45)
    st.pyplot(fig)

    # Insights for each restaurant
    for name in selected_restaurants:
        st.write(f"### Insights pour {name}")
        analysis = restaurant_analyses[name]

        # Sentiment Distribution
        plt.figure(figsize=(8, 5))
        plt.hist(analysis['sentiments'], bins=30, color='blue', alpha=0.7)
        plt.title(f'Sentiment Distribution for {name}')
        plt.xlabel('Sentiment Score')
        plt.ylabel('Frequency')
        st.pyplot(plt)

        # Word Frequencies
        words, counts = zip(*analysis['word_frequencies'].items())
        plt.figure(figsize=(8, 5))
        plt.barh(words, counts, color='green')
        plt.title(f'Top Words in Reviews for {name}')
        plt.xlabel('Frequency')
        plt.ylabel('Words')
        st.pyplot(plt)

        # Aspect Mentions
        aspects, counts = zip(*analysis['stats']['aspect_mentions'].items())
        plt.figure(figsize=(8, 5))
        plt.bar(aspects, counts, color='purple')
        plt.title(f'Aspect Mentions for {name}')
        plt.xlabel('Aspect')
        plt.ylabel('Mentions')
        st.pyplot(plt)
