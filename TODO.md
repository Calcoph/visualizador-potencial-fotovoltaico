Cambiar Debug=true a Debug=false de django

Cambiar SECRET_KEY de django y hacerla secreta (con `python3 manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

Añadir anti-csrf

Añadir transacciones django

En prácticamente todos los inputs/edits hay que handlear el return en vez de simplemente que se enseñe un json/success/whatever que no es una página html
