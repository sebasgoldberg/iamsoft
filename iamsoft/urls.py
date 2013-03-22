from django.conf.urls import patterns, include, url
from iampacks.cross.usuario.forms import UsuarioAuthenticationForm

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'iamsoft.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^usuario/', include('iampacks.cross.usuario.urls')),
    #url(r'^idioma/', include('iampacks.cross.idioma.urls')),
    url(r'^iamcast/', include('iamcast.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'authentication_form':UsuarioAuthenticationForm}),
    url(r'^', include('home.urls')),
)
