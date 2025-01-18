import sqlite3
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from textblob import TextBlob
import matplotlib.pyplot as plt
import plotly.express as px

# Load database
DB_PATH = "./tripadvisor.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables dans la base de données :", tables)

with sqlite3.connect(DB_PATH) as conn:
    query = "SELECT * FROM reviews"
    data = pd.read_sql_query(query, conn)

# Fonction qui calcule note moyenne et l'affiche avec le nom du restaurant
# Fonction modifiée pour ne récupérer que la note moyenne
def get_average_rating_per_restaurant():
    """
    Calcule la note moyenne de chaque restaurant sans les autres détails.
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

# top 5 restaurants
def get_top_5_restaurants():
    """
    Cette fonction récupère les restaurants, les trie par note moyenne et retourne les 5 premiers restaurants.
    """
    average_ratings = get_average_rating_per_restaurant()
    sorted_ratings = sorted(average_ratings, key=lambda x: x['Average Rating'], reverse=True)

    return sorted_ratings[:5]

# Fonction pour récupérer les noms de restaurants depuis la base de données
def load_restaurant_names():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT RESTAURANT_NAME FROM RESTAURANT"
        cursor.execute(query)
        restaurant_names = [row[0] for row in cursor.fetchall()]
    return restaurant_names

#Fonction pour récupérer les années dans la table reviews

#Fonction pour récupérer les mois dans la table reviews

# Ajouter des colonnes latitude et longitude si elles n'existent pas
def ensure_lat_lon_columns():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE restaurant ADD COLUMN latitude REAL")
            cursor.execute("ALTER TABLE restaurant ADD COLUMN longitude REAL")
        except sqlite3.OperationalError:
            pass 

# Récupérer les coordonnées géographiques d'une adresse
def get_coordinates(address):
    geolocator = Nominatim(user_agent="restaurant_geocoder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        return None, None

# Mettre à jour les coordonnées géographiques dans la base de données
def update_restaurant_coordinates():
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

# Récupérer les restaurants avec leurs coordonnées
def get_restaurants_with_coordinates():
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT RESTAURANT_NAME, ID_RESTAURANT, latitude, longitude
            FROM restaurant
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """
        return pd.read_sql_query(query, conn)

# Ajouter la fonction d'extraction du type de cuisine
def extract_cuisines(detail):
    try:
        data = json.loads(detail)
        cuisines = data.get("CUISINES", "").strip("[]").replace('"', '').split(", ")
        
        # Enlever les espaces vides et les éléments vides dans la liste
        cuisines = [cuisine.strip() for cuisine in cuisines if cuisine.strip()]
        
        return cuisines
    except Exception as e:
        print(f"Erreur lors de l'extraction des cuisines : {e}")
        return []

# Fonction pour récupérer les informations d'un restaurant
def get_restaurant_details(restaurant_name):
    with sqlite3.connect(DB_PATH) as conn:
        query = """
            SELECT r.ID_RESTAURANT, r.RESTAURANT_NAME, r.ADDRESS, r.DETAILS, pc.POSTAL_CODE, AVG(rv.REVIEW_SCORE) AS AVERAGE_RATING
            FROM RESTAURANT r
            LEFT JOIN REVIEWS rv ON r.ID_RESTAURANT = rv.ID_RESTAURANT
            LEFT JOIN POSTAL_CODE pc ON r.POSTAL_CODE = pc.ID_POSTAL_CODE
            WHERE r.RESTAURANT_NAME = ?
            GROUP BY r.RESTAURANT_NAME
        """
        cursor = conn.cursor()
        cursor.execute(query, (restaurant_name,))
        row = cursor.fetchone()

    # Extraire les cuisines du détail
    cuisines = extract_cuisines(row[3])  # row[3] correspond à la colonne DETAILS
    
    return {
        "ID_RESTAURANT": row[0],
        "RESTAURANT_NAME": row[1],
        "ADDRESS": row[2],
        "DETAILS": row[3],
        "POSTAL_CODE": row[4],
        "AVERAGE_RATING": round(row[5], 2) if row[5] else "N/A",
        "CUISINES": ", ".join(cuisines)  # Ajouter les cuisines extraites
    }

# Fonction pour récupérer le nombre total d'avis pour un restaurant
def get_total_reviews_for_restaurant(restaurant_name):
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

#====================== SENTIMENT ANALYSIS

# Fonction pour récupérer les meilleurs commentaires pour un restaurant
def get_top_reviews_for_restaurant(restaurant_id, limit=3):
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

# Fonction pour récupérer la distribution des scores de commentaires
def get_review_score_distribution(restaurant_name):
    """
    Calcule la distribution des scores des commentaires pour un restaurant spécifique.
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

    # Extraire les scores
    score_list = [score[0] for score in scores]
    return score_list

# Fonction pour analyser la distribution des sentiments
def analyze_sentiment(text):
    """
    Analyse le sentiment d'un texte et retourne 'Positif', 'Neutre' ou 'Négatif'.
    """
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:  # Positif si la polarité est significativement au-dessus de zéro
        return 'Positif'
    elif polarity < -0.1:  # Négatif si la polarité est significativement en dessous de zéro
        return 'Négatif'
    else:  # Neutre sinon
        return 'Neutre'


def get_sentiment_distribution_for_restaurant(restaurant_name):
    """
    Analyse les sentiments des avis pour un restaurant donné.
    Retourne la distribution des sentiments (Positif, Neutre, Négatif).
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

# Analyse avis selon visit_context
def get_sentiment_distribution_by_visit_context(restaurant_name):
    """
    Analyse les sentiments des avis pour chaque type de VISIT_CONTEXT pour un restaurant donné.
    Retourne la distribution des sentiments par contexte de visite (Positif, Neutre, Négatif).
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

#recuperer avis selon sentiments
def get_reviews_by_sentiment(restaurant_name, sentiment):
    """
    Récupère les avis pour un restaurant donné et filtre selon le sentiment spécifié.
    Retourne une liste d'avis correspondant à ce sentiment.
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




#------------------------ TENDANCE ANALYSIS
# Fonction pour récupérer les notes moyennes filtrées
def get_monthly_review_trends(restaurant_name, year, month):
    # Connexion à la base de données
    with sqlite3.connect(DB_PATH) as conn:
        # Définition de la requête SQL
        query = """
            SELECT r.REVIEW_YEAR, r.REVIEW_MONTH, AVG(r.REVIEW_SCORE) as average_score
            FROM reviews r
            JOIN restaurant rest ON r.ID_RESTAURANT = rest.ID_RESTAURANT
            WHERE rest.RESTAURANT_NAME = ?
              AND (? IS NULL OR r.REVIEW_YEAR = ?)
              AND (? IS NULL OR r.REVIEW_MONTH = ?)
            GROUP BY r.REVIEW_YEAR, r.REVIEW_MONTH
            ORDER BY r.REVIEW_YEAR, r.REVIEW_MONTH;
        """
        # Exécution de la requête et récupération des résultats dans un DataFrame
        df = pd.read_sql_query(query, conn, params=(restaurant_name, year, year, month, month))
        
    return df