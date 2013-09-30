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
from django.conf import settings

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

  def test_creacion_agencia(self):

    if settings.AMBIENTE.productivo:
      raise Exception('No se pueden crear servicios de agencias de prueba en un sistema productivo')

    nombre=u'creacion_agencia'

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

    agencia=Agencia.objects.get(pk=agencia.id)
    
    try:
      agencia.crear_servicio()

      agencia=Agencia.objects.get(pk=agencia.id)

      self.assertTrue(agencia.isActiva())
      self.assertFalse(agencia.vencida())
      self.assertFalse(agencia.borrada())
      self.assertTrue(agencia.en_periodo_prueba())
      self.assertTrue(agencia.estado_exitoso())
      self.assertFalse(agencia.estado_advertencia())
      self.assertFalse(agencia.estado_erroneo())
    finally:
      agencia=Agencia.objects.get(pk=agencia.id)
      agencia.borrar_servicio()


  def test_desactivar_activar_servicio_agencia(self):
  
    if settings.AMBIENTE.productivo:
      raise Exception('No se pueden crear servicios de agencias de prueba en un sistema productivo')

    nombre=u'desactivar_servicio_agencia'

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

    agencia=Agencia.objects.get(pk=agencia.id)
    
    try:
      agencia.crear_servicio()

      agencia=Agencia.objects.get(pk=agencia.id)

      agencia.desactivar()

      self.assertFalse(agencia.isActiva())
      self.assertFalse(agencia.borrada())
      self.assertFalse(agencia.estado_exitoso())
      self.assertFalse(agencia.estado_advertencia())
      self.assertTrue(agencia.estado_erroneo())

      agencia.activar()

      self.assertTrue(agencia.isActiva())
      self.assertFalse(agencia.vencida())
      self.assertFalse(agencia.borrada())
      self.assertTrue(agencia.en_periodo_prueba())
      self.assertTrue(agencia.estado_exitoso())
      self.assertFalse(agencia.estado_advertencia())
      self.assertFalse(agencia.estado_erroneo())

    finally:
      agencia=Agencia.objects.get(pk=agencia.id)
      agencia.borrar_servicio()

from django.test.client import Client

class IamCastClientTest(TestCase):

  def test_creacion_agencia(self):

    password = 's3cr3t3'
    user = User.objects.create_user(
      'test_creacion_agencia', 
      email='test_creacion_agencia@gmail.com', 
      password=password
    )

    user.save()
    
    self.assertEqual('test_creacion_agencia',user.username)
    self.assertNotEqual(password,user.password)

    c = Client()

    self.assertTrue(c.login(username=user.username,password=password))

    response = c.get('/iamcast/configurar/', follow=True)
    self.assertEqual(response.status_code,200)
    print response.redirect_chain
    self.assertTrue('iamcast/configurar.html' in [t.name for t in response.templates])

    nombre_nueva_agencia = 'test_creacion_agencia'
    response = c.post('/iamcast/configurar/',{
      'nombre': nombre_nueva_agencia,
      'idioma': 'es',
      'usuario_gmail': 'test_creacion_agencia@gmail.com',
      'clave_gmail': password,
      'clave_gmail2': password,
      }, follow = True)
    self.assertEqual(response.status_code,200)
    self.assertTrue('iamcast/cuenta_usuario.html' in [t.name for t in response.templates])

    nueva_agencia = Agencia.objects.get(nombre=nombre_nueva_agencia)

    nueva_agencia.borrar_servicio(modificar_estado=False)

    self.assertEqual(Agencia.CREACION_INICIADA,nueva_agencia.estado_creacion)

    from django.core.management import call_command

    call_command('crear_agencias_pendientes')

    nueva_agencia = Agencia.objects.get(nombre=nombre_nueva_agencia)

    self.assertEqual(
      Agencia.DICT_ESTADO_CREACION[Agencia.FINALIZADA_CON_EXITO],
      Agencia.DICT_ESTADO_CREACION[nueva_agencia.estado_creacion]
      )
    
    nueva_agencia.borrar_servicio()
