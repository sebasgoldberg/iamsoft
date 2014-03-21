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
from iampacks.cross.mercadopago.models import Pago
from subprocess import Popen
import traceback
from home.mail import MailIamSoft
import subprocess
import os
from django.template import loader
from django.template import Context
from iampacks.cross.zonomi.models import Zonomi
import logging

GMAIL_SIGNUP_URL=u'https://accounts.google.com/SignUp'
DIAS_CONTRATO=settings.AMBIENTE.iamcast.dias_contrato
MONEDA_TARIFA_DIARIA = Pago.PESO_ARGENTINO
TARIFA_DIARIA = settings.AMBIENTE.iamcast.tarifa_diaria 

class Moneda(models.Model):

  codigo = models.CharField(max_length=3, verbose_name=_(u'Código'))
  simbolo = models.CharField(max_length=3, verbose_name=_(u'Símbolo'))

  class Meta:
    ordering = ['-codigo']
    verbose_name = _(u"Moneda")
    verbose_name_plural = _(u"Monedas")

  def __unicode__(self):
    return self.codigo

  @staticmethod
  def get_default():
    return Moneda.objects.first()

class Tarifa(models.Model):

  moneda = models.ForeignKey(Moneda, null=False, blank=False)
  importe_compra = models.DecimalField(max_digits=10,decimal_places=2, verbose_name=_(u'Importe de compra'))
  importe_servicio = models.DecimalField(max_digits=10,decimal_places=2, verbose_name=_(u'Importe de servicio'))

  class Meta:
    ordering = ['-moneda__codigo']
    verbose_name = _(u"Tarifa")
    verbose_name_plural = _(u"Tarifas")

  def __unicode__(self):
    return _(u'Servicio %s %s - Compra %s %s') % (
      self.importe_servicio,
      self.moneda,
      self.importe_compra,
      self.moneda,
      )

  @staticmethod
  def get_vigente(moneda):
    return Tarifa.objects.filter(moneda=moneda).first()

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
  nombre = models.CharField(max_length=60, verbose_name=_(u'Nombre agencia'), unique=True)
  slug = models.CharField(max_length=60, verbose_name=_(u'Slug'), unique=True)
  dominio = models.CharField(max_length=100, unique=True, verbose_name=_(u'Dominio'), null=False, blank=True, help_text=_(u'Si no utilizará su propio dominio DEJELO VACIO. Tenga en cuenta que si coloca algún valor aqui, habrá que solicitar a la entidad registrante de su dominio que apunte a nuestros servidores DNS. Por otro lado en caso de usar su propio dominio, se deberá contratratar un certificado de seguridad con alguna entidad reconocida de forma que su sitio se vea seguro para los usuarios que lo utilizan.'))
  CREACION_INICIADA='CI'
  CREACION_EN_PROCESO='CP'
  FINALIZADA_CON_ERRORES='FR'
  FINALIZADA_CON_EXITO='FX'
  BORRADO_INICIADO='BI'
  BORRADO_EN_PROCESO='BE'
  BORRADA_CON_ERRORES='BR'
  BORRADA_CON_EXITO='BX'
  ESTADO_CREACION = (
    (CREACION_INICIADA,ugettext(u'Creación iniciada')),
    (CREACION_EN_PROCESO,ugettext(u'Creación en proceso')),
    (FINALIZADA_CON_ERRORES,ugettext(u'Finalizada con errores')),
    (FINALIZADA_CON_EXITO,ugettext(u'Finalizada con éxito')),
    (BORRADO_INICIADO,ugettext(u'Borrado Iniciado')),
    (BORRADO_EN_PROCESO,ugettext(u'Borrado en proceso')),
    (BORRADA_CON_ERRORES,ugettext(u'Borrada con errores')),
    (BORRADA_CON_EXITO,ugettext(u'Borrada con éxito')),
    )
  DICT_ESTADO_CREACION=dict(ESTADO_CREACION)
  estado_creacion = models.CharField(max_length=2,default=CREACION_INICIADA, verbose_name=(u'Estado creación'), choices=ESTADO_CREACION)
  activa = models.BooleanField(default=True, verbose_name=(u'Activa'))
  fecha_inicio = models.DateTimeField(verbose_name=_(u'Fecha inicio'), null=False, blank=False, default=datetime.now())

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

  def get_alfa_id(self):
    return 'iamcast_%s'%self.id

  def get_nombre_carpeta(self):
    return self.get_alfa_id()

  def get_db_name(self):
    return self.get_alfa_id()

  def get_db_user(self):
    return self.get_alfa_id()

  def get_ruta_instalacion(self):
    return '%s/%s'%(settings.AMBIENTE.path_agencias,self.get_nombre_carpeta())

  def get_manage_script(self):
    return '%s/manage.py'%self.get_ruta_instalacion()

  def get_ambiente_file_path(self):
    return '%s/alternativa/ambiente.py'%self.get_ruta_instalacion()

  def get_wsgi_file_path(self):
    return '%s/alternativa/wsgi.py'%self.get_ruta_instalacion()

  def get_puerto_http(self):
    return settings.AMBIENTE.puerto_http

  def get_puerto_https(self):
    return settings.AMBIENTE.puerto_https

  def get_mail_server(self):
    return settings.AMBIENTE.email.host

  def get_user(self):
    return self.slug

  def get_mail_user(self):
    return settings.AMBIENTE.email.user

  def get_mail_password(self):
    return settings.AMBIENTE.email.password

  def get_mail_port(self):
    return settings.AMBIENTE.email.port

  def get_zonomi_api_key(self):
    return settings.AMBIENTE.zonomi.api_key

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

  def crear(self):
    pass

  def borrar(self):
    pass

  def testActivar(self):
    if self.activa:
      raise Exception('La agencia %s, ya se encuentra activa.'%self.id)

  def doActivar(self):
    self.__callScript([
      'sudo',
      'a2ensite',
      self.get_apache_site(),
      ])

    self.__callScript([
      'sudo',
      'a2ensite',
      self.get_apache_ssl_site(),
      ])

    self.__callScript([
      'sudo',
      'service',
      'apache2',
      'reload'
      ])

    ddns = Zonomi(settings.AMBIENTE.zonomi.api_key)
    ddns.domain_update(self.get_dominio())
    ddns.add_domain_update_to_crontab(self.get_dominio(),settings.AMBIENTE.default_user)

    self.activa = True
    self.save()

  def activar(self):
    self.testActivar()
    self.doActivar()

  def get_scripts_id(self):
    return u"%s_%s"%(self.slug,self.id)

  def get_apache_site(self):
    return u"iamcast_%s"%self.id

  def get_apache_ssl_site(self):
    return u"iamcast_%s-ssl"%self.id

  def get_apache_ssl_config_file_path(self):
    return u'%s/%s'%(settings.AMBIENTE.apache.available_sites_dir, self.get_apache_ssl_site())

  def get_apache_config_file_path(self):
    return u'%s/%s'%(settings.AMBIENTE.apache.available_sites_dir, self.get_apache_site())

  def testDesactivar(self):
    if not self.activa:
      raise Exception('La agencia %s, ya se encuentra inactiva.'%self.id)

  def doDesactivar(self):
    
    try:
      self.__callScript([
        'sudo',
        'a2dissite',
        self.get_apache_site(),
        ])
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())

    try:
      self.__callScript([
        'sudo',
        'a2dissite',
        self.get_apache_ssl_site(),
        ])
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())

    try:
      self.__callScript([
        'sudo',
        'service',
        'apache2',
        'reload'
        ])
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())
    
    try:
      os.remove(self.get_apache_config_file_path())
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())

    try:
      os.remove(self.get_apache_ssl_config_file_path())
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())

    try:
      ddns = Zonomi(settings.AMBIENTE.zonomi.api_key)

      try:
        ddns.delete_domain(self.get_dominio())
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())

      try:
        ddns.remove_domain_update_from_crontab(self.get_dominio(),settings.AMBIENTE.default_user)
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())

    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())

    self.activa = False
    self.save()

  def get_dominio(self):
    return self.dominio

  def desactivar(self):
    self.testDesactivar()
    self.doDesactivar()

  def __callScript(self,args,shell=False,**kwargs):
    try:
      return subprocess.check_call(args,shell=shell,**kwargs)
    except subprocess.CalledProcessError as e:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())
      logger.error('Generated output from executed command: %s'%e.output)
      raise e

  def crear_servicio(self):
    
    if self.estado_creacion != Agencia.CREACION_INICIADA:
      raise Exception('Se ha intentado crear servicio para agencia %s pero su estado de creación %s es distinto de %s.'%(
        self.id,
        Agencia.DICT_ESTADO_CREACION[self.estado_creacion],
        Agencia.DICT_ESTADO_CREACION[Agencia.CREACION_INICIADA]
        ))

    self.estado_creacion=Agencia.CREACION_EN_PROCESO
    self.save()
    password = User.objects.make_random_password()

    os.makedirs(self.get_ruta_instalacion())
    os.chdir(self.get_ruta_instalacion())
    self.__callScript(['git', 'init'])
    self.__callScript(['git', 'pull', settings.AMBIENTE.iamcast.agencia_git_url])

    os.environ['DJANGO_SETTINGS_MODULE'] = "alternativa.settings"

    template = loader.get_template('iamcast/servicio/ambiente.py')
    context = Context({ 
      'agencia':self,
      'password':password,
      'admins': settings.AMBIENTE.admins,
      'root_password': settings.AMBIENTE.db.root.password,
      })
    ambiente_content = template.render(context)
    ambiente_file = open(self.get_ambiente_file_path(),'w')
    ambiente_file.write(ambiente_content)
    ambiente_file.close()

    self.__callScript(['./install.sh'])

    array_llamada=[
      self.get_manage_script(),
      'crear_super_usuario',
      '--username=%s'%self.user.username,
      '--first_name=%s'%self.user.first_name,
      '--last_name=%s'%self.user.last_name,
      '--email=%s'%self.user.email,
      '--password=%s'%self.user.password,
    ]
    self.__callScript(array_llamada)

    del os.environ['DJANGO_SETTINGS_MODULE']

    asunto = ugettext(u'La Creación de su Agencia Finalizó Exitosamente')
    template = loader.get_template('iamcast/mail/exito_creacion_agencia.html')
    context = Context({'agencia':self, 'password':password, 'ambiente': settings.AMBIENTE})
    html_content = template.render(context)
    msg = MailIamSoft(asunto,ugettext(u'El contenido de este email debe ser visualizado en formato HTML'),[self.user.email])
    msg.set_html_body(html_content)
    msg.send()

    self.estado_creacion = Agencia.FINALIZADA_CON_EXITO
    self.activa = True
    self.save()

  def borrar_servicio(self, modificar_estado=True):

    error = False
    import MySQLdb 

    try:

      try:
        self.desactivar()
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())
        error = True

      mysql_connection = MySQLdb.connect(
        'localhost', 
        settings.AMBIENTE.iamcast.mysql_user,
        settings.AMBIENTE.iamcast.mysql_pass
        )

      cursor = mysql_connection.cursor()

      try:
        cursor.execute("drop user '%s'"%self.get_db_user())
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())
        error = True

      try:
        cursor.execute("drop user '%s'@'localhost'"%self.get_db_user())
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())
        error = True
      try:
        cursor.execute("drop database %s"%self.get_db_name())
      except:
        logger = logging.getLogger(__name__)
        logger.error(traceback.format_exc())
        error = True
      
      mysql_connection.close()
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())
      error = True

    try:
      self.__callScript(['rm', '-rf', self.get_ruta_instalacion()])
    except:
      logger = logging.getLogger(__name__)
      logger.error(traceback.format_exc())
      error = True

    if modificar_estado:
      self.estado_creacion = Agencia.BORRADA_CON_EXITO
      self.activa = False
      self.save()

  def isActiva(self):
    return self.activa

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
