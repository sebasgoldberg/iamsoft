# coding=utf-8
from decimal import Decimal
from base_ambiente import BaseAmbiente
import os

class Ambiente(BaseAmbiente):
  default_user = u'user'
  crontabs_dir = u'/var/spool/cron/crontabs'

  productivo=False
  admins = (
    ('admin', 'admin@xxxx.com'),
  )
  app_in_dev=None

  dominio='dominio'
  puerto_http='8080'
  puerto_https='8081'

  path_agencias='path_agencias'
  dominio_agencias='dominio_agencias'
  script_crear_agencia='script_crear_agencia'
  script_borrar_agencia='script_borrar_agencia'
  class scripts:
    activar_agencia='activar_agencia'
    desactivar_agencia='desactivar_agencia'

  class db:
    name='name'
    user='user'
    password='password'

  project_directory = '%s/' % os.path.abspath('%s/..' % os.path.split(os.path.abspath(__file__))[0])

  class email:
    
    """
    use_tls = True
    host = 'host'
    user = 'user'
    password = 'password'
    port = 587
    """

    use_tls = True
    host = 'host'
    user = 'user'
    password = 'password'
    port = 587

  class mercado_pago:
    #client_id='1495799923023357'
    #client_secret='Jxlm7QqG3y7fUtnfwsPcwTAzxCtzhBUI'
    client_id = 'client_id'
    client_secret = 'client_secret'
    password = 'password'
    email = 'email'
    nickname = 'nickname'

  class iamcast:
    dias_contrato=1
    tarifa_diaria=Decimal('0.010')
    mysql_user='mysql_user'
    mysql_pass='mysql_pass'
    agencia_git_url = 'agencia_git_url'
    db_name_ciudades = 'ciudades'

  class zonomi:
    api_key='api_key'

  class apache:
    available_sites_dir = '/etc/apache2/sites-available'

ambiente=Ambiente()