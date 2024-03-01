FROM ubuntu:22.04

# Remove /var/www/
RUN rm -rf /var/www/

COPY ./.secrets/db_django_password.txt /etc/secrets/db_django_password.txt
COPY ./.secrets/db.cnf /etc/secrets/db.cnf

RUN apt-get update

# Install python
RUN apt-get install python3.10 --assume-yes
RUN apt-get install python3.10-dev --assume-yes
RUN apt-get install python3-pip --assume-yes

# Install Django
RUN pip3 install Django
RUN pip3 install tzdata
# Install mysql drivers
RUN apt-get install default-libmysqlclient-dev --assume-yes
RUN apt-get install pkg-config --assume-yes
RUN pip3 install mysqlclient

# Install qgis
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install python3-qgis --assume-yes

# Install apache
RUN apt-get install apache2 --assume-yes
RUN apt-get install apache2-dev --assume-yes

# Install apache's mod_wsgi module so it works with Django
WORKDIR /root
ADD https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/5.0.0.tar.gz mod_wsgi-5.0.tar.gz
RUN tar xvfz mod_wsgi-5.0.tar.gz
RUN rm -rf mod_wsgi-5.0.tar.gz
WORKDIR /root/mod_wsgi-5.0.0
RUN ./configure --with-python=/usr/bin/python3
RUN make
RUN make install
#RUN make clean

# Update apache2.conf to include mod_wsgi
COPY apache2/apache2.conf /etc/apache2/apache2.conf
COPY apache2/sites-available /etc/apache2/sites-available

RUN a2dissite 000-default.conf

RUN apachectl stop

WORKDIR /var/www/ehuvpf/
