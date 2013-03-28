# coding=utf-8
class ambiente:
  productivo=False
  admins = (
    ('Sebastian', 'sebas.goldberg@gmail.com'),
  )
  app_in_dev=None

  #dominio='iamsoft.no-ip.org:8080'
  dominio='iamsoft.com.ar:8080'
  path_agencias='/home/cerebro/django-projects'
  script_crear_agencia='/home/cerebro/django-projects/install-agencia/crear_agencia.sh'
  script_borrar_agencia='/home/cerebro/django-projects/install-agencia/borrar_agencia.sh'

  class db:
    name='iamsoft'
    user='iamsoft'
    password='IamsofT9123'

  project_directory = '/home/cerebro/django-projects/iamsoft/'

  class email:
    host = 'smtp.gmail.com'
    user = 'iamsoft.contacto@gmail.com'
    password = 'cerebrin'
    port = 587

  class mercado_pago:
    #client_id='1495799923023357'
    #client_secret='Jxlm7QqG3y7fUtnfwsPcwTAzxCtzhBUI'
    client_id = '17363745234438'
    client_secret = 'QmWNS0U8EbMDz0lphSFnudphqeBDb7tF'
    password = 'qatest7942'
    email = 'test_user_27209785@testuser.com'
    nickname = 'TT632250'
