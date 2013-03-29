from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('iamcast.views',
    # Examples:
    # url(r'^$', 'alternativa.views.home', name='home'),
    # url(r'^alternativa/', include('alternativa.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'index'),
    url(r'^contratar/$', 'contratar'),
    url(r'^configurar/$', 'configurar'),
    url(r'^notificacion/pago/mp/$', 'notificacion_pago'),
    #url(r'^resultado/creacion/agencia/$', 'resultado_creacion_agencia'),
    url(r'^pago/success/(\d+)/$', 'pago_success'),
    url(r'^pago/pending/(\d+)/$', 'pago_pending'),
)

