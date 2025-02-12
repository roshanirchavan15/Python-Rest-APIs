# Importing necessary modules and connection functions
from config import MYSQL_CREDS
from mysql.connector import connect, Error


# Function to fetch the top cited faculty
def get_top_cited(year):
    # jsonify is used to create a JSON response from a Flask view function
    from flask import jsonify
    try:
        # Database connection
        with connect(
            host=MYSQL_CREDS["host"],
            user=MYSQL_CREDS["user"],
            password=MYSQL_CREDS["password"],
            database=MYSQL_CREDS["database"],
        ) as connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        f.id AS faculty_id,
                        f.name AS faculty_name,
                        COUNT(p.id) AS num_publications
                    FROM 
                        faculty f
                    JOIN 
                        faculty_publication fp ON f.id = fp.faculty_id
                    JOIN 
                        publication p ON fp.publication_id = p.id
                    WHERE 
                        p.year = %s
                    GROUP BY 
                        f.id, f.name
                    HAVING 
                        COUNT(p.id) > 10 AND AVG(p.num_citations) > 10
                    ORDER BY 
                        num_publications DESC;
                """
                cursor.execute(query, (year,))
                results = cursor.fetchall()
                formatted_results = [
                    {"faculty_id": row[0], "faculty_name": row[1], "num_publications": row[2]}
                    for row in results
                ]
                return jsonify(formatted_results), 200
    except Error as e:
        return jsonify({"error": f"Error connecting to MySQL: {e}"}), 500
