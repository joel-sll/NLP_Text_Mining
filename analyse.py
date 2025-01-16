# analyse.py

import sqlite3
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

# Charger BDD
DB_PATH = "./tripadvisor.db"

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables dans la base de données :", tables)

with sqlite3.connect(DB_PATH) as conn:
    query = "SELECT * FROM reviews"
    data = pd.read_sql_query(query, conn)

# Distribution des notes
def get_review_distribution(cursor, restaurant_id):

    query = """
        SELECT REVIEW_SCORE, COUNT(*) AS count
        FROM reviews
        WHERE ID_RESTAURANT = ?
        GROUP BY REVIEW_SCORE
        ORDER BY REVIEW_SCORE
        """
        
    cursor.execute(query, (restaurant_id,))
    rows = cursor.fetchall()
        
    review_distribution = {row[0]: row[1] for row in rows}
        
    return review_distribution


# Fonction qui calcule note moyenne et l'affiche avec le nom du restaurant
def get_average_rating_per_restaurant():
    """
    Calcule la note moyenne de chaque restaurant.
    """
    query = """
        SELECT 
            r.RESTAURANT_NAME, 
            AVG(rv.REVIEW_SCORE) AS average_rating,
            r.PRICE_RANGE,
            r.ADDRESS,
            pc.POSTAL_CODE
        FROM 
            RESTAURANT r
        INNER JOIN 
            REVIEWS rv 
        ON 
            r.ID_RESTAURANT = rv.ID_RESTAURANT
        LEFT JOIN 
            POSTAL_CODE pc
        ON 
            r.POSTAL_CODE = pc.ID_POSTAL_CODE
        GROUP BY 
            r.RESTAURANT_NAME
        ORDER BY 
            average_rating DESC
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    
    return [{"Restaurant Name": row[0], 
             "Average Rating": round(row[1], 2), 
             "Price Range": row[2],
             "Address": row[3],
             "Postal Code": row[4]} for row in rows]

# top 5 restaurants
def get_top_5_restaurants():
    """
    Cette fonction récupère les restaurants, les trie par note moyenne et retourne les 5 premiers restaurants.
    """
    # Récupérer les restaurants, leurs notes moyennes, le type de cuisine, l'adresse et le code postal
    average_ratings = get_average_rating_per_restaurant()  # Fonction déjà définie pour récupérer les notes moyennes
    
    # Trier les restaurants par note moyenne de manière décroissante
    sorted_ratings = sorted(average_ratings, key=lambda x: x['Average Rating'], reverse=True)
    
    # Retourner les 5 restaurants avec les meilleures notes
    return sorted_ratings[:5]


# Fonction pour récupérer les noms de restaurants depuis la base de données
def load_restaurant_names():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT RESTAURANT_NAME FROM RESTAURANT"
        cursor.execute(query)
        restaurant_names = [row[0] for row in cursor.fetchall()]
    return restaurant_names