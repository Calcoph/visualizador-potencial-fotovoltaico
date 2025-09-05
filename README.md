# Inicializar el proyecto

1. Crea una carpeta con los ficheros secretos

Esta carpeta debe llamarse `.secrets` y estar en el root del proyecto (al mismo nivel que este README.md).

Dentro de `.secrets` deben encontrarse los siguientes ficheros:
* `db_django_password.txt`: debe contener la contraseña del usuario que usará el servidor web para conectarse a la base de datos.
* `db_root_password.txt`: debe contener la contraseña del usuario root (administrador) de la base de datos.
* `db.cnf`: Debe contener esto (cambiar el valor de contraseña por el contenido de db_django_password.txt):

```
[client]
host = db
database = ehuvpf
user = django
password = <valor de db_django_password.txt>
default-character-set = utf8
```


1. Crea el directorio donde se va a almacenar la base de datos

    `mkdir ~/db-data`

1. Crear el directorio donde se almacenarán los proyectos

    `mkdir ehuvpf-projects`

1. Crea el directorio donde se va a almacenar la base de datos de OpenStreetMaps

    `mkdir ~/osm-data`

1. Descarga los datos de OpenStreetmaps. Por ejemplo para obtener los datos del país vasco:

    `wget https://download.geofabrik.de/europe/spain/pais-vasco-latest.osm.pbf`

1. Tras haber descargado el archivo `.osm.pbf`, copia la ruta *absoluta* del archivo, y úsala en el siguiente comando para importar los datos a la base de datos de OpenStreetMaps

    ```
    docker run
        -v <ruta absoluta del archivo .osm.pbf>:/data/region.osm.pbf
        -v /root/osm-data:/data/database/
        overv/openstreetmap-tile-server
        import
    ```

    Este comando utiliza la misma imagen docker que usaremos más tarde de servidor del mapa para importar los datos. Una vez completada la importación, se puede quitar la imagen con `docker rm <id del contenedor>`

1. Obten un certificado TLS para la página. Las instrucciones para esto quedan fuera del alcance de este documento.

    Si esto no es posible, habrá que modificar apache2/000-default.conf para permitir conexiones HTTP, que por defecto redirigen a la versión HTTPS de la página.

1. Cambier el nombre de dominio en la configuración. En este repositorio se asume que el dominio es "ehukhivpf.com".

    Hay menciones al dominio en los siguientes archivos: `apache2/apache2.conf`, `apache2/sites-available/000-default.conf`, `servidor/ehuvpf/ehuvpf/settings.py`

1. Asegurar de que el certificado TLS y la clave privada están en `/etc/letsencrypt/live/ehukhivpf.com/fullchain.pem` y `/etc/letsencrypt/live/ehukhivpf.com/privkey.pem` respectivamente.

    Si se desea cambiar la ruta, habrá que editar `compose.yaml`

1. Crea y ejecuta los contenedores docker

    `docker-compose up -d --build`

1. Obtener id del contenedor de db

    `docker ps`

    *Copia el id del contenedor de db*

1. Entrar a la consola del contenedor db

    `docker exec -it <id del contenedor de db> bash`

1. Intentar conectarse a la base de datos

    `mysql -p`

    Pedirá una contraseña, usa la de `.secrets/db_root_password.txt`

    Si da error *Can't connect to local server through socket '/run/mysqld/mysqld.sock' (2)* Significa que todabía no se ha inicializado la base de datos, espera un poco y vuelve a intentarlo.

1. Ejecutar los comandos de [scripts/db_init.sql](scripts/db_init.sql) (manualmente, mirando los comentarios, no como script)
1. Obtener id del contenedor de apachedjango

    `docker ps`

    *Copia el id del contenedor de apachedjango*

1. Entrar a la consola del contenedor apachedjango

    `docker exec -it <id del contenedor de apachedjango> bash`

1. Ve a /var/www/ehuvpf

    `cd /var/www/ehuvpf`

1. Compila las traducciones

    `django-admin compilemessages`

1. Inicializa la base de datos desde django

    `python3 manage.py makemigrations`

    `python3 manage.py migrate`

1. El proyecto está listo! Puedes ir a [localhost:8080](http://localhost:8080) para comprobarlo

# Configuración y administración

Para configurar la página, sigue estos pasos.

Primero crearemos un usuario administrador:

`python3 manage.py createsuperuser`

Una vez tengamos ese usuario, podremos iniciar sesión en la página web con todos los permisos disponibles, incluida la página de administración.

## Registrar usuarios

Para registrar usuarios, primero es necesario añadir los emails de los usuarios que se van a registrar a la lista de emails permitidos.
Para ello, es necesario iniciar sesión con el usuario administrador y entrar en la página de admionistración "Administrar App". Una vez estemos en la página de administración, hay que hacer click en "Allowed emails" y añadirlos.

Una vez los emails han sido añadidos, cada usuario tendrá que hacer click en "registrarse" y rellenar sus datos, incluyendo el email que se ha añadido a la lista.

Una vez se ha creado un usuario, el administrador puede modificar sus permisos desde la página de administración. Seleccionando el usuario que se quiere modificar.

Es posible crear grupos de permisos, para poder agrupar los usuarios con los mismos permisos en el mismo grupo. De esta manera si se editan los permisos del grupo, tambien se editarán los de los usuarios miembros.

# Hacer cambios en el código fuente

## Traducción

Al añadir/editar texto nuevo al proyecto hay que ejecutar el siguiente comando en el contenedor de django:

`django-admin makemessages -l eu_ES`

Si se cambia algún texto en ficheros javascript (`.js`), habrá que ejecutar la siguiente secuencia de comandos:

```
cd ../map/js
django-admin makemessages -l eu_ES --domain=djangojs
cd ../../ehuvpf
mv ../map/js/locale/eu_ES/LC_MESSAGES/djangojs.po locale/eu_ES/LC_MESSAGES/djangojs.po
```

Estos comandos generarán los archivos de localización `django.po` y `djangojs.po` respectivamente, en `locale/eu_ES/LC_MESSAGES`. Habrá que editar estos 2 archivos manualmente para traducir el texto.

Una vez traducido, hay que ejecutar `django-admin compilemessages` para que los cambios surtan efecto.

## Datos

Al cambiar los modelos de datos es necesario actualizar la base de datos para reflejar estos cambios.

Tras realizar algún cambio en el fichero `models.py` el modelo del código no se corresponderá con la base datos.

Es muy importante antes de proceder hacer una copia de la base de datos, ya que si la migración al nuevo modelo no se hace con cuidado se pueden perder datos.

Para hacer la migración, primero hay que entrar al contenedor de django.

1. Ejecutar `python3 manage.py makemigrations` para generar archivos de migración.
2. Ejecutar `python3 manage.py migrate` para ajecutar los archivos de migración.
