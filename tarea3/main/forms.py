from django import forms
from django.forms import ModelForm
from .models import Usuario, Comida
from django import forms

class LoginForm(forms.Form):
   email = forms.EmailField(max_length = 100)
   password = forms.CharField(widget = forms.PasswordInput())


class LoginUsuario(ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre','email','avatar']

class LoginVendedor(LoginUsuario):

    listaFormasDePago = (
        (0, 'Efectivo'),
        (1, 'Tarjeta de Crédito'),
        (2, 'Tarjeta de Débito'),
        (3, 'Tarjeta Junaeb'),
    )
    formasDePago = forms.MultipleChoiceField(choices=listaFormasDePago)


class LoginVendedorFijo(LoginVendedor):
    horarioIni = forms.CharField(max_length=200)
    horarioFin = forms.CharField(max_length=200)

class LoginVendedorAmbulante(LoginVendedor):
    activo = forms.BooleanField()


class GestionProductosForm(forms.Form):
    idVendedor = 0
    nombre = forms.CharField(max_length=200)
    categoria = forms.IntegerField()
    descripcion = forms.CharField(max_length=500)
    stock = forms.IntegerField()
    precio = forms.IntegerField()


class editarProductosForm(forms.Form):
    foto = forms.FileField()