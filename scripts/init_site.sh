#! /bin/bash

if [ ! -e "ehuvpf-projects" ]; then
    echo "Creando ehuvpf-projects"
    mkdir "ehuvpf-projects"
fi

if [ ! -e "$HOME/db-data" ]; then
    echo "Creando ~/db-data"
    mkdir -p "$HOME/db-data"
fi

if [ ! -e "$HOME/osm-data" ]; then
    echo "Creando ~/osm-data"
    mkdir "$HOME/osm-data"
fi

if [ ! -e ".secrets" ]; then
    echo "Creando .secrets"
    mkdir ".secrets"
fi

django_pass=""
if [ ! -e "docker/apachedjango/.secrets/db_django_password.txt" ]; then
    read -p "Genere una contraseña para el usuario 'django' de la base de datos: " -s django_pass
    echo $django_pass > docker/apachedjango/.secrets/db_django_password.txt
    echo "Contraseña guardada en docker/apachedjango/.secrets/db_django_password.txt"
else
    echo "Usando contraseña del usuario 'django' de la base de datos (docker/apachedjango/.secrets/db_django_password.txt)"
    django_pass=$(cat docker/apachedjango/.secrets/db_django_password.txt)
fi

# docker/db/.secrets/db_django_password.txt is always recreated in case django_pass changes
echo $django_pass > docker/db/.secrets/db_django_password.txt
echo "Contraseña guardada en docker/db/.secrets/db_django_password.txt"

if [ ! -e ".secrets/db_root_password.txt" ]; then
    read -p "Genere una contraseña para el usuario 'root' de la base de datos: " -s root_pass
    echo $root_pass > .secrets/db_root_password.txt
    echo "Contraseña guardada en .secrets/db_root_password.txt"
else
    echo "Usando contraseña del usuario 'root' de la base de datos (.secrets/db_root_password.txt)"
fi

# .secrets/db.cnf is always recreated in case django_pass changes
echo "[client]
host = db
database = ehuvpf
user = django
password = $django_pass
default-character-set = utf8
" > .secrets/db.cnf


osm_data="$PWD/pais-vasco-latest.osm.pbf"

if [ ! -e $osm_data ]; then
    echo "Descargando datos de OSM"
    wget https://download.geofabrik.de/europe/spain/pais-vasco-latest.osm.pbf
else
    echo "Saltando descarga de datos de OSM data ya que el archivo existe"
fi

echo "Importando datos de OSM"
docker run --cidfile importcid.tmp -v osm_data -v $PWD/ignore/osm-data:/data/database overv/openstreetmap-tile-server import

docker rm $(cat importcid.tmp)
rm importcid.tmp

echo
echo "Proyecto inicializado"
