# Inicializar el proyecto

1. Crea una carpeta con los ficheros secretos

Esta carpeta debe llamarse `.secrets` y estar en el root del proyecto (al mismo nivel que este README.md).

Dentro de `.secrets` deben encontrarse los siguientes ficheros:
* `db_django_password.txt`: debe contener la contraseña del usuario que usará el servidor web para conectarse a la base de datos.
* `db_root_password.txt`: debe contener la contraseña del usuario root (administrador) de la base de datos.

2. Crea el directorio donde se va a almacenar la base de datos

`mkdir ~/db-data`

3. Crear el directorio donde se almacenarán los proyectos

`mkdir ehuvpf-projects`

4. Crea y ejecuta los contenedores docker

`docker-compose up -d --build`

5. Obtener id del contenedor de db

`docker ps`

*Copia el id del contenedor de db*

6. Entrar a la consola del contenedor db

`docker exec -it <id del contenedor de db> bash`

7. Intentar conectarse a la base de datos

`mysql -p`

Pedirá una contraseña, usa la de `.secrets/db_root_password.txt`

Si da error *Can't connect to local server through socket '/run/mysqld/mysqld.sock' (2)* Significa que todabía no se ha inicializado la base de datos, espera un poco y vuelve a intentarlo.

8. Ejecutar los comandos de [scripts/db_init.sql](scripts/db_init.sql) (manualmente, mirando los comentarios, no como script)
9. Obtener id del contenedor de apachedjango

`docker ps`

*Copia el id del contenedor de apachedjango*

10. Entrar a la consola del contenedor apachedjango

`docker exec -it <id del contenedor de apachedjango> bash`

11. Ve a /var/www/ehuvpf

`cd /var/www/ehuvpf`

12. Compila las traducciones

`django-admin compilemessages`

13. Inicializa la base de datos desde django

`python3 manage.py makemigrations`

`python3 manage.py migrate`

14. El proyecto está listo! Puedes ir a [localhost:8080](http://localhost:8080) para comprobarlo

# Hacer cambios en el código fuente

## Traducción

Al añadir/editar texto nuevo al proyecto hay que ejecutar el siguiente comando en el contenedor de django:

`django-admin makemessages -l eu_ES`

De esta manera se actualizará el fichero de localización. Tras traducir el texto,
hay que ejecutar `django-admin compilemessages` para que los cambios surtan efecto.

## Datos

Al cambiar los modelos de datos es necesario actualizar la base de datos para reflejar estos cambios.

Tras realizar algún cambio en el fichero `models.py` el modelo del código no se corresponderá con la base datos.

Es muy importante antes de proceder hacer una copia de la base de datos, ya que si la migración al nuevo modelo no se hace con cuidado se pueden perder datos.

Para hacer la migración, primero hay que entrar al contenedor de django.

1. Ejecutar `python3 manage.py makemigrations` para generar archivos de migración.
2. Ejecutar `python3 manage.py migrate` para ajecutar los archivos de migración.
