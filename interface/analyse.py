import sqlite3
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from textblob import TextBlob
import matplotlib.pyplot as plt
from collections import Counter
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import spacy
from nltk.corpus import stopwords

# Load database
DB_PATH = "./tripadvisor.db"

def get_average_rating_per_restaurant():
    """
    Calculates the average rating for each restaurant without including other details.
    The result is ordered by the average rating in descending order.
    """
    query = """
        SELECT 
            r.RESTAURANT_NAME, 
            AVG(rv.REVIEW_SCORE) AS average_rating
        FROM 
            RESTAURANT r
        INNER JOIN 
            REVIEWS rv 
        ON 
            r.ID_RESTAURANT = rv.ID_RESTAURANT
        GROUP BY 
            r.RESTAURANT_NAME
        ORDER BY 
            average_rating DESC
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    
    return [{"Restaurant Name": row[0], "Average Rating": round(row[1], 2)} for row in rows]


def get_top_5_restaurants():
    """
    This function retrieves the restaurants, sorts them by average rating, 
    and returns the top 5 restaurants with the highest ratings.
    """
    average_ratings = get_average_rating_per_restaurant()
    sorted_ratings = sorted(average_ratings, key=lambda x: x['Average Rating'], reverse=True)

    return sorted_ratings[:5]


def load_restaurant_names():
    """
    This function retrieves all restaurant names from the database.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT RESTAURANT_NAME FROM RESTAURANT"
        cursor.execute(query)
        restaurant_names = [row[0] for row in cursor.fetchall()]
    return restaurant_names


def ensure_lat_lon_columns():
    """
    This function adds 'latitude' and 'longitude' columns to the 'restaurant' table if they do not already exist.
    If the columns already exist, the function does nothing.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE restaurant ADD COLUMN latitude REAL")
            cursor.execute("ALTER TABLE restaurant ADD COLUMN longitude REAL")
        except sqlite3.OperationalError:
            pass 


def get_coordinates(address):
    """
    This function retrieves the geographical coordinates (latitude and longitude) for a given address.
    If the address is valid, it returns the coordinates. If not, it returns None for both latitude and longitude.
    """
    geolocator = Nominatim(user_agent="restaurant_geocoder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        return None, None


def update_restaurant_coordinates():
    """
    This function updates the geographical coordinates (latitude and longitude) 
    for each restaurant in the database based on its address, postal code, and city.
    It first ensures that the latitude and longitude columns exist, then fetches the required data,
    geocodes the addresses, and updates the database with the retrieved coordinates.
    """
    ensure_lat_lon_columns()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        query = """
            SELECT r.ID_RESTAURANT, r.ADDRESS, pc.POSTAL_CODE, c.CITY_NAME
            FROM restaurant r
            LEFT JOIN postal_code pc ON r.POSTAL_CODE = pc.ID_POSTAL_CODE
            LEFT JOIN city c ON r.CITY = c.ID_CITY
        """
        cursor.execute(query)
        restaurants = cursor.fetchall()

        for id_restaurant, address, postal_code, city_name in restaurants:
            full_address = ", ".join(filter(None, [address, postal_code, city_name]))
            latitude, longitude = get_coordinates(full_address)
            cursor.execute("""
                UPDATE restaurant
                SET latitude = ?, longitude = ?
                WHERE ID_RESTAURANT = ?
            """, (latitude, longitude, id_restaurant))

        conn.commit()


def get_restaurants_with_coordinates():
    """
    This function retrieves restaurants from the database that have valid geographical coordinates (latitude and longitude).
    It returns a DataFrame containing the restaurant names, IDs, and their corresponding coordinates.
    """
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT RESTAURANT_NAME, ID_RESTAURANT, latitude, longitude
            FROM restaurant
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        return pd.read_sql_query(query, conn)


def extract_cuisines(detail):
    """
    This function extracts the list of cuisines from the provided 'detail' JSON string.
    If the 'detail' is valid, it returns the cuisines. If not, it returns a default value of ["Non renseigné"].
    """
    try:
        if detail is not None:
            cuisines = json.loads(detail)
            return cuisines["CUISINES"]
        else:
            return ["Non renseigné"]
    except Exception as e:
        print(f"Erreur lors de l'extraction des cuisines : {e}")
        return ["Non renseigné"]


def get_restaurant_details(restaurant_name):
    """
    This function retrieves detailed information about a restaurant, including its name, address, services, 
    postal code, average rating, price range, phone number, and cuisine types from the database.
    The data is returned as a dictionary.
    """
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT r.ID_RESTAURANT, r.RESTAURANT_NAME, r.ADDRESS, r.SERVICES, pc.POSTAL_CODE, AVG(rv.REVIEW_SCORE) AS AVERAGE_RATING, r.PRICE_RANGE, r.PHONE_NUMBER
            FROM RESTAURANT r
            LEFT JOIN REVIEWS rv ON r.ID_RESTAURANT = rv.ID_RESTAURANT
            LEFT JOIN POSTAL_CODE pc ON r.POSTAL_CODE = pc.ID_POSTAL_CODE
            WHERE r.RESTAURANT_NAME = ?
            GROUP BY r.RESTAURANT_NAME
        """
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        row = cursor.fetchone()
    cuisines = extract_cuisines(row[3])
    
    return {
        "ID_RESTAURANT": row[0],
        "RESTAURANT_NAME": row[1],
        "ADDRESS": row[2],
        "SERVICES": row[3],
        "POSTAL_CODE": row[4],
        "AVERAGE_RATING": round(row[5], 2) if row[5] else "N/A",
        "PRICE_RANGE": row[6],
        "PHONE_NUMBER": row[7],
        "CUISINES": cuisines
        
    }


def get_total_reviews_for_restaurant(restaurant_name):
    """
    This function retrieves the total number of reviews for a specific restaurant.
    It performs a join between the REVIEWS and RESTAURANT tables and counts the number of reviews for the given restaurant name.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) 
            FROM REVIEWS rv
            INNER JOIN RESTAURANT r ON rv.ID_RESTAURANT = r.ID_RESTAURANT
            WHERE r.RESTAURANT_NAME = ?
        """
        cursor.execute(query, (restaurant_name,))
        total_reviews = cursor.fetchone()[0]
    return total_reviews


def get_top_reviews_for_restaurant(restaurant_id, limit=3):
    """
    This function retrieves the top reviews for a specific restaurant, ordered by review score in descending order.
    It returns a list of the best reviews, with a default limit of 3 reviews.
    """
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT REVIEW_TITLE, REVIEW_BODY, REVIEW_SCORE
            FROM reviews
            WHERE ID_RESTAURANT = ?
            ORDER BY REVIEW_SCORE DESC
            LIMIT ?
        """
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_id, limit))
        rows = cursor.fetchall()
        
    top_reviews = [{"title": row[0], "body": row[1], "score": row[2]} for row in rows]
    return top_reviews


def get_review_score_distribution(restaurant_name):
    """
    This function calculates the distribution of review scores for a specific restaurant.
    It retrieves the review scores and returns them as a list.
    """
    query = """
        SELECT rv.REVIEW_SCORE
        FROM REVIEWS rv
        INNER JOIN RESTAURANT r ON rv.ID_RESTAURANT = r.ID_RESTAURANT
        WHERE r.RESTAURANT_NAME = ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        scores = cursor.fetchall()

    score_list = [score[0] for score in scores]
    return score_list


def analyze_sentiment(text):
    """
    This function analyzes the sentiment of a given text and returns 'Positive', 'Neutral', or 'Negative'.
    It uses TextBlob to calculate the sentiment polarity and classify the sentiment accordingly.
    """
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:  
        return 'Positif'
    elif polarity < -0.1: 
        return 'Négatif'
    else:
        return 'Neutre'


def get_sentiment_distribution_for_restaurant(restaurant_name):
    """
    This function analyzes the sentiment of reviews for a given restaurant and returns the distribution of sentiments 
    (Positive, Neutral, Negative).
    """
    query = """
        SELECT rv.REVIEW_BODY
        FROM REVIEWS rv
        INNER JOIN RESTAURANT r ON rv.ID_RESTAURANT = r.ID_RESTAURANT
        WHERE r.RESTAURANT_NAME = ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        reviews = [row[0] for row in cursor.fetchall()]

    sentiments = [analyze_sentiment(review) for review in reviews]
    sentiment_counts = pd.Series(sentiments).value_counts()

    return {
        'Positif': sentiment_counts.get('Positif', 0),
        'Neutre': sentiment_counts.get('Neutre', 0),
        'Négatif': sentiment_counts.get('Négatif', 0)
    }


def get_sentiment_distribution_by_visit_context(restaurant_name):
    """
    This function analyzes the sentiment of reviews for each type of VISIT_CONTEXT for a given restaurant. 
    It returns the sentiment distribution (Positive, Neutral, Negative) by visit context.
    """
    query = """
        SELECT rv.REVIEW_BODY, rv.VISIT_CONTEXT
        FROM REVIEWS rv
        INNER JOIN RESTAURANT r ON rv.ID_RESTAURANT = r.ID_RESTAURANT
        WHERE r.RESTAURANT_NAME = ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        reviews_data = cursor.fetchall()

    sentiment_by_context = {'couples': {'Positif': 0, 'Neutre': 0, 'Négatif': 0},
                           'friends': {'Positif': 0, 'Neutre': 0, 'Négatif': 0},
                           'family': {'Positif': 0, 'Neutre': 0, 'Négatif': 0},
                           'business': {'Positif': 0, 'Neutre': 0, 'Négatif': 0},
                           'solo': {'Positif': 0, 'Neutre': 0, 'Négatif': 0}}

    for review_body, visit_context in reviews_data:
        sentiment = analyze_sentiment(review_body)
        if visit_context in sentiment_by_context:
            sentiment_by_context[visit_context][sentiment] += 1

    return sentiment_by_context


def get_reviews_by_sentiment(restaurant_name, sentiment):
    """
    This function retrieves reviews for a given restaurant and filters them based on the specified sentiment.
    It returns a list of reviews that match the specified sentiment (Positive, Neutral, or Negative).
    """
    query = """
        SELECT rv.REVIEW_BODY, rv.REVIEW_TITLE, rv.REVIEW_SCORE
        FROM REVIEWS rv
        INNER JOIN RESTAURANT r ON rv.ID_RESTAURANT = r.ID_RESTAURANT
        WHERE r.RESTAURANT_NAME = ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        reviews_data = cursor.fetchall()

    filtered_reviews = []
    for review in reviews_data:
        analyzed_sentiment = analyze_sentiment(review[0])
        print(f"Texte : {review[0]}\nSentiment : {analyzed_sentiment}\n")  # Debugging
        if analyzed_sentiment == sentiment:
            filtered_reviews.append({
                'title': review[1],
                'body': review[0],
                'score': review[2]
            })

    return filtered_reviews


def get_monthly_review_trends(restaurant_name, year, month):
    """
    This function retrieves the monthly review trends for a given restaurant, including the average score and 
    the number of reviews, filtered by year and month if provided.
    Returns a DataFrame with the monthly review trends.
    """
    with sqlite3.connect(DB_PATH) as conn:

        query = """
            SELECT r.REVIEW_YEAR, r.REVIEW_MONTH, AVG(r.REVIEW_SCORE) as average_score, COUNT(r.REVIEW_SCORE) as n_review
            FROM reviews r
            JOIN restaurant rest ON r.ID_RESTAURANT = rest.ID_RESTAURANT
            WHERE rest.RESTAURANT_NAME = ?
              AND (? IS NULL OR r.REVIEW_YEAR = ?)
              AND (? IS NULL OR r.REVIEW_MONTH = ?)
            GROUP BY r.REVIEW_YEAR, r.REVIEW_MONTH
            ORDER BY r.REVIEW_YEAR, r.REVIEW_MONTH;
        """
        df = pd.read_sql_query(query, conn, params=(restaurant_name, year, year, month, month))
        
    return df

# Load the French language model for spaCy
nlp = spacy.load('fr_core_news_sm')

# List of NLTK stopwords for French and additional words to exclude
french_stopwords = set(stopwords.words('french'))
additional_stopwords = {'et', 'de', 'un', 'le', 'la', 'les', 'des', 'est', 'très', 'pour'}
french_stopwords.update(additional_stopwords)

def clean_text(text):
    """
    Cleans the input text by performing the following operations:
    - Converts the text to lowercase.
    - Removes numbers and punctuation.
    - Lemmatizes the text using spaCy.
    - Filters out stopwords based on a custom stopword list.
    
    Returns the cleaned text as a string.
    """
    text = text.lower() 
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Process the text using spaCy (tokenization and lemmatization)
    doc = nlp(text)
    
    # Filter out stopwords, punctuation, and spaces, and lemmatize the remaining tokens
    cleaned_text = ' '.join([token.lemma_ for token in doc if token.text not in french_stopwords and not token.is_punct and not token.is_space])
    
    return cleaned_text


def generate_wordcloud(restaurant_name):
    """
    Generates a word cloud based on the positive reviews of a given restaurant.
    - Retrieves positive reviews using `get_reviews_by_sentiment`.
    - Cleans the reviews using `clean_text`.
    - Counts the most frequent words and generates a word cloud.

    Args:
    - restaurant_name (str): The name of the restaurant for which to generate the word cloud.
    """
    
    positive_reviews = get_reviews_by_sentiment(restaurant_name, "Positif")
    positive_reviews_text = ' '.join([review['body'] for review in positive_reviews])
    
    cleaned_text = clean_text(positive_reviews_text)
    
    words = cleaned_text.split()
    word_counts = Counter(words)
    
    most_common_words = word_counts.most_common(20)
    word_freq = {item[0]: item[1] for item in most_common_words}
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
    
    # Display the word cloud using matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)