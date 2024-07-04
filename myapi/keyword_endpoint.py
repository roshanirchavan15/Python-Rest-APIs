# from myapi import db
import os
import logging
import pathlib

from config import MYSQL_CREDS
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


