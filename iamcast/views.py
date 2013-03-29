# coding=utf-8
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subprocess import Popen
from django.contrib import messages
import hashlib
from django.conf import settings
from django.http import HttpResponse
from mercadopago.models import MercadoPago
from iampacks.cross.correo.mail import Mail
from iamcast.models import Agencia
from django.utils.translation import ugettext as _
from iamcast.forms import AgenciaForm
from iamcast.models import PagoContrato
from datetime import datetime


def index(request):
  return render(request,'iamcast/index.html')

def crear_agencia(form, request):
  """
  Ojo editar con visudo para que script llamado corra para el usuario de apache2 sin introducir clave.
  """
  form.save()

  output=Popen([
    '%s/manage.py'%settings.AMBIENTE.project_directory,
    'crear_agencia',
    '--id=%s'%form.instance.id,
    '&'
    ])

  messages.info(request,_(u'Hemos iniciado el proceso de creación del módulo de administración y página estándar. Este proceso puede demorar varios minutos. Una vez finalizado el proceso le notificaremos por email de forma que pueda comenzar a utilizar la aplicación.'))
  messages.info(request,_(u'Podrá probar la aplicación por un período de %s días. Luego para seguir utilizandola deberá realizar el pago correspondiente por el período de tiempo que crea más conveniente.')%settings.DIAS_PRUEBA_IAMCAST)

@login_required
def configurar(request):
  agencia=Agencia(
    user=request.user,
    fecha_inicio = datetime.today(),
    activa=True
  )

  if request.method == 'POST':
    form = AgenciaForm(request.POST,instance=agencia)
    if form.is_valid():
      crear_agencia(form, request)
      next_page = '/cuenta/usuario/'
      return redirect(next_page)
  else:
    next_page = request.GET.get('next')
    form = AgenciaForm(instance=agencia,initial={'next_page':next_page})
  return render(request,'iamcast/configurar.html',{'form':form})

@login_required
def contratar(request):

  cantidad = '1'
  moneda = 'ARS'
  importe = '0.01'
  id_contrato_agencia = '123'
  id_agencia = '456'

  item_id = id_contrato_agencia
  external_reference = id_agencia

  md5String = settings.AMBIENTE.mercado_pago.client_id + settings.AMBIENTE.mercado_pago.client_secret + cantidad + moneda + importe + item_id + external_reference;

  md5 = hashlib.md5(md5String).hexdigest()

  pago = {
      "client_id":settings.AMBIENTE.mercado_pago.client_id,
      "md5":md5,
     
      #<!-- Datos obligatorios del item -->
      "item_title":u"Contratación mensual IamCast",
      "item_quantity":cantidad,
      "item_currency_id":moneda,
      "item_unit_price":importe,
      
      #<!-- Datos opcionales -->
      "item_id":item_id,
      "external_reference":external_reference,
      "item_picture_url":'',
      "payer_name":request.user.first_name,
      "payer_surname":request.user.last_name,
      "payer_email":request.user.email,
      "back_url_success":"",
      "back_url_pending":""
    }

  return render(request,'iamcast/contratar.html',{'pago':pago})

def notificacion_pago(request):
  if request.GET['topic']!='payment':
    raise Exception(u'No se ha encontrado en GET parámetro "topic" con valor "payment"')

  id_notificacion_pago = request.GET['id']
  if not id_notificacion_pago:
    raise Exception(u'No se ha encontrado en GET parámetro "id"')

  mp = MercadoPago()

  pago=mp.get_pago_notificado(id_notificacion_pago)

  msg = Mail('Notificacion de pago MP',str(pago),['sebas.goldberg@gmail.com'])
  msg.send()

  return HttpResponse()

"""
def resultado_creacion_agencia(request):
  id_agencia=request.GET['id_agencia']
  resultado=request.GET['resultado']
  if not id_agencia:
    raise Exception('No se ha informado el parámetro id_agencia.')
  if not resultado:
    raise Exception('No se ha informado el parámetro resultado.')
  agencia=Agencia.objects.get(pk=id_agencia)
  if agencia.creacion_exitosa is None:
    agencia.creacion_exitosa = (resultado == '0')
    agencia.save()

  destinatarios= [ mail for _, mail in settings.AMBIENTE.admins ]
  cuerpo=u"El resultado de la creación de la agencia '%s' fue '%s'" % (agencia.nombre, resultado)
  msg = Mail('Resultado de creación de agencia',str(pago),destinatarios)
  msg.send()

  return HttpResponse()
"""

def actualizar_pago(request,id):
  pago=PagoContrato.objects.get(pk=id)
  pago.actualizar_estado_items()
  if pago.contratoagencia.pagado():
    messages.success(request,_(u"Felicitaciones! Nos han confirmado que su pago por '%s' ya se encuentra acreditado. Hemos actualizado la fecha de vencimiento del contrato de su agencia.")%pago.contratoagencia.titulo)
  else:
    messages.info(request,_(u"Hemos registrado que el pago por '%s' se encuentra pendiente. Si ya realizó el pago tenga en cuenta que su confirmación puede demorar un tiempo.")%pago.contratoagencia.titulo)

def pago_success(request,id):
  actualizar_pago(request,id)
  return redirect('/cuenta/usuario/')

def pago_pending(request,id):
  actualizar_pago(request,id)
  return redirect('/cuenta/usuario/')
