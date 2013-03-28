#!/bin/bash
if [ $# -ne 10 ]
then
  echo "$0 <ID_AGENCIA> <SLUG_AGENCIA> <GMAIL_USER> <GMAIL_PASS> <DOMINIO> <UBICACION_INSTALACION> <SUPER_USUARIO> <CLAVE_SUPER_USUARIO> <SCRIPT_CREACION> <URL_RESPUESTA>"
  exit 1
fi

ID_AGENCIA="$1"
SLUG_AGENCIA="$2"
GMAIL_USER="$3"
GMAIL_PASS="$4"
DOMINIO="$5"
UBICACION_INSTALACION="$6"
SUPER_USUARIO="$7"
CLAVE_SUPER_USUARIO="$8"
SCRIPT_CREACION="$9"
URL_RESPUESTA="${10}"

"$SCRIPT_CREACION" "$ID_AGENCIA" "$SLUG_AGENCIA" "$GMAIL_USER" "$GMAIL_PASS" "$DOMINIO" "$UBICACION_INSTALACION" "$SUPER_USUARIO" "$CLAVE_SUPER_USUARIO"

wget "${URL_RESPUESTA}?id_agencia=${ID_AGENCIA}&resultado=${?}" -O /dev/null

exit $?

