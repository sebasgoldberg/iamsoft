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
from datetime import datetime, timedelta
from mercadopago.models import Pago

GMAIL_SIGNUP_URL=u'https://accounts.google.com/SignUp'
DIAS_CONTRATO=settings.AMBIENTE.iamcast.dias_contrato
MONEDA_TARIFA_DIARIA = Pago.PESO_ARGENTINO
TARIFA_DIARIA = settings.AMBIENTE.iamcast.tarifa_diaria 

# Create your models here.
class Contrato(models.Model):
  titulo = models.CharField(max_length=200, verbose_name=_(u'Titulo del contrato'))
  fecha_inicio = models.DateTimeField(verbose_name=_(u'Fecha inicio'), null=False, blank=False)
  fecha_fin = models.DateTimeField(verbose_name=_(u'Fecha fin'), null=False, blank=False)
  INICIAL='IN'
  PENDIENTE='PE'
  PAGADO='PA'
  ESTADO= (
    (INICIAL,ugettext(u'Inicial')),
    (PENDIENTE,ugettext(u'Pendiente')),
    (PAGADO,ugettext(u'Pagado')),
    )
  DICT_ESTADO=dict(ESTADO)
  estado = models.CharField(max_length=2,default=PENDIENTE, verbose_name=(u'Estado'), choices=ESTADO)

  class Meta:
    abstract = True
    verbose_name = _(u"Contrato")
    verbose_name_plural = _(u"Contratos")
    ordering=['-fecha_inicio']

  def __unicode__(self):
    return self.titulo

  def pagado(self):
    return self.estado==Contrato.PAGADO

  def vencido(self):
    # Si no está pagado y además la fecha de fin está en el pasado.
    return not self.pagado() and self.fecha_fin < datetime.now()

  def pendiente(self):
    return self.estado==Contrato.PENDIENTE

  def descripcion_estado(self):
    return Contrato.DICT_ESTADO[self.estado]

class Agencia(models.Model):
  user = models.ForeignKey(User, null=False, blank=True, editable=False)
  nombre = models.CharField(max_length=60, verbose_name=_(u'Nombre'), unique=True, help_text=_('Nombre de su agencia'))
  slug = models.CharField(max_length=60, verbose_name=_(u'Slug'), unique=True)
  usuario_gmail = models.EmailField(max_length=60, verbose_name=_(u'Email de gmail'), help_text=_(u'Este usuario es necesario para que su aplicación pueda enviar mails (tenga en cuenta que esta casilla enviará emails a los usuarios que interactuen con su agencia: productoras, agenciados, etc.). Preferentemente debe ser una cuenta a la que nadie tenga acceso. Si no tiene una cuenta en gmail, por favor creela en %s y suministrenos usuario y contraseña de dicha cuenta.')%('<a href="%s" target="_blank">%s</a>'%(GMAIL_SIGNUP_URL,GMAIL_SIGNUP_URL)))
  clave_gmail = models.CharField(max_length=60, verbose_name=_(u'Clave gmail'), help_text=_(u'Clave del usuario gmail.'))
  dominio = models.CharField(max_length=100, unique=True, verbose_name=_(u'Dominio'), null=False, blank=True, help_text=_(u'Si no utilizará su propio dominio DEJELO VACIO. Tenga en cuenta que si coloca algún valor aqui, habrá que solicitar a la entidad registrante de su dominio que apunte a nuestros servidores DNS. Por otro lado en caso de usar su propio dominio, se deberá contratratar un certificado de seguridad con alguna entidad reconocida de forma que su sitio se vea seguro para los usuarios que lo utilizan.'))
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
  fecha_inicio = models.DateTimeField(verbose_name=_(u'Fecha inicio'), null=False, blank=False, default=datetime.now())
  #fecha_vencimiento = models.DateTimeField(verbose_name=_(u'Fecha vencimiento'), null=False, blank=False, default=datetime.now()+timedelta(days=settings.DIAS_PRUEBA_IAMCAST))

  class Meta:
    ordering = ['-id']
    verbose_name = _(u"Agencia")
    verbose_name_plural = _(u"Agencias")

  def slugify(self):
    if not self.slug:
      self.slug = slugify_filter(self.nombre)
    if not self.dominio:
      self.dominio = '%s.%s'%(self.slug,settings.AMBIENTE.dominio_agencias)

  def url_historial_pagos(self):
    return '/iamcast/historial/pagos/%s/'%self.id

  def creada(self):
    return self.estado_creacion in [Agencia.FINALIZADA_CON_EXITO, Agencia.FINALIZADA_CON_ERRORES]

  def borrada(self):
    return self.estado_creacion in [Agencia.BORRADA_CON_ERRORES, Agencia.BORRADA_CON_EXITO]

  def vencida(self):
    return self.proximo_contrato().fecha_fin<datetime.now()

  def en_periodo_prueba(self):
    """
    Una agencia está en período de prueba si no tiene contratos pagados y la fecha actual es menor que la fecha de vencimiento.
    """
    if self.fecha_vencimiento() > datetime.now():
      if self.contratoagencia_set.exclude(estado=Contrato.PAGADO):
        return True
    return False

  def clean(self):
    self.slugify()
    # Se verifica slug
    if self.id:
      # Verifica que no exista otra agencia con mismo slug (se excluye a si misma)
      agencias=Agencia.objects.filter(slug=self.slug).exclude(id=self.id)
    else:
      # Verifica que no exista otra agencia con mismo slug
      agencias=Agencia.objects.filter(slug=self.slug)
    if agencias:
      raise ValidationError(ugettext('El nombre ingresado ya existe o es muy similar a uno ya existente. Por favor ingrese otro nombre'))
    # Se verifica cantidad de agencias de un mismo usuario
    if not self.id:
      for agencia in self.user.agencia_set.all():
        if not agencia.id:
          continue
        if agencia.borrada():
          continue
        if agencia.vencida():
          raise ValidationError(ugettext(u'No hemos registrado el pago de la agencia %s. Para poder crear una nueva agencia, antes deberá abonar el importe correspondiente. Dicho pago podrá realizarlo accediendo a su cuenta.')%(agencia.nombre))
        if agencia.en_periodo_prueba():
          raise ValidationError(ugettext(u'Hemos registrado que la agencia %s se encuentra en período de prueba. Para que pueda crear una nueva agencia, antes deberá realizar el pago correspondiente. Dicho pago podrá realizarlo accediendo a su cuenta.')%(agencia.nombre))

  def get_nombre_carpeta(self):
    return 'iamcast_%s'%self.id

  def get_manage_script(self):
    return '%s/%s/manage.py'%(settings.AMBIENTE.path_agencias,self.get_nombre_carpeta())

  def url_base_agencia(self):
    return u'http://%s:%s'%(self.dominio,settings.AMBIENTE.puerto_http)

  def url_sitio_agencia(self):
    return u'%s/'%self.url_base_agencia()

  def url_admin_agencia(self):
    return u'%s/admin/'%self.url_base_agencia()

  def url_reiniciar_clave(self):
    return '%s%s'%(self.url_sitio_agencia(),'usuario/reiniciar/clave/')

  def descripcion_estado_creacion(self):
    return Agencia.DICT_ESTADO_CREACION[self.estado_creacion]

  def __unicode__(self):
    return self.nombre

  def estado_erroneo(self):
    return self.estado_creacion in (Agencia.FINALIZADA_CON_ERRORES, Agencia.BORRADA_CON_EXITO, Agencia.BORRADA_CON_ERRORES) or not self.activa

  def estado_advertencia(self):
    return self.activa and self.estado_creacion in (Agencia.CREACION_INICIADA, Agencia.CREACION_EN_PROCESO)

  def estado_exitoso(self):
    return self.activa and self.estado_creacion in (Agencia.FINALIZADA_CON_EXITO)

  def get_ultimo_contrato_pagado(self):
    contratos=self.contratoagencia_set.filter(estado=Contrato.PAGADO).order_by('-fecha_fin')
    if contratos:
      return contratos[0]
    return None

  def get_contrato_por_pagar(self):
    contratos=self.contratoagencia_set.exclude(estado=Contrato.PAGADO)
    if contratos:
      return contratos[0]
    return None

  def fecha_vencimiento(self):
    contrato=self.get_ultimo_contrato_pagado()
    if contrato:
      return contrato.fecha_fin
    contrato=self.get_contrato_por_pagar()
    if contrato:
      return contrato.fecha_inicio-timedelta(seconds=1)
    return self.fecha_inicio+timedelta(days=settings.DIAS_PRUEBA_IAMCAST)

  def proximo_contrato(self):

    contrato=self.get_contrato_por_pagar()
    if contrato:
      return contrato

    fecha_vencimiento=self.fecha_vencimiento()

    fecha_inicio=fecha_vencimiento+timedelta(seconds=1)
    fecha_fin=fecha_vencimiento+timedelta(days=DIAS_CONTRATO)

    titulo_contrato=ugettext(u'Contrato servicio IamCast para agencia %(agencia)s por %(dias)s días (desde %(fecha_inicio)s hasta %(fecha_fin)s)')%{
      'agencia':self.nombre,
      'dias':DIAS_CONTRATO,
      'fecha_inicio':fecha_inicio,
      'fecha_fin':fecha_fin
    }

    titulo_pago=ugettext(u'Pago de %s')%titulo_contrato

    pago=PagoContrato(
      item_title=titulo_pago,
      item_quantity=DIAS_CONTRATO,
      item_currency_id=MONEDA_TARIFA_DIARIA,
      item_unit_price=TARIFA_DIARIA
    )

    pago.save()

    contrato=ContratoAgencia(
      agencia=self,
      titulo=titulo_contrato,
      fecha_inicio=fecha_inicio,
      fecha_fin=fecha_fin,
      pago=pago
    )

    contrato.save()

    return contrato

  def proximo_pago(self):
    return self.proximo_contrato().pago

class PagoContrato(Pago):

  def payer_name(self):
    return self.contratoagencia.agencia.user.first_name

  def payer_surname(self):
    return self.contratoagencia.agencia.user.last_name

  def payer_email(self):
    return self.contratoagencia.agencia.user.email

  def back_url_success(self):
    return u'%s/iamcast/pago/success/%s/'%(settings.AMBIENTE.get_base_https(),self.id)

  def back_url_pending(self):
    return u'%s/iamcast/pago/pending/%s/'%(settings.AMBIENTE.get_base_https(),self.id)

  def actualizar_estado_items(self):
    if self.approved_and_accredited():
      self.contratoagencia.estado=Contrato.PAGADO
    else:
      self.contratoagencia.estado=Contrato.PENDIENTE
    self.contratoagencia.save()

class ContratoAgencia(Contrato):
  agencia = models.ForeignKey(Agencia, null=False, blank=False)
  pago = models.OneToOneField(PagoContrato, null=False, blank=False)

  """
  def save(self, *args, **kwargs):
    if self.pago is None:
      self.pago=Pago(
        item_title=titulo,
        item_quantity=DIAS_CONTRATO,
        item_currency_id=MONEDA_TARIFA_DIARIA,
        item_unit_price=TARIFA_DIARIA
      )
    super(ContratoAgencia,self).save(*args,**kwargs)
    """

"""
@todo Verificar si el método Agencia.clean cumple una función similar.
@receiver(pre_save, sender=Agencia)
def callback_pre_save_agencia(sender, instance, raw, using, **kwargs):
  instance.slugify()
"""

#class ContratoAgencia(Contrato):
  #agencia = models.ForeignKey(Agencia,on_delete=models.PROTECT,verbose_name = _(u'Agencia'))
