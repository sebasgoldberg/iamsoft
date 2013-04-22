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
from iamcast.forms import AgenciaForm, BorrarAgenciaForm
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

  messages.success(request,_(u'Hemos iniciado el proceso de creación del módulo de administración y página estándar. Este proceso puede demorar varios minutos. Una vez finalizado el proceso le notificaremos por email de forma que pueda comenzar a utilizar la aplicación.'))
  messages.success(request,_(u'Podrá probar la aplicación por un período de %s días. Luego para seguir utilizandola deberá realizar el pago correspondiente por el período de tiempo que crea más conveniente.')%settings.DIAS_PRUEBA_IAMCAST)

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

"""
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

@login_required
def ver_historial_pagos(request,id_agencia):
  agencia=Agencia.objects.get(pk=id_agencia)
  #agencia.proximo_pago() #Aseguramos que se cree el último pago a ser realizado
  #contratos=agencia.contratoagencia_set.order_by('-fecha_inicio')
  return render(request,'iamcast/ver_historial_pagos.html',{'agencia':agencia})

@login_required
def borrar_agencia(request):

  if request.method == 'POST':
    form = BorrarAgenciaForm(request.POST)
    if form.is_valid():
      agencia=Agencia.objects.get(pk=form.cleaned_data.get('agencia_id'))
      output=Popen([
        '%s/manage.py'%settings.AMBIENTE.project_directory,
        'borrar_agencia',
        '--id=%s'%agencia.id,
        '&'
        ])
      messages.info(request,_(u'Hemos iniciado el proceso de borrado de la agencia %s. Este proceso puede demorar varios minutos. Una vez finalizado el proceso podrá verificar el estado de su agencia en su cuenta')%agencia.nombre)
      return redirect('/cuenta/usuario/')
  else:
    id = request.GET.get('id')
    form = BorrarAgenciaForm(initial={'agencia_id':id})

  agencia=Agencia.objects.get(pk=form['agencia_id'].value())

  messages.warning(request,_(u'ATENCION! Si lleva a cabo este proceso no tendrá posibilidad de recuperar los datos de la agencia %s')%agencia.nombre)

  return render(request,'iamcast/borrar_agencia.html',{'form':form, 'agencia':agencia})

@login_required
def tutorial(request,id):
  agencia=Agencia.objects.get(pk=id)
  if agencia.user.username!=request.user.username:
    messages.error(request,_(u'El tutorial al que está intentando acceder es de una agencia que no forma parte de su cuenta.'))
    return redirect('/cuenta/usuario/')
  if not agencia.activa:
    messages.error(request,_(u'El tutorial al que está intentando acceder es de una agencia que no se encuentra activa.'))
    return redirect('/cuenta/usuario/')
  return render(request,'iamcast/tutorial.html', {'agencia':agencia})
