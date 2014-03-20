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
    make_option('--suprimir_mail', action='store_true', default=False),
    )

  def handle(self,*args,**options):
    
    agencias_creadas_en_estado_creacion_inicial=Agencia.objects.filter(estado_creacion=Agencia.CREACION_INICIADA)

    for agencia in agencias_creadas_en_estado_creacion_inicial:

      try:

        try:
          agencia=Agencia.objects.get(pk=agencia.id,estado_creacion=Agencia.CREACION_INICIADA)
        except AgenciaNotFound:
          continue

        agencia.crear_servicio()

      except Exception as e:
        
        if hasattr(e,'output'):
          output=e.output
        else:
          output=''

        logger = logging.getLogger(__name__)
        logger.error('Excepcion ocurrida al intentar crear agencia con id "%s": %s' % (agencia.id,e))
        logger.error('Salida registrada: %s'%output)
        logger.error('Detalle de la excepción: %s' % traceback.format_exc())

        cuerpo='%s\n\nsalida:\n%s'%(traceback.format_exc(),output)
        msg = MailIamSoft(u'Error en la creación',cuerpo,[email for _,email in settings.ADMINS])
        msg.send()

