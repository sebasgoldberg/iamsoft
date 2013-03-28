# coding=utf-8
# Create your views here.

from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.contrib.auth.decorators import login_required

def index(request):
  return render(request,'index.html')

def contacto(request):
  return render(request,'contacto.html')

def quienes_somos(request):
  return render(request,'quienes_somos.html')

@login_required
def cuenta(request):
  return render(request,'cuenta.html')
