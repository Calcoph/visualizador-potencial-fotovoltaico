FROM mysql:8.3.0

COPY .secrets/db_django_password.txt /etc/secrets/db_django_password.txt

# Scripts are renamed this way since the execution order is alphabetical
COPY create_user.sh /docker-entrypoint-initdb.d/000-create_user.sh
COPY init_db.sql /docker-entrypoint-initdb.d/001-init_db.sql
