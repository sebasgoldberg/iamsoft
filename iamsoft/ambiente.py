# coding=utf-8
class ambiente:
  productivo=False
  app_in_dev=None

  #dominio='iamsoft.no-ip.org:8080'
  dominio='iamsoft.com.ar:8080'

  class db:
    name='iamsoft'
    user='iamsoft'
    password='IamsofT9123'

  project_directory = '/home/cerebro/django-projects/iamsoft/'

  class email:
    host = 'smtp.gmail.com'
    user = 'contacto.iamsoft@gmail.com'
    password = 'IamsofT9123'
    port = 587

