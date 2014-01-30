#!/bin/bash

### Variables globales
WD="$(readlink -f "$(dirname "$0")")"

INSTALL_FRAMEWORK='X'
INSTALL_IAMPACKS='X'
INSTALL_CIUDADES='X'
INSTALL_IAMSOFT='X'

if [ "$1" = '--only-iamsoft' ]
then
  INSTALL_FRAMEWORK=' '
  INSTALL_IAMPACKS=' '
  INSTALL_CIUDADES=' '
fi

function install_django_crispy_forms
{
  pip install --upgrade django-crispy-forms

  if [ $? -ne 0 ]
  then
    echo "ERROR: Error al ejecutar 'pip install --upgrade django-crispy-forms'"
    exit 1
  fi
}

function install_standard_framework
{
  if [ "$INSTALL_FRAMEWORK" = ' ' ]
  then
    return 0
  fi

  apt-get update

  apt-get -y install make
  apt-get -y install bc
  apt-get -y install apache2
  apt-get -y install mysql-server
  apt-get -y install cython
  apt-get -y install libapache2-mod-wsgi
  apt-get -y install python-mysqldb
  apt-get -y install python-imaging
  apt-get -y install mercurial #necesario para hacer el pull de algunos pagetes a ser instalados
  apt-get -y install unzip
  apt-get -y install gettext
  apt-get -y install python-pip
  apt-get -y install curl

  pip install Django==1.4.3

# Instalacion de paquete para manejo de thumbnails
  pip install django-imagekit==2.0.4
  pip install requests

# Instalacion de PyYaml
  mkdir pyyaml
  cd pyyaml
  hg clone https://bitbucket.org/xi/pyyaml
  cd pyyaml
  python setup.py install
  cd ../..
  rm -rf pyyaml

# Generación de los directorios donde estarán los certificados
  if [ ! -d /etc/apache2/ssl ]
  then
    mkdir /etc/apache2/ssl 
  fi

  a2enmod ssl
  a2enmod rewrite
  service apache restart

  apt-get -y install python-coverage

  install_django_crispy_forms

  easy_install South
  pip install django-cities-light
}

function install_ciudades
{
  if [ "$INSTALL_CIUDADES" = ' ' ]
  then
    return 0
  fi

  cd "$WD"
  cd ..

  if [ -d "ciudades" ]
  then
    echo "ERROR: Parecería ser que ya ha sido instalado ciudades."
    return 1
  fi

  git clone https://github.com/sebasgoldberg/ciudades.git

  cd ciudades

  ./install
}

function install_iampacks
{
  if [ "$INSTALL_IAMPACKS" = ' ' ]
  then
    return 0
  fi

  echo "Se realiza la instalación de los paquetes de iamsoft."

  #DIST_PACKAGE_DIR="$(readlink -f "$(dirname "$(python -c 'import django;print django.__file__')")/..")"
  DIST_PACKAGE_DIR="/usr/local/lib/python2.7/dist-packages"

  if [ $? -ne 0 ]
  then
    echo "ERROR: No se pudo obtener el directorio dist-packages de python."
    exit 1
  fi

  cd "$DIST_PACKAGE_DIR"

  if [ -d "iampacks" ]
  then
    echo "ERROR: Parecería ser que ya ha sido instalado iampacks."
    return 1
  fi

  mkdir iampacks
  cd iampacks
  touch __init__.py

  git clone https://github.com/sebasgoldberg/cross.git
  git clone https://github.com/sebasgoldberg/agencia.git

}

function get_ambient_parameter
{
  echo "$(python -c "from iamsoft.ambiente import ambiente; print ambiente.$1" )"
}

function crear_usuario_y_base_datos
{
  cd "$(readlink -f "$(dirname "$0")")"

  DB_NAME="$(get_ambient_parameter "db.name")"
  DB_USER="$(get_ambient_parameter "db.user")"
  DB_PASS="$(get_ambient_parameter "db.password")"

  echo "Se procede a crear base de datos y usuario de base de datos, por favor introduzca la contraseña del usuario root:"

  (echo "create database $DB_NAME character set utf8;"
  echo "create user '$DB_USER'@'localhost' identified by '$DB_PASS';"
  echo "grant all on $DB_NAME.* to $DB_USER;"
  ) | mysql -u root -p

  if [ $? -ne 0 ]
  then
    echo "ERROR: Ha ocurrido un error al intentar crear usuario y base de datos de iamsoft."
    return 1
  fi

}

function create_ambient_dir
{
  DIR="$(get_ambient_parameter "$1")"

  if [ $? -ne 0 ]
  then
    echo 'ERROR: No se ha podido obtener el path de agencias del ambiente.'
    return 1
  fi

  if [ ! -d "$DIR" ]
  then
    mkdir "$DIR"
    if [ $? -ne 0 ]
    then
      echo "Error al crear '$DIR'"
      exit 1
    fi
  fi

  chgrp -R www-data "$DIR"

  if [ $? -ne 0 ]
  then
    echo "Error al cambiar grupo a www-data '$DIR'"
    exit 1
  fi
}

function install_iamsoft
{
  if [ "$INSTALL_IAMSOFT" = ' ' ]
  then
    return 0
  fi

  echo "Se realiza la instalación del proyecto iamsoft."

  IAMSOFT_WD="$WD"

  AMBIENTE_FILE="$IAMSOFT_WD/iamsoft/ambiente.py"
  AMBIENTE_TEMPLATE_FILE="$IAMSOFT_WD/iamsoft/ambiente.default.py"

  if [ ! -f "$AMBIENTE_FILE" ]
  then
    echo "ERROR: Archivo $AMBIENTE_FILE no encontrado. Copiar $AMBIENTE_TEMPLATE_FILE y editar la configuración correspondiente."
    exit 1
  fi  

  create_ambient_dir 'path_agencias'
  create_ambient_dir 'log_directory'

  # @todo asignar permisos al usuario para el archivo de log
  LOG_FILE="$(get_ambient_parameter "log_file")"
  touch "$LOG_FILE"
  chmod 775 "$LOG_FILE"
  sudo chgrp www-data "$LOG_FILE"

  mkdir "$IAMSOFT_WD/collectedstatic"

  "$IAMSOFT_WD/manage.py" collectstatic

  crear_usuario_y_base_datos

  "$IAMSOFT_WD/manage.py" syncdb
}

install_standard_framework

install_iampacks

install_ciudades

install_iamsoft

exit 0


