from django import forms
from django.forms import ModelForm
from .models import *
from django import forms

class LoginForm(forms.Form):
   email = forms.EmailField(max_length = 100)
   password = forms.CharField(widget = forms.PasswordInput())


class LoginUsuario(ModelForm):
    class Meta:
        model = Usuario
        fields = ['id','user','nombre','email','avatar']

class LoginVendedor(LoginUsuario):
    class Meta:
        model = Vendedor
        fields = ['id', 'user', 'nombre', 'email', 'avatar']


class LoginVendedorFijo(LoginVendedor):
    class Meta:
        model = vendedorFijo
        fields = ['id', 'user', 'nombre', 'email', 'avatar','horarioIni','horarioFin']

class LoginVendedorAmbulante(LoginVendedor):
    class Meta:
        model = vendedorAmbulante
        fields = ['id', 'user', 'nombre', 'email', 'avatar','activo']



class GestionProductosForm(forms.Form):
    idVendedor = 0
    nombre = forms.CharField(max_length=200)
    categoria = forms.IntegerField()
    descripcion = forms.CharField(max_length=500)
    stock = forms.IntegerField()
    precio = forms.IntegerField()


class editarProductosForm(forms.Form):
    foto = forms.FileField()