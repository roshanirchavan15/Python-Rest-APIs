#!/bin/bash

echo "sleep for 40 seconds because of latency of myapi_volume populating the project_data dir"
sleep 40s

# Check if project_data folder exists
if [ -d "project_data" ]; then
    echo "project_data folder exists"
    
    # Check if mysql folder exists
    if [ -d "project_data/mysql" ]; then
        echo "mysql folder exists"
        
        # Check if academicworld.sql exists
        if [ -f "project_data/mysql/academicworld.sql" ]; then
            echo "academicworld.sql exists"
            echo "import academicworld data into mysql through shared myapi_volume"
            mysql --user="take_home_assessment_user" --password="take_home_assessment_password" --database="academicworld" < "project_data/mysql/academicworld.sql"
            echo "finish importing academicworld data into mysql"
        else
            echo "academicworld.sql does not exist"
        fi
        
    else
        echo "mysql folder does not exist"
    fi
    
else
    echo "project_data folder does not exist"
fi
