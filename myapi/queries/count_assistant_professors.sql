/*
    Purpose:    Count the number of assistant professors 
                (whose position is “Assistant Professor”) among all faculty.
    Output:     Return only the number of assistant professors.
    Author:     Cristian Nuno
*/
SELECT 
    COUNT(1) AS num_records
FROM 
    academicworld.faculty
WHERE 
    position = 'Assistant Professor'
;