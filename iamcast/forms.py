# coding=utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from iamcast.models import Agencia
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class AgenciaForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):

    self.helper = FormHelper()
    self.helper.form_class = 'uniForm'
    self.helper.form_method = 'post'
    self.helper.form_action = 'iamcast.views.configurar'
    self.helper.add_input(Submit('submit',_('Crear Agencia')))
 
    super(AgenciaForm, self).__init__(*args, **kwargs)

  class Meta:
    model=Agencia
    fields = ('nombre', 'usuario_gmail', 'clave_gmail')
