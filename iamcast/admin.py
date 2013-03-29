from django.contrib import admin
from iamcast.models import Agencia, ContratoAgencia, PagoContrato
from mercadopago.admin import PagoAdmin

class AgenciaAdmin(admin.ModelAdmin):
  list_display=['id','nombre']

admin.site.register(Agencia,AgenciaAdmin)
admin.site.register(ContratoAgencia)
admin.site.register(PagoContrato,PagoAdmin)

