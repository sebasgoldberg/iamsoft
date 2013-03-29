"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from iamcast.models import Agencia
from django.contrib.auth.models import User

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

