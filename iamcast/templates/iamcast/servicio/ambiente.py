# coding=utf-8
from iampacks.cross.ambiente.models import BaseAmbiente
import os

id_agencia='{{agencia.get_alfa_id}}'

class Ambiente(BaseAmbiente):
  productivo=False
  app_in_dev=None

  id_agencia=id_agencia
  site_id=id_agencia

  dominio='{{agencia.get_dominio}}'
  puerto_http='{{agencia.get_puerto_http}}'
  puerto_https='{{agencia.get_puerto_https}}'

  admins = (
  {%for nombre, mail in admins%}
    ('{{nombre}}', '{{mail}}'),
  {%endfor%}
  )

  class sitio:
    class externo:
      url = None

  class db:
    name=id_agencia
    user=id_agencia
    password='{{password}}'
    class root:
      password='{{root_password}}'

  class ciudades:
    class db:
      name='ciudades'

  project_directory = '%s/' % os.path.abspath('%s/..' % os.path.split(os.path.abspath(__file__))[0])
  wsgi_dir = os.path.dirname(__file__)

  class email:
    host = '{{agencia.get_mail_server}}'
    user = '{{agencia.get_mail_user}}'
    password = '{{agencia.get_mail_password}}'
    port = {{agencia.get_mail_port}}

  class zonomi:
    api_key = '{{agencia.get_zonomi_api_key}}'

  class backup:
    user = None
    host = None
    destination = None

ambiente=Ambiente()
