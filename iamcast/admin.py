from django.contrib import admin
from iamcast.models import Agencia

class AgenciaAdmin(admin.ModelAdmin):
  list_display=['id','nombre']

admin.site.register(Agencia,AgenciaAdmin)

