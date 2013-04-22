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

  help=u'Desactiva una agencia'

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
      agencia=Agencia.objects.get(pk=id)
      
      subprocess.check_call([
        'a2dissite',
        agencia.get_apache_site(),
        ])

      subprocess.check_call([
        'a2dissite',
        agencia.get_apache_ssl_site(),
        ])

      subprocess.check_call([
        'service',
        'apache2',
        'reload'
        ])

      """
      @todo Agregar desactivación de zonomi
      """

      agencia.activa = False
      agencia.save()

      self.stdout.write('Agencia %s desactivada con éxito.\n'%(agencia.nombre))

    except Exception as e:
      #msg = MailIamSoft(u'Error al desactivar agencia %s'%agencia.id,'%s\n\n'%(traceback.format_exc()),[email for _,email in settings.ADMINS])
      #msg.send()
      """
      @todo Usar logger
      logger = logging.getLogger(__name__)
      logger.error('Excepción ocurrida al intentar crear agencia con id "%s": %s' % (id,e))
      """
      if e.__class__ is subprocess.CalledProcessError:
        output=e.output
      else:
        output=''
      self.stdout.write('%s\n\n%s'%
        (traceback.format_exc(), output) 
        )
