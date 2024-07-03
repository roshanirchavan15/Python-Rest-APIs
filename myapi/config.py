#!/usr/bin/python3

"""
Store useful constants in one place

NOTE: in production we would never store credentials in plain text nor version control them
"""

MONGODB_CREDS = {
    "prefix": "mongodb://",
    "username": "take_home_assessment_user",
    "password": "take_home_assessment_password",
    "host": "mongodb",
    "port": "27017",
    "database": "academicworld",
    "options": "authSource=admin",
    "find_assistant_professors_query": "myapi/queries/find_assistant_professors.json",
}

# NOTE: create the connection url for mongodb from the various componentns
MONGODB_CREDS["url"] = (
    f"{MONGODB_CREDS['prefix']}{MONGODB_CREDS['username']}:{MONGODB_CREDS['password']}"
    f"@{MONGODB_CREDS['host']}:{MONGODB_CREDS['port']}/{MONGODB_CREDS['database']}?{MONGODB_CREDS['options']}"
)

MYSQL_CREDS = {
    "host": "mysql",
    "user": "take_home_assessment_user",
    "password": "take_home_assessment_password",
    "database": "academicworld",
    "count_assistant_professors_query": "myapi/queries/count_assistant_professors.sql",
}
