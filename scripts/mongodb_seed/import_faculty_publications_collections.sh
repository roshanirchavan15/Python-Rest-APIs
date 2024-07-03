#!/bin/bash

current_date=$(date +"%Y-%m-%d %H:%M:%S")

echo "starting at ($current_date)"

echo "($current_date) sleep for 40 seconds because of latency of myapi_volume populating the project_data dir"
sleep 40s

echo "($current_date) now that we've slept, let's traverse the project_data dir to ensure all is in its right place"

echo "($current_date) import faculty data into mongodb through shared myapi_volume"
mongoimport --username="take_home_assessment_user" --password="take_home_assessment_password" --host="localhost:27017" --db="academicworld" --authenticationDatabase="admin" --drop --collection="faculty" --file="project_data/mongodb/faculty.json"
echo "($current_date) finish importing faculty data into mongodb"

echo "($current_date) import publications data into mongodb through shared myapi_volume"
mongoimport --username="take_home_assessment_user" --password="take_home_assessment_password" --host="localhost:27017" --db="academicworld" --authenticationDatabase="admin" --drop --collection="publications" --file="project_data/mongodb/publications.json"
echo "($current_date) finish importing publications data into mongodb"
