#!/usr/bin/python3

"""
Test the ability to connect with both the mysql and mongodb databases
"""

import json
import logging
import os
import pathlib


from mysql.connector import connect, Error

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


from config import MONGODB_CREDS, MYSQL_CREDS


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

logging.info("pull in relevant queries")
with open(MYSQL_CREDS["count_assistant_professors_query"], "r") as mysql_file:
    logging.info("pull in mysql query")
    mysql_query = mysql_file.read()

with open(MONGODB_CREDS["find_assistant_professors_query"], "r") as mongodb_file:
    logging.info("pull in mongodb query")
    mongodb_query = json.load(mongodb_file)


logging.info("connect to the mysql db and view test connection")
try:
    logging.info("attempting to connect to mysql db...")
    with connect(
        # NOTE: hard coding credentials is not something one should do in PROD
        host=MYSQL_CREDS["host"],
        user=MYSQL_CREDS["user"],
        password=MYSQL_CREDS["password"],
        database=MYSQL_CREDS["database"],
    ) as connection:
        with connection.cursor() as cursor:
            logging.info(f"beginning to execute query..\n{mysql_query}")
            cursor.execute(mysql_query)
            logging.info("connection to mysql db successful!")
            mysql_result = cursor.fetchall()
            logging.info(f"there are {len(mysql_result)} query results")
            logging.info(f"the results are: {mysql_result}")
except Error as e:

    logging.info(f"failed to connect to mysql db: {e}")

with MongoClient(MONGODB_CREDS["url"]) as client:
    try:
        # The ping command is cheap and does not require auth.
        client.admin.command("ping")
        logging.info("connection to mongodb is successful")
    except ConnectionFailure as e:

        logging.info(f"failed to connect to mongodb: {e}")

    logging.info(f"use {MONGODB_CREDS['database']} db")
    db = client[MONGODB_CREDS["database"]]

    logging.info("switch to relevant collection")
    faculty_collection = db["faculty"]

    logging.info(f"the query we are executing for mongodb is: \n{mongodb_query}")
    # Execute the aggregation query
    results_iterator = faculty_collection.aggregate(mongodb_query)
    assistant_professor_list = [doc["name"] for doc in results_iterator]
    logging.info(f"there are {len(assistant_professor_list)} results")
    logging.info(f"here's the first 5 results: {assistant_professor_list[0:5]}")
