# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.
class Contrato(models.Model):
  user = models.OneToOneField(User, null=False, blank=False, editable=False)
  fecha = models.DateField(verbose_name=_(u'Fecha'), null=False, blank=False, editable=False)
  activo = models.BooleanField(default=True, verbose_name=(u'Activo'))

  class Meta:
    abstract = True
    verbose_name = _(u"Contrato")
    verbose_name_plural = _(u"Contratos")
  
class ContratoAgencia(Contrato):
  #echo "$0 <ID_AGENCIA> <SLUG_AGENCIA> <GMAIL_USER> <GMAIL_PASS> <DOMINIO>"
  nombre_agencia = models.CharField(max_length=60, verbose_name=_(u'Nombre'), unique=True)
  #nombre_agencia_slug = SlugField(max_length=50, editable=False, unique=True)
  usuario_gmail = models.CharField(max_length=60, verbose_name=_(u'Usuario gmail'), help_text=_(u'Este usuario es necesario para que su aplicación pueda enviar mails. Preferentemente debe ser una cuenta a la que nadie tenga acceso'))
  clave_gmail = models.CharField(max_length=60, verbose_name=_(u'Clave gmail'), help_text=_(u'Clave del usuario gmail.'))
