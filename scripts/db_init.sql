-- Para inicializar hace falta ejecutar estos comandos.
-- Algunos requieren de input manual (para la contraseña, por ejemplo).
-- Por lo que no se debería ejecutar como script, si no que manualmente
-- leyendo los comentarios.

CREATE DATABASE ehuvpf;
USE ehuvpf;

-- ESTE COMANDO REQUIERE EDICIÓN MANUAL
-- Al final del comando, se debe poner la contraseña de django, que está en db_django_password.txt
CREATE USER IF NOT EXISTS 'django'@'%' IDENTIFIED BY '<contraseña contenida en db_django_password.txt>';
CREATE USER IF NOT EXISTS 'django'@'%' IDENTIFIED BY 'GVRHM@qrU@N*6WZ9rW#^acx^^4BXT6qVGafbe%bk6qAV2fyE4fefCbQTvBjHjWP#';

GRANT SELECT ON ehuvpf.* TO 'django'@'%';
GRANT CREATE ON ehuvpf.* TO 'django'@'%';
GRANT ALTER ON ehuvpf.* TO 'django'@'%';
GRANT INSERT ON ehuvpf.* TO 'django'@'%';
GRANT INDEX ON ehuvpf.* TO 'django'@'%';
GRANT REFERENCES ON ehuvpf.* TO 'django'@'%';
GRANT UPDATE ON ehuvpf.* TO 'django'@'%';
