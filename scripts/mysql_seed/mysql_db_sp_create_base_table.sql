/*
    Author:     Cristian Nuno
    Date:       2024-04-21
    Purpose:    Create a stored procedure that:
                1. Create a base analytics table
                    + Creates an index
                    + Uses a prepare statement to execute dynamic sql
                2. Creates a view that shows publication counts per year from base analytics table
                3. Creates a view that shows keyword relevant citation scores per keyword-faculty pair from base analytics table
    Note:       Build a dynamic where statement to reflect users ability to search more broadly
*/

DROP PROCEDURE IF EXISTS academicworld.sp_create_base_table;

DELIMITER //

CREATE PROCEDURE academicworld.sp_create_base_table (
    IN keyword VARCHAR(13383),
    IN venue VARCHAR(13383),
    IN university VARCHAR(13383),
    IN faculty VARCHAR(13383),
    IN min_year INT,
    IN max_year INT
)
BEGIN
    -- instantiate existence of a useful string
    DECLARE where_clause VARCHAR(13383);

    -- Initialize WHERE clause without any conditions
    SET where_clause = 'WHERE';

    -- NOTE: as long as something was selected, add AND statement to WHERE clause
    IF keyword != 'none_selected' THEN
        SET where_clause = CONCAT(where_clause, ' k.name COLLATE utf8mb4_unicode_ci IN (', keyword COLLATE utf8mb4_unicode_ci, ') AND');
    END IF;

    -- NOTE: as long as something was selected, add AND statement to WHERE clause
    IF venue != 'none_selected' THEN
        SET where_clause = CONCAT(where_clause, ' p.venue COLLATE utf8mb4_unicode_ci IN (', venue COLLATE utf8mb4_unicode_ci, ') AND');
    END IF;

    -- NOTE: as long as something was selected, add AND statement to WHERE clause
    IF university != 'none_selected' THEN
        SET where_clause = CONCAT(where_clause, ' u.name COLLATE utf8mb4_unicode_ci IN (', university COLLATE utf8mb4_unicode_ci, ') AND');
    END IF;

    -- NOTE: as long as something was selected, add AND statement to WHERE clause
    IF faculty != 'none_selected' THEN
        SET where_clause = CONCAT(where_clause, ' f.name COLLATE utf8mb4_unicode_ci IN (', faculty COLLATE utf8mb4_unicode_ci, ') AND');
    END IF;

    -- Remove the trailing 'AND' if it exists
    IF RIGHT(where_clause, 4) = ' AND' THEN
        SET where_clause = LEFT(where_clause, LENGTH(where_clause) - 4);
    END IF;
    
    -- Append a condition to always be true if no other conditions are present
    IF where_clause = 'WHERE' THEN
        SET where_clause = CONCAT(where_clause, ' 1=1');
    END IF;

    -- DROP table if exists
    DROP TABLE IF EXISTS academicworld.base_analytics_table;

    -- NOTE: create table
    CREATE TABLE academicworld.base_analytics_table (
            row_num INT AUTO_INCREMENT,
            publication_id INT,
            publication_title VARCHAR(512),
            publication_venue VARCHAR(512),
            publication_year INT,
            publication_num_citations INT,
            keyword_id INT,
            keyword_name VARCHAR(512),
            keyword_publication_relevancy_score FLOAT, -- or DOUBLE
            faculty_id INT,
            faculty_name VARCHAR(512),
            faculty_position VARCHAR(512),
            faculty_keyword_relevancy_score FLOAT, -- or DOUBLE
            university_id INT,
            university_name VARCHAR(512),
            PRIMARY KEY (row_num),
            INDEX idx_publication_year (publication_year)
    );

    -- Prepare the dynamic SQL statement
    SET @sql = CONCAT('
        INSERT INTO academicworld.base_analytics_table
        SELECT 
            ROW_NUMBER() OVER() AS row_num,
            p.id AS publication_id,
            p.title AS publication_title,
            p.venue AS publication_venue,
            p.year AS publication_year,
            p.num_citations AS publication_num_citations,
            k.id AS keyword_id,
            k.name AS keyword_name,
            pk.score AS keyword_publication_relevancy_score,
            fp.faculty_id,
            TRIM(f.name) AS faculty_name,
            f.position AS faculty_position,
            fk.score AS faculty_keyword_relevancy_score,
            u.id AS university_id,
            u.name AS university_name
        FROM 
            academicworld.publication AS p
        INNER JOIN
            academicworld.faculty_publication AS fp
            ON p.id = fp.publication_id
            AND p.year >= ', min_year, '
            AND p.year <= ', max_year, '
        INNER JOIN
            academicworld.publication_keyword AS pk
            ON p.id = pk.publication_id
        INNER JOIN
            academicworld.keyword AS k
            ON pk.keyword_id = k.id
        INNER JOIN
            academicworld.faculty AS f
            ON fp.faculty_id = f.id
        INNER JOIN
            academicworld.university AS u
            ON f.university_id = u.id
        LEFT JOIN
            academicworld.faculty_keyword AS fk
            ON pk.keyword_id = fk.keyword_id
            AND fp.faculty_id = fk.faculty_id
        ', where_clause, '
        ;'
    );

    -- DEBUG
    -- SELECT @sql;

    -- Execute the dynamic SQL statement
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;


    -- create view for publication counts per year
    CREATE OR REPLACE VIEW academicworld.vw_publications_per_year AS (
        -- NOTE: count publications per year
        SELECT
            publication_year
            , COUNT(DISTINCT publication_id) AS num_publications
        FROM
            academicworld.base_analytics_table
        GROUP BY
            publication_year
        ORDER BY
            publication_year
    );

    -- create view for keyword relevant citation score for each faculty keyword pair
    CREATE OR REPLACE VIEW academicworld.vw_faculty_keyword_relevant_citation_score AS (
        SELECT 
            faculty_name
            , keyword_name
            , SUM(keyword_publication_relevancy_score * publication_num_citations) AS keyword_relevancy_citation_score
        FROM 
            academicworld.base_analytics_table
        GROUP BY 
            faculty_name
            , keyword_name
        ORDER BY
            keyword_name
            , keyword_relevancy_citation_score DESC
    );

    -- NOTE: create useful views for data viz
    CREATE OR REPLACE VIEW academicworld.vw_keyword_pub_count AS (
        -- NOTE: grain is one row per keyword
        SELECT 
            keyword_name
            , count(distinct publication_id) AS num_publications
        FROM 
            academicworld.base_analytics_table
        GROUP BY 
            keyword_name
        ORDER BY 
            num_publications DESC
        LIMIT
            10
    );

    CREATE OR REPLACE VIEW academicworld.vw_venue_pub_count AS (
        -- NOTE: grain is one row per venue
        SELECT 
            publication_venue
            , count(distinct publication_id) AS num_publications
        FROM academicworld.base_analytics_table
        WHERE publication_venue <> ''
        GROUP BY publication_venue
        ORDER BY num_publications DESC
        LIMIT 10
    );

    CREATE OR REPLACE VIEW academicworld.vw_university_faculty_pub_count AS (
        WITH cte AS (
            SELECT 
                t.*
                , ROW_NUMBER() OVER(PARTITION BY t.university_name ORDER BY t.num_publications DESC) AS row_num
            FROM (
                SELECT 
                    university_name
                    , faculty_name
                    , count(distinct publication_id) AS num_publications
                FROM academicworld.base_analytics_table
                GROUP BY 1, 2
            ) AS t
        )

        -- view results
        -- NOTE: grain is one row per university per top 10 faculty by pub count
        SELECT *
        FROM cte
        WHERE row_num >= 1 AND row_num <= 10
        ORDER BY university_name, row_num
    );

    CREATE OR REPLACE VIEW academicworld.vw_keyword_faculty_score AS (
        WITH cte AS (
            SELECT 
                faculty_name
                , keyword_name
                , IFNULL(faculty_keyword_relevancy_score, 0) AS faculty_keyword_relevancy_score
                , ROW_NUMBER() OVER(PARTITION BY keyword_name ORDER BY IFNULL(faculty_keyword_relevancy_score, 0) DESC) AS row_num
            FROM 
                academicworld.base_analytics_table
            GROUP BY 1, 2, 3
            )

            -- NOTE: one row per keyword per top ten faculty based on relevancy score
            SELECT *
            FROM cte
            WHERE row_num >= 1 AND row_num <= 10
            ORDER BY keyword_name, row_num
    );

    CREATE OR REPLACE VIEW academicworld.vw_publication_citation_count AS (
        -- NOTE: one row per publication
        SELECT 
            publication_id
            , publication_title
            , publication_num_citations
        FROM academicworld.base_analytics_table
        GROUP BY 1, 2, 3
        ORDER BY 3 DESC
        LIMIT 10
    );

    CREATE OR REPLACE VIEW academicworld.vw_venue_citation_count AS (
        WITH cte_publication_venue_data AS (
            SELECT 
                publication_id
                , publication_venue
                , publication_num_citations
            FROM academicworld.base_analytics_table
            WHERE publication_venue <> ''
            GROUP BY 1, 2, 3
        )

        -- NOTE: grain is one row per publication venue
        SELECT 
            publication_venue
            , SUM(publication_num_citations) AS sum_publication_num_citations
        FROM cte_publication_venue_data
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 10
    );

    CREATE OR REPLACE VIEW academicworld.vw_university_faculty_citation_count AS (
        WITH cte_publication_data AS (
            SELECT 
                publication_id
                , faculty_name
                , university_name
                , publication_num_citations
            FROM academicworld.base_analytics_table
            GROUP BY 1, 2, 3, 4
        ),

        -- NOTE: grain is one row per faculty per university per 
        cte AS (SELECT 
            faculty_name
            , university_name
            , SUM(publication_num_citations) AS sum_publication_num_citations
            , ROW_NUMBER() OVER(PARTITION BY university_name ORDER BY SUM(publication_num_citations) DESC) AS row_num
        FROM cte_publication_data
        GROUP BY 1, 2)

        -- NOTE: limit to the top ten faculty by citation per university
        SELECT *
        FROM cte
        WHERE row_num >= 1 AND row_num <= 10
    );
    

END //

DELIMITER ;
