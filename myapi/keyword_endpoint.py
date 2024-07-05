# from myapi import db
import os
import logging
import pathlib

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import MONGODB_CREDS,MYSQL_CREDS
from mysql.connector import connect, Error


# NOTE: create log file naming convention
LOG_FILENAME = os.path.join("myapi", "logs", "test_db_connections.log")
pathlib.Path(os.path.dirname(LOG_FILENAME)).mkdir(parents=True, exist_ok=True)
LOG_ENCODING = "utf-8"

# NOTE: setup logging
logging.basicConfig(
    filename=LOG_FILENAME,
    encoding=LOG_ENCODING,
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s.%(msecs)03d: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)


def create():
    from flask import request, jsonify
    if not request.is_json:
        return jsonify({"error": "Invalid input"}), 400

    data = request.get_json()
    keyword_str = data.get("keyword")
    id = data.get("id")


    try:
        with connect(
            # NOTE: hard coding credentials is not something one should do in PROD
            host=MYSQL_CREDS["host"],
            user=MYSQL_CREDS["user"],
            password=MYSQL_CREDS["password"],
            database=MYSQL_CREDS["database"],
        ) as connection:
            with connection.cursor() as cursor:
                query = "INSERT INTO keyword (id, name) VALUES (%s, %s)"
                cursor.execute(query, (id, keyword_str))
                connection.commit()
        
        return jsonify({"message": "Keyword created successfully"}), 201
    except Error as e:
        # logging.error(f"Error connecting to MySQL: {e}")
        return jsonify({"error": f"Error connecting to MySQL: {e}"}), 500

    # return jsonify({"message": f"Keyword {keyword_str} with id {id}"}), 201

def get_popular():
    from flask import request, jsonify
    # Get query parameters
    start_year = int(request.args.get('startDate'))
    end_year = int(request.args.get('endDate'))

    # Query MongoDB
    mongodb_query = [
        {
            '$match': {
                'year': {'$gte': start_year, '$lte': end_year}
            }
        },
        {
            '$unwind': '$keywords'
        },
        {
            '$group': {
                '_id': '$keywords.name',
                'publicationsCount': {'$sum': 1}
            }
        },
        {
            '$sort': {'publicationsCount': -1}
        },
        {
            '$limit': 10
        },
        {
            '$project': {
                '_id': 0,
                'keywordName': '$_id',
                'publicationsCount': 1
            }
        }
    ]

    try:
        with MongoClient(MONGODB_CREDS["url"]) as client:
            db = client[MONGODB_CREDS["database"]]
            publication_collection = db["publications"]
            
            results_iterator = publication_collection.aggregate(mongodb_query)
            results = []
            for entry in results_iterator:
                results.append(entry)

            return jsonify(results), 200

    except Exception as e:
        logging.error(f"Failed to connect to MongoDB or execute query: {e}")
        return jsonify({"error": str(e)}), 500

