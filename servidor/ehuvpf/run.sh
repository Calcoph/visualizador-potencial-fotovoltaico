#!/bin/bash

db_connection=1;

for i in {1..60};do
    echo "checking DB connection"
    python3 manage.py check --database default
    if [ $? -eq 0 ];then
        echo "DB connection check OK"
        db_connection=0
        break
    else
        echo "DB connection failed. Checking again in 3 seconds"
        sleep 3
    fi
done

if [ $db_connection -eq 1]; then
    echo "Maximum DB connection check retries failed. Exiting"
    exit 1
fi

django-admin compilemessages
python3 manage.py makemigrations
python3 manage.py migrate

echo "Running ApacheDjango"
apachectl -D FOREGROUND
