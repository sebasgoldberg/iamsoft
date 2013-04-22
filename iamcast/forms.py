# coding=utf-8
from django import forms
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from iamcast.models import Agencia
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.hashers import check_password

class AgenciaForm(forms.ModelForm):

  clave_gmail=forms.CharField(widget=forms.widgets.PasswordInput, required=True, label=_('Clave de gmail'),max_length=60)
  clave_gmail2=forms.CharField(widget=forms.widgets.PasswordInput, required=True, label=_('Confirme clave de gmail'),max_length=60)

  def __init__(self, *args, **kwargs):

    self.helper = FormHelper()
    self.helper.form_class = 'uniForm'
    self.helper.form_method = 'post'
    self.helper.form_action = 'iamcast.views.configurar'
    self.helper.add_input(Submit('submit',_('Crear Agencia')))
 
    super(AgenciaForm, self).__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super(AgenciaForm, self).clean()
    clave_gmail = cleaned_data.get("clave_gmail")
    clave_gmail2 = cleaned_data.get("clave_gmail2")

    if clave_gmail and clave_gmail2:
      if clave_gmail != clave_gmail2:
        raise forms.ValidationError(ugettext(u"Las claves de gmail no coinciden"))

    return cleaned_data

  class Meta:
    model=Agencia
    fields = ('nombre', 'idioma', 'usuario_gmail', 'clave_gmail', 'clave_gmail2')

class BorrarAgenciaForm(forms.Form):
  agencia_id=forms.IntegerField(widget=forms.widgets.HiddenInput, required=True)
  username=forms.CharField(required=True, label=_('Confirme su usuario'))
  password=forms.CharField(widget=forms.widgets.PasswordInput, required=True, label=_('Confirme su clave'))

  def __init__(self, *args, **kwargs):

    self.helper = FormHelper()
    self.helper.form_class = 'uniForm'
    self.helper.form_method = 'post'
    self.helper.form_action = 'iamcast.views.borrar_agencia'
    self.helper.add_input(Submit('submit',_('Borrar Agencia')))
 
    super(BorrarAgenciaForm, self).__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super(BorrarAgenciaForm, self).clean()
    agencia_id = cleaned_data.get("agencia_id")
    username = cleaned_data.get("username")
    password = cleaned_data.get("password")

    if agencia_id and password:
      agencia = Agencia.objects.get(pk=agencia_id)
      if agencia.borrada():
        raise forms.ValidationError(ugettext(u"La agencia %s ya se encuentra borrada")%agencia.nombre)
      if agencia.user.username!=username:
        raise forms.ValidationError(ugettext(u"El usuario ingresado es inválido"))
      if not check_password(password, agencia.user.password):
        raise forms.ValidationError(ugettext(u"El password ingresado es incorrescto"))

    return cleaned_data
