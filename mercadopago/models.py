from django.db import models
import requests
import json
from django.conf import settings

# Create your models here.
class MercadoPago(object):
  
  MIME_JSON = "application/json"
  MIME_FORM = "application/x-www-form-urlencoded"

  def __init__(self,client_id=settings.AMBIENTE.mercado_pago.client_id,client_secret=settings.AMBIENTE.mercado_pago.client_secret):
    self.client_id=client_id
    self.client_secret=client_secret

  def get_access_token(self):
    params={
      'grant_type': 'client_credentials',
      'client_id': self.client_id,
      'client_secret': self.client_secret
      }
    response=requests.post('https://api.mercadolibre.com/oauth/token',params)
    return response.json()['access_token']

  def crear_usuario_prueba(self,site_id='MLA'):
    data=json.dumps({"site_id":site_id})
    response=requests.post(
      'https://api.mercadolibre.com/users/test_user?access_token=%s'%self.get_access_token(),
      data=data,
      headers={'Content-type':self.MIME_JSON, 'Accept':self.MIME_JSON}
      ).json()
    return response

  def get_pago(self,id_pago):
    response=requests.get(
      'https://api.mercadolibre.com/collections/%s?access_token=%s'%(id_pago,self.get_access_token()),
      headers={'Accept':self.MIME_JSON}
      )
    return response.json()

  def get_pagos(self):
    response=requests.get(
      'https://api.mercadolibre.com/collections/search?access_token=%s'%self.get_access_token(),
      headers={'Accept':self.MIME_JSON}
      )
    return response.json()

  def search_pagos_by_external_reference(self,external_reference):
    response=requests.get(
      'https://api.mercadolibre.com/collections/search?access_token=%s&external_reference=%s'%(self.get_access_token(),external_reference),
      headers={'Accept':self.MIME_JSON}
      )
    return response.json()

  def get_pago_notificado(self,id_notificacion_pago):
    response=requests.get(
      'https://api.mercadolibre.com/collections/notifications/%s?access_token=%s'%(id_notificacion_pago,self.get_access_token()),
      headers={'Accept':self.MIME_JSON}
      )
    return response.json()
    
  
