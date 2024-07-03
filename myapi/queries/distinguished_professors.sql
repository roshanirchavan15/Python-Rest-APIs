/*
    Purpose:    Find the phone number for each distinguished professor
    Output:     Return the faculty id and the phone number of the faculty
    Author:     Cristian Nuno
*/
SELECT 
  id
  , phone
FROM 
 faculty
where 
 position = 'Distinguished Professor'
;