#!/bin/bash

current_date=$(date +"%Y-%m-%d %H:%M:%S")
echo "($current_date) start!"

echo "($current_date) download .zip project_data folder from UIUC Box"
wget "https://uofi.box.com/shared/static/jrh1kqk5ahkfa09w8xgtvp3ybjt2c7rj" -O project_data.zip

echo "($current_date) sleep for 1 second"
sleep 1s

echo "($current_date) unzip the .zip file"
unzip project_data.zip

echo "($current_date) sleep for 1 second"
sleep 1s

echo "($current_date) download neo4j.dump file"
wget "https://uofi.box.com/shared/static/rv6f9bqq1ee8zaun9i6ilt0pmhwxl7cv" -O project_data/neo4j/neo4j.dump

echo "($current_date) end!"