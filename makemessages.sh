#!/bin/bash
if [ $# -ne 1 ]
then
  echo "ERROR: Uso: $0 <IDIOMA>"
  exit 1
fi

IDIOMA="$1"

./manage.py makemessages -l "$IDIOMA" "--ignore=home/*" "--ignore=iamcast/*" "--ignore=mercadopago/*"

exit "$?"
