from django.contrib import admin
from iamcast.models import Agencia, ContratoAgencia, PagoContrato
from mercadopago.admin import PagoAdmin

class AgenciaAdmin(admin.ModelAdmin):
  list_display=['id', 'nombre', 'estado_creacion',  'dominio', 'vencida']
  list_display_links = ('id', 'nombre')
  list_filter=['activa', 'estado_creacion']
  search_fields=['id', 'nombre']
  list_per_page = 40

admin.site.register(Agencia,AgenciaAdmin)
admin.site.register(ContratoAgencia)
admin.site.register(PagoContrato,PagoAdmin)

