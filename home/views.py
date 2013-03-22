# coding=utf-8
# Create your views here.

from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

def index(request):
  return render(request,'index.html')

def contacto(request):
  return render(request,'contacto.html')

def quienes_somos(request):
  return render(request,'quienes_somos.html')
