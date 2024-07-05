## Infrastructure Setup

## Part 1 : Clean and Standardize Phone Numbers

I created a feature branch feature/add-clean-phone-numbers-api and merged it with the main branch

### Steps

1. **Read SQL Query**:
   - The SQL query located in `myapi/queries/distinguished_professors.sql` is used to fetch the professors' data.

2. **Database Connection**:
   - Establish a connection to the MySQL database using credentials stored in the `MYSQL_CREDS` dictionary.
   - Execute the query to retrieve `faculty_id` and `phone` columns.

3. **Phone Number Parsing**:
   - A function `parse_phone_number(phone)` is created to clean and standardize the phone numbers:
     - Remove non-numeric characters.
     - Ensure the phone number is exactly 10 digits long.
     - Prefix a leading '1' to form an 11-digit phone number.
     - Return `None` if the phone number is invalid or missing.

4. **Data Processing**:
   - Iterate over the query results.
   - For each entry, parse the phone number and, if valid, store the `faculty_id` and cleaned phone number in a list.

5. **Generate Timestamp**:
   - Generate a timestamp in the `America/Los_Angeles` timezone using the format `YYYYMMDD_HHmmss`.

6. **Write to CSV**:
   - Create a CSV file named `clean_phone_numbers_YYYYMMDD_HHmmss.csv` in the `myapi/data/` directory.
   - Write the `faculty_id` and `clean_phone` columns to the CSV file using a pipe (`|`) delimiter.

## Part 2: Python RESTful API 

Another feature branch was created feature/add-python-RESTful-api which was later merged with the main branch

1. **Keyword_endpoint**

In the keyword_endpoint we are creating, updating, retrieving, and deleting keywords in a MySQL and MongoDB database. The following endpoints were implemented to handle these operations:

**create()**
This function handles the creation/insertion of keywords in the MySQL database. If the keyword already exists, it updates the existing entry; otherwise, it inserts a new entry.

**get_popular()**
This function retrieves the top-10 most popular keywords from the MongoDB database for a specified date range. It uses MongoDB's aggregation framework to match documents within the date range, unwind the keywords array, group by keyword name, sort by publication count, and limit the results to the top-10.

**update_keyword()**
This function updates the name of an existing keyword in the MySQL database. It checks if the keyword exists and performs the update if found.

**delete_keyword()**
This function deletes a keyword and its associations from the MySQL database. It first checks if the keyword exists, then deletes it from related tables and finally removes the keyword entry itself. Here the id column in the Keyword table is a foreign key for faculty_keyword tables and publication_keyword tables. I was receiving an error when deleting "id" only from the keyword table. After my research I concluded that the foreign keys shall be deleted for the successful execution.

2. **faculty-top-cited/{year} endpoint**

Created a function  to fetch the top cited faculty members for a specified year from a MySQL database. The function returns faculty members who have more than 10 publications and an average of more than 10 citations per publication for the given year.

**get_top_cited(year)**
The function takes year as an input parameter. It connects to the MySQL database using credentials from MYSQL_CREDS. It executes a query to fetch faculty members who have more than 10 publications and an average of more than 10 citations per publication for the given year.
The results are formatted into a JSON response and returned with a status code of 200. If there is an error connecting to the database, it returns a JSON response with the error message and a status code of 500.
