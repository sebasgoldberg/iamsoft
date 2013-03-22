# coding=utf-8
# Create your views here.

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from subprocess import check_output
from django.contrib import messages

def index(request):
  return render(request,'iamcast/index.html')

@login_required
def contratar(request):
  """
  Ojo editar con visudo para que script llamado corra para el usuario de apache2 sin introducir clave.
  """
  output=check_output(['sudo','/home/cerebro/django-projects/iamsoft/iamcast/restart_apache.sh','&'])
  #output=check_output(['whoami'])
  messages.success(request, output)
  return render(request,'iamcast/index.html')
  """
  contrato=Contrato(
    user=request.user,
    fecha = date.today(),
    activo=False,
  )

  if request.method == 'POST':
    form = ContratoForm(request.POST,instance=contrato)
    if form.is_valid():
      form.save()
      messages.success(request, _(u'Datos guardados con éxito'))
      messages.info(request, _(u'A continuación complete la información del pago para concretar la operación'))
      next_page = form.cleaned_data['next_page']
      if not next_page:
        next_page = '/iamcast/cuenta/'
      return redirect(next_page)
  else:
    next_page = request.GET.get('next')
    form = ContratoForm(instance=agenciado,initial={'next_page':next_page})
  return render(request,'iamcast/contratar.html',{'form':form})
  """
