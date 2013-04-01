"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from iamcast.models import Agencia, Contrato
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ValidationError

class IamCastTest(TestCase):
  def test_obtencion_proximo_pago(self):
    user = User.objects.create_user(
      'test_obtencion_proximo_pago', 
      'test_obtencion_proximo_pago@gmail.com', 
      's3cr3t'
    )

    user.save()

    agencia=Agencia(
      user=user,
      nombre=u'test_obtencion_proximo_pago',
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234'
    )
    
    agencia.save()

    pago=agencia.proximo_pago()

    self.assertTrue(agencia.fecha_vencimiento()<pago.contratoagencia.fecha_inicio)
    self.assertEqual(pago.id,agencia.proximo_pago().id)
    self.assertEqual(pago.item_unit_price,agencia.proximo_pago().item_unit_price)
    self.assertEqual(pago.item_unit_price_as_str(),agencia.proximo_pago().item_unit_price_as_str())
    self.assertEqual(pago.md5(),agencia.proximo_pago().md5())
    self.assertTrue(not pago.contratoagencia.vencido())
    self.assertTrue(agencia.en_periodo_prueba())
    self.assertFalse(agencia.vencida())
    self.assertFalse(agencia.borrada())

  def test_vencimiento_contrato(self):
    
    user = User.objects.create_user(
      'test_vencimiento_contrato', 
      'test_vencimiento_contrato@gmail.com', 
      's3cr3t'
    )

    user.save()

    agencia=Agencia(
      user=user,
      nombre=u'test_vencimiento_contrato',
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234',
      fecha_inicio = datetime.datetime(2012,1,1,1,1,1)
    )
    
    agencia.save()

    self.assertFalse(agencia.en_periodo_prueba())
    self.assertTrue(agencia.vencida())
    self.assertFalse(agencia.borrada())

    pago=agencia.proximo_pago()

    self.assertTrue(pago.contratoagencia.vencido())

    pago.contratoagencia.estado=Contrato.PAGADO

    self.assertFalse(pago.contratoagencia.vencido())

  def test_agencia_vencida_y_creacion_otra_agencia(self):
    
    nombre=u'creacion_otra_agencia1'

    user = User.objects.create_user(
      nombre, 
      '%s@gmail.com'%nombre, 
      's3cr3t'
    )

    user.save()

    agencia=Agencia(
      user=user,
      nombre=nombre,
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234',
      fecha_inicio = datetime.datetime(2012,1,1,1,1,1)
    )
    
    agencia.clean()
    agencia.save()

    agencia=Agencia(
      user=user,
      nombre='%s2'%nombre,
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234',
    )
    
    self.assertRaises(ValidationError,agencia.clean)

  def test_agencia_prueba_y_creacion_otra_agencia(self):
    
    nombre=u'creacion_otra_agencia2'

    user = User.objects.create_user(
      nombre, 
      '%s@gmail.com'%nombre, 
      's3cr3t'
    )

    user.save()

    agencia=Agencia(
      user=user,
      nombre=nombre,
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234',
    )
    
    agencia.clean()
    agencia.save()

    agencia=Agencia(
      user=user,
      nombre='%s2'%nombre,
      usuario_gmail=u'test.agencia@gmail.com',
      clave_gmail = u'agencia1234',
    )
    
    self.assertRaises(ValidationError,agencia.clean)
