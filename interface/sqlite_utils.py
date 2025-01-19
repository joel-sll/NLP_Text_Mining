import sqlite3
import os
try:
    import pyarrow
except:
    %pip install pyarrow
    import pyarrow

try:
    import pandas as pd
except:
    %pip install pandas
    import pandas as pd

import json
import numpy
import re

country_schema = {
    "ID_COUNTRY": "INTEGER PRIMARY KEY",
    "COUNTRY": "TEXT"
}

postal_code_schema = {
    "ID_POSTAL_CODE": "INTEGER PRIMARY KEY",
    "POSTAL_CODE": "TEXT"
}

city_schema = {
    "ID_CITY": "INTEGER PRIMARY KEY",
    "ID_COUNTRY": "INTEGER REFERENCES COUNTRY(ID_COUNTRY)",
    "ID_POSTAL_CODE": "INTEGER REFERENCES POSTAL_CODE(ID_POSTAL_CODE)",
    "CITY_NAME": "TEXT"
}

restaurant_schema = {
    "ID_RESTAURANT": "INTEGER PRIMARY KEY",
    "SOURCE_PAGE": "TEXT UNIQUE",
    "RESTAURANT_NAME": "TEXT",
    "CLAIMED": "BOOLEAN",
    "PRICE_RANGE": "TEXT",
    "ADDRESS": "TEXT",
    "POSTAL_CODE": "INTEGER REFERENCES POSTAL_CODE(ID_POSTAL_CODE)",
    "CITY": "INTEGER REFERENCES CITY(ID_CITY)",
    "COUNTRY": "INTEGER REFERENCES COUNTRY(ID_COUNTRY)",
    "PHONE_NUMBER": "TEXT",
    "OPENING_HOURS": "TEXT",
    "TRAVELERS_CHOICE": "TEXT",
    "DETAILED_RATING": "TEXT",
    "REVIEW_NUMBER": "INTEGER",
    "OVERALL_RATING": "REAL",
    "RANKING": "TEXT",
    "INFO": "TEXT",
    "SERVICES": "TEXT",
    "RATINGS": "TEXT"
}

photos_schema = {
    "ID_PHOTO": "INTEGER PRIMARY KEY",
    "ID_RESTAURANT": "INTEGER REFERENCES RESTAURANT(ID_RESTAURANT)",
    "DESCRIPTION": "TEXT",
    "URL": "TEXT"
}

reviews_schema = {
    "ID_REVIEW": "INTEGER PRIMARY KEY",
    "ID_RESTAURANT": "INTEGER REFERENCES RESTAURANT(ID_RESTAURANT)",
    "N_CONTRIB": "INTEGER",
    "REVIEW_TITLE": "TEXT",
    "REVIEW_BODY": "TEXT",
    "REVIEW_SCORE": "REAL",
    "REVIEW_DAY": "TEXT",
    "REVIEW_MONTH": "TEXT",
    "REVIEW_YEAR": "TEXT",
    "VISIT_MONTH": "TEXT",
    "VISIT_YEAR": "TEXT",
    "VISIT_CONTEXT": "TEXT"
}

schemas = {
    "country": country_schema,
    "postal_code": postal_code_schema,
    "city": city_schema,
    "restaurant": restaurant_schema,
    "photos": photos_schema,
    "reviews": reviews_schema
}

class DButils:
    def __init__(self, path: str, filename: str, exists_ok: bool =False):
        """
        Initialize a new sqlite database.

        Args:
            path (str): Path to the sqlite database file.
            filename (str): name of the sqlite file.
            exists_ok (bool): will thow an error if the database already exists if exists_ok is False.

        Notes:
            If the file does not exist, it will be created.
        """
        
        if not exists_ok and \
            os.path.exists(os.path.join(path, filename)):
            raise FileExistsError(f"Database {filename} already exists at {path}.")

        os.makedirs(path, exist_ok=True)
        self.PATH_TO_DB = os.path.join(path, filename)

    def is_table(self, table_name: str) -> bool:
        with sqlite3.connect(self.PATH_TO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name.upper(),)
            )
            return cursor.fetchone() is not None
        
    def create_table(self, table_name: str, schema: dict):
        schema_str = ", ".join(f"{col} {col_type}" for col, col_type in schema.items())

        with sqlite3.connect(self.PATH_TO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(f"CREATE TABLE {table_name.upper()} ({schema_str})")
            return True
        
        
    def insert(self, table_name: str, data: dict[str, any]) -> bool:

        columns = ", ".join(data.keys())
        values = tuple(data.values())
        placeholders = ", ".join("?" for _ in data)
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        #print(sql)
        try:
            with sqlite3.connect(self.PATH_TO_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute(sql, values)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error inserting data into table '{table_name}': {e}")
            return False
        
    def insert_restaurant(self, restaurant: pd.DataFrame):
        address = pd.DataFrame()
        address[["ADDRESS", "OTHER"]] = restaurant["address"].str.split(", ", expand=True)
        address[["POSTAL_CODE", "CITY", "COUNTRY"]] = address["OTHER"].str.split(" ", expand=True)
        address.drop(columns=["OTHER"], inplace=True)
        address = {key: value.iloc[0] for key, value in address.items()}

        restaurant_keys = [col for col in restaurant.columns if col not in ["address", "photos", "reviews", "traveler's choice"]]
        restaurant_dict = {key: restaurant[key].iloc[0] for key in restaurant_keys}
        restaurant_dict["overall_rating"] = restaurant_dict.pop("rating")
        
        if "fonctionnalités" in restaurant.columns:
            restaurant_dict["fonctionnalités"]["Fonctionnalités"] = restaurant_dict["fonctionnalités"]["Fonctionnalités"].tolist()
            restaurant_dict["services"] = json.dumps(restaurant_dict.pop("fonctionnalités"), ensure_ascii=False)

        if "traveler's choice" in restaurant.columns:
            restaurant_dict["travelers_choice"] = restaurant["traveler's choice"][0]

        if "ratings" in restaurant.columns:
            restaurant_dict["ratings"] = json.dumps(restaurant_dict["ratings"])


        restaurant_dict["opening_hours"] = json.dumps(restaurant_dict["opening_hours"], ensure_ascii=False)
        restaurant_dict["ranking"] = json.dumps(restaurant_dict["ranking"], ensure_ascii=False)
        restaurant_dict["detailed_rating"] = json.dumps(restaurant_dict["detailed_rating"], ensure_ascii=False)
        restaurant_dict["address"] = address["ADDRESS"]
        restaurant_dict["postal_code"] = address["POSTAL_CODE"]
        restaurant_dict["city"] = address["CITY"]
        restaurant_dict["country"] = address["COUNTRY"]

        

        with sqlite3.connect(self.PATH_TO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("SELECT ID_COUNTRY from COUNTRY WHERE COUNTRY=?", (restaurant_dict["country"],))
            country_id = cursor.fetchone()
            if not country_id:
                self.insert("country", {"country": restaurant_dict["country"]})
                country_id = [cursor.lastrowid + 1]
            country_id = country_id[0]

            cursor.execute("SELECT ID_POSTAL_CODE from POSTAL_CODE WHERE POSTAL_CODE=?", (restaurant_dict["postal_code"],))
            postal_code_id = cursor.fetchone()
            if not postal_code_id:
                self.insert("postal_code", {"postal_code": restaurant_dict["postal_code"]})
                postal_code_id = [cursor.lastrowid + 1]
            postal_code_id = postal_code_id[0]

            


            cursor.execute("SELECT ID_CITY from CITY WHERE CITY_NAME=?", (restaurant_dict["city"],))
            city_id = cursor.fetchone()
            if not city_id:
                self.insert("city", {"city_name": restaurant_dict["city"], "ID_COUNTRY": country_id, "ID_postal_code": postal_code_id})
                city_id = [cursor.lastrowid + 1]
            city_id = city_id[0]

            restaurant_dict["restaurant_name"] = restaurant_dict.pop("name")
            restaurant_dict["city"] = city_id
            restaurant_dict["postal_code"] = postal_code_id
            restaurant_dict["country"] = country_id
            
            self.insert("restaurant", restaurant_dict)
            restaurant_id = self.fetch_Foreignkey("restaurant", "restaurant_name", restaurant_dict["restaurant_name"])

            

            # for desc, url in restaurant["photos"][0].items():
            #     photo_dict = {
            #     'ID_RESTAURANT': restaurant_id[0],
            #     'DESCRIPTION': desc,
            #     'URL': url
            #     }
            #     self.insert("photos", photo_dict)

            for review in restaurant["reviews"].iloc[0]:
                r_dict = {}
                
                r_dict["n_contrib"] = review["n_contrib"]
                r_dict["review_title"] = review["review_title"]
                r_dict["review_body"] = review["review_body"]
                r_dict["review_score"] = review["review_score"]
                r_dict["ID_RESTAURANT"] = restaurant_id[0]
                r_dict["REVIEW_DAY"] = review["review_date"]["day"]
                r_dict["review_month"] = review["review_date"]["month"]
                r_dict["review_year"] = review["review_date"]["year"]
                # Invalid values for review["visit_date"]["year"] indicate the fields were missing in the review
                if re.match(r"\d{4}", review["visit_date"]["year"]):
                    r_dict["visit_month"] = review["visit_date"]["month"]
                    r_dict["visit_year"] = review["visit_date"]["year"]
                    r_dict["visit_context"] = review["visit_context"]
                else:
                    r_dict["visit_month"] = None
                    r_dict["visit_year"] = None
                    r_dict["visit_context"] = None
                db_tripadvisor.insert("REVIEWS", r_dict)
        return restaurant_dict


    def fetch_Foreignkey(self, table_name, var_name, value):
        with sqlite3.connect(self.PATH_TO_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute(f"SELECT ID_{table_name} from {table_name} WHERE {var_name}=?", (value,))
            FK = cursor.fetchone()
        return FK

    def drop_all_tables(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.PATH_TO_DB)
        cursor = conn.cursor()
        
        # Get the list of all table names from sqlite_master
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        