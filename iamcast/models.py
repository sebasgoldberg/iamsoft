# coding=utf-8
from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify as slugify_filter 
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.
class Contrato(models.Model):
  fecha_inicio = models.DateTimeField(verbose_name=_(u'Fecha inicio'), null=False, blank=False, editable=False)
  fecha_fin = models.DateTimeField(verbose_name=_(u'Fecha fin'), null=False, blank=False, editable=False)
  activo = models.BooleanField(default=True, verbose_name=(u'Activo'), editable=False)
  importe = models.DecimalField(max_digits=9, decimal_places=3, editable=False)
  cancelado = models.BooleanField(default=True, verbose_name=(u'Activo'), editable=False)

  class Meta:
    abstract = True
    verbose_name = _(u"Contrato")
    verbose_name_plural = _(u"Contratos")


class Agencia(models.Model):
  user = models.ForeignKey(User, null=False, blank=True, editable=False)
  fecha_inicio = models.DateTimeField(verbose_name=_(u'Fecha inicio'), null=False, blank=False)
  nombre = models.CharField(max_length=60, verbose_name=_(u'Nombre'), unique=True, help_text=_('Nombre de su agencia'))
  slug = models.CharField(max_length=60, verbose_name=_(u'Slug'), unique=True)
  usuario_gmail = models.CharField(max_length=60, verbose_name=_(u'Usuario gmail'), help_text=_(u'Este usuario es necesario para que su aplicación pueda enviar mails. Preferentemente debe ser una cuenta a la que nadie tenga acceso. Si no tiene una cuenta en gmail, por favor creela en %s y suministrenos usuario y contraseña de dicha cuenta.')%u'https://accounts.google.com/SignUp')
  clave_gmail = models.CharField(max_length=60, verbose_name=_(u'Clave gmail'), help_text=_(u'Clave del usuario gmail.'))
  dominio = models.URLField(unique=True, verbose_name=_(u'Dominio'), null=False, blank=True, help_text=_(u'Si no utilizará su propio dominio DEJELO VACIO. Tenga en cuenta que si coloca algún valor aqui, habrá que solicitar a la entidad registrante de su dominio que apunte a nuestros servidores DNS. Por otro lado en caso de usar su propio dominio, se deberá contratratar un certificado de seguridad con alguna entidad reconocida de forma que su sitio se vea seguro para los usuarios que lo utilizan.'))
  CREACION_INICIADA='CI'
  CREACION_EN_PROCESO='CP'
  FINALIZADA_CON_ERRORES='FR'
  FINALIZADA_CON_EXITO='FX'
  BORRADA_CON_ERRORES='BR'
  BORRADA_CON_EXITO='BX'
  ESTADO_CREACION = (
    (CREACION_INICIADA,ugettext(u'Creación iniciada')),
    (CREACION_EN_PROCESO,ugettext(u'Creación en proceso')),
    (FINALIZADA_CON_ERRORES,ugettext(u'Finalizada con errores')),
    (FINALIZADA_CON_EXITO,ugettext(u'Finalizada con éxito')),
    (BORRADA_CON_ERRORES,ugettext(u'Borrada con errores')),
    (BORRADA_CON_EXITO,ugettext(u'Borrada con éxito')),
    )
  DICT_ESTADO_CREACION=dict(ESTADO_CREACION)
  estado_creacion = models.CharField(max_length=2,default=CREACION_INICIADA, verbose_name=(u'Estado creación'), choices=ESTADO_CREACION)
  activa = models.BooleanField(default=True, verbose_name=(u'Activa'))

  def slugify(self):
    if not self.slug:
      self.slug = slugify_filter(self.nombre)
    if not self.dominio:
      self.dominio = '%s.%s'%(self.slug,settings.AMBIENTE.dominio)

  def clean(self):
    self.slugify()
    if self.id:
      agencias=Agencia.objects.filter(slug=self.slug).exclude(id=self.id)
    else:
      agencias=Agencia.objects.filter(slug=self.slug)

    if agencias:
      raise ValidationError(ugettext('El nombre ingresado ya existe o es muy similar a uno ya existente. Por favor ingrese otro nombre'))

  def get_nombre_carpeta(self):
    return 'iamcast_%s'%self.id

  def get_manage_script(self):
    return '%s/%s/manage.py'%(settings.AMBIENTE.path_agencias,self.get_nombre_carpeta())

  def url_base_agencia(self):
    return 'http://%s'%self.dominio

  def url_sitio_agencia(self):
    return '%s/'%self.url_base_agencia()

  def url_admin_agencia(self):
    return '%s/admin/'%self.url_base_agencia()

  def __unicode__(self):
    return self.nombre

"""
@todo Verificar si el método Agencia.clean cumple una función similar.
@receiver(pre_save, sender=Agencia)
def callback_pre_save_agencia(sender, instance, raw, using, **kwargs):
  instance.slugify()
"""

#class ContratoAgencia(Contrato):
  #agencia = models.ForeignKey(Agencia,on_delete=models.PROTECT,verbose_name = _(u'Agencia'))
