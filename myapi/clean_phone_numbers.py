import pytz
import csv
from datetime import datetime
from mysql.connector import connect, Error
from config import MYSQL_CREDS


# Function to get the phone numbers
def parse_phone_number(phone):
    if phone:
        # Remove any non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        # Ensure the phone number is 10 digits
        if len(phone) == 10:
            return '1' + phone
    return None


# opening the directory to get the SQL query to get the faculty id, phone
with open(
    "myapi/queries/distinguished_professors.sql",
    "r",
    encoding="utf8"
) as mysql_file:
    mysql_query = mysql_file.read()

try:
    # database connection
    with connect(
        # NOTE: hard coding credentials is not something one should do in PROD
        host=MYSQL_CREDS["host"],
        user=MYSQL_CREDS["user"],
        password=MYSQL_CREDS["password"],
        database=MYSQL_CREDS["database"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(mysql_query)
            mysql_result = cursor.fetchall()  # fetching the result
except Error as e:

    print(f"failed to connect to mysql db: {e}")

# List to later convert into CSV. List will store faculty_id, phone
cleaned_data = []
for x in mysql_result:
    faculty_id, phone = x[0], x[1]  # splitting the tuple
    parse_phone = parse_phone_number(phone)
    if parse_phone:
        cleaned_data.append([faculty_id, parse_phone])

timestamp = datetime.now(
    pytz.timezone('America/Los_Angeles')
    ).strftime('%Y%m%d_%H%M%S')
filename = "myapi/data/clean_phone_numbers_" + timestamp + ".csv"

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter='|')
    csvwriter.writerow(['faculty_id', 'clean_phone'])  # Write header
    csvwriter.writerows(cleaned_data)
