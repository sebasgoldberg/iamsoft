# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import subprocess
from django.utils.translation import ugettext as _
from django.conf import settings
from iamcast.models import Agencia
from django.contrib.auth.models import User
from home.mail import MailIamSoft
import logging
import traceback

class Command(BaseCommand):

  help=u'Crea una instancia de la aplicación iamcast para la agencia pasada'

  option_list = BaseCommand.option_list + (
    make_option('--id'),
    )

  def handle(self,*args,**options):
    
    id=options['id']

    if id:
      agencia=Agencia.objects.get(pk=id)
    else:
      raise Exception(_(u'Debe pasar un id de agencia como parámetro'))

    try:
      array_llamada=[
        settings.AMBIENTE.script_borrar_agencia,
        str(agencia.id),
        'iamcast',
        settings.AMBIENTE.path_agencias,
        agencia.dominio,
        settings.AMBIENTE.zonomi.api_key
        ]
      output=subprocess.check_output(array_llamada)
      agencia.estado_creacion = Agencia.BORRADA_CON_EXITO
      agencia.activa = False
      agencia.save()

      """
      if not suprimir_mail:
        asunto = _(u'La Creación de su Agencia Finalizó Exitosamente')
        template = loader.get_template('iamcast/mail/exito_creacion_agencia.html')
        context = RequestContext(request,{'agencia':agencia, 'password':password})
        text_content = template.render(context)
        msg = MailIamSoft(asunto,text_content,[user.email])
        msg.send()
        """

    except Exception as e:
      msg = MailIamSoft(u'Error en borrado de agencia %s'%agencia.id,'%s\n\n%s'%(traceback.format_exc(),array_llamada),[email for _,email in settings.ADMINS])
      msg.send()
      """
      logger = logging.getLogger(__name__)
      logger.error('Excepción ocurrida al intentar crear agencia con id "%s": %s' % (id,e))
      """
      agencia.estado_creacion = Agencia.BORRADA_CON_ERRORES
      agencia.save()
      raise e

    # @todo enviar mail con el resultado de la creación
    self.stdout.write('El estado de borrado de la agencia %s fue: %s\n'%(agencia.nombre,Agencia.DICT_ESTADO_CREACION[agencia.estado_creacion]))
