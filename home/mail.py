# coding=utf-8
from iampacks.cross.correo.mail import Mail

class MailIamSoft(Mail):

  def actualizar_asunto(self,asunto):
    return u'IamSoft - %s' % asunto

