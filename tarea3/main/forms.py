from django import forms

from .models import Usuario, Comida
from django import forms

class LoginForm(forms.Form):
   email = forms.CharField(max_length = 100)
   password = forms.CharField(widget = forms.PasswordInput())

   def get_email(self):
       return self.email
   def get_password(self):
       return self.password

class GestionProductosForm(forms.Form):
    idVendedor = 0
    nombre = forms.CharField(max_length=200)
    categoria = forms.IntegerField()
    descripcion = forms.CharField(max_length=500)
    stock = forms.IntegerField()
    precio = forms.IntegerField()


class editarProductosForm(forms.Form):
    foto = forms.FileField()