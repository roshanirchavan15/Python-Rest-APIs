from config import MYSQL_CREDS
from mysql.connector import connect, Error

def get_top_cited(year):
    from flask import jsonify
    try:
        with connect(
            # NOTE: hard coding credentials is not something one should do in PROD
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
        # logging.error(f"Error connecting to MySQL: {e}")
        return jsonify({"error": f"Error connecting to MySQL: {e}"}), 500
