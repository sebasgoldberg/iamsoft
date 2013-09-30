# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import subprocess
from django.utils.translation import ugettext
from django.conf import settings
from iamcast.models import Agencia
from django.contrib.auth.models import User
from home.mail import MailIamSoft
import logging
import traceback
import os
from django.template import loader
from django.template import Context

class Command(BaseCommand):

  help=u'Crea una instancia de la aplicación iamcast para la agencia pasada'

  option_list = BaseCommand.option_list + (
    make_option('--id'),
    make_option('--nombre'),
    make_option('--saltar_verif_estado', action='store_true', default=False),
    make_option('--suprimir_mail', action='store_true', default=False),
    )

  def handle(self,*args,**options):
    
    id=options['id']
    nombre=options['nombre']
    saltar_verif_estado=options['saltar_verif_estado']
    suprimir_mail=options['suprimir_mail']

    if id:
      agencia=Agencia.objects.get(pk=id)
    elif nombre:
      agencia=Agencia.objects.get(nombre=nombre)
    else:
      raise Exception(ugettext(u'Debe pasar un id o nombre de agencia como parámetro'))

    try:

      agencia.crear_servicio()      

    except Exception as e:
      if hasattr(e,'output'):
        output=e.output
      else:
        output=''
      cuerpo='%s\n\n%s\n\nsalida:\n%s'%(traceback.format_exc(),array_llamada,output)
      msg = MailIamSoft(u'Error en la creación',cuerpo,[email for _,email in settings.ADMINS])
      msg.send()
      """
      logger = logging.getLogger(__name__)
      logger.error('Excepción ocurrida al intentar crear agencia con id "%s": %s' % (id,e))
      """
      agencia.estado_creacion = Agencia.FINALIZADA_CON_ERRORES
      agencia.save()
      raise e

