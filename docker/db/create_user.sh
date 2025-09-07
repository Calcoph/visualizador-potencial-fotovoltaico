#!/bin/bash

mysql -u root -p"$(cat /run/secrets/db_root_password)" -Bse "CREATE USER IF NOT EXISTS 'django'@'%' IDENTIFIED BY '$(cat /etc/secrets/db_django_password.txt)';"
