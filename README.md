# Inicializar el proyecto

1. Obten un certificado TLS para la página. Las instrucciones para esto quedan fuera del alcance de este documento. Asegúrate que el campo "Common Name" es el dominio de la página web

    Para entornos de desarrollo, bastaría con un certificado auto-firmado. Instrucciones: https://www.baeldung.com/openssl-self-signed-cert

    Si esto no es posible, habrá que modificar apache2/000-default.conf para permitir conexiones HTTP, que por defecto redirigen a la versión HTTPS de la página.

1. Cambiar el nombre de dominio en la configuración. En este repositorio se asume que el dominio es "ehukhivpf.com".

    Hay menciones al dominio en los siguientes archivos: `apache2/apache2.conf`, `apache2/sites-available/000-default.conf`, `servidor/ehuvpf/ehuvpf/settings.py`

1. Asegurar de que el certificado TLS y la clave privada están en `/etc/letsencrypt/live/ehukhivpf.com/fullchain.pem` y `/etc/letsencrypt/live/ehukhivpf.com/privkey.pem` respectivamente.

    Si se desea cambiar la ruta, habrá que editar `compose.yaml`

1. Ejecuta el script de inicialización, que hará lo siguiente:

    * Crear directorios necesarios para el proyecto
    * Descargar los el mapa del país vasco de OpenStreetMaps (https://download.geofabrik.de/europe/spain/pais-vasco-latest.osm.pbf)
    * Importar el mapa a la base de datos

    Asegúrate de que estás en la carpeta principal del proyecto (es decir, si ejecutas `ls | grep README.md` deberías ver este fichero) y ejecuta el script:
    `./scripts/init_site.sh`

1. Crea y ejecuta los contenedores docker

    `docker compose up -d --build`

1. El proyecto está listo! Puedes ir a [localhost:443](https://localhost:443) para comprobarlo. Debido al posible cambio de nombre de dominio, habrá que editar `www/js/map.js` para cargar el mapa desde `localhost:8081` en vez de `ehukhivpf.com:8081`.

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
