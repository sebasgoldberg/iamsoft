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

    if not saltar_verif_estado:
      if agencia.estado_creacion!=Agencia.CREACION_INICIADA:
        raise Exception(ugettext(u'La agencia tiene un estado inválido para ser creada'))

    agencia.estado_creacion=Agencia.CREACION_EN_PROCESO
    agencia.save()

    password = User.objects.make_random_password()

    array_llamada=[]

    try:

      array_llamada = [
        settings.AMBIENTE.script_crear_agencia,
        str(agencia.id),
        'iamcast',
        agencia.usuario_gmail,
        agencia.clave_gmail,
        agencia.dominio,
        settings.AMBIENTE.puerto_http,
        settings.AMBIENTE.puerto_https,
        settings.AMBIENTE.path_agencias,
        agencia.user.username,
        password,
        settings.AMBIENTE.zonomi.api_key,
        ]

      output=subprocess.check_output(array_llamada)

      os.environ['DJANGO_SETTINGS_MODULE'] = "alternativa.settings"
      array_llamada=[
        agencia.get_manage_script(),
        'crear_super_usuario',
        '--username=%s'%agencia.user.username,
        '--first_name=%s'%agencia.user.first_name,
        '--last_name=%s'%agencia.user.last_name,
        '--email=%s'%agencia.user.email,
        '--password=%s'%password,
      ]
      del os.environ['DJANGO_SETTINGS_MODULE']
      
      output=subprocess.check_output(array_llamada)

      if not suprimir_mail:
        asunto = ugettext(u'La Creación de su Agencia Finalizó Exitosamente')
        template = loader.get_template('iamcast/mail/exito_creacion_agencia.html')
        context = Context({'agencia':agencia, 'password':password, 'ambiente': settings.AMBIENTE})
        html_content = template.render(context)
        msg = MailIamSoft(asunto,ugettext(u'El contenido de este email debe ser visualizado en formato HTML'),[agencia.user.email])
        msg.set_html_body(html_content)
        msg.send()

      agencia.estado_creacion = Agencia.FINALIZADA_CON_EXITO
      agencia.activa = True
      agencia.save()

      self.stdout.write(u'Creacion exitosa.\n')

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

    # @todo enviar mail con el resultado de la creación
