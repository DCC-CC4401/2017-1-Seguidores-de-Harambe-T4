from django.db import models
from multiselectfield import MultiSelectField
from django.utils import timezone
from django.utils.formats import get_format
from django.contrib.auth.models import User

# Create your models here

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to = 'avatars')
  #  tipos = ((0, 'admin'), (1, 'alumno'), (2, 'fijo'), (3, 'ambulante'))
    tipo = models.IntegerField()
    longitud = models.DecimalField(max_digits=8, decimal_places=6, default=-70.663949)
    latitud = models.DecimalField(max_digits=8, decimal_places=6, default=-33.457879)


    def __init__(self, *args, **kwargs):
        super(Usuario, self).__init__(*args, **kwargs)
        if not self.pk and not self.tipo:
            self.tipo = self.DEFAULT_TYPE

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'usuario'

class Vendedor(Usuario):
    listaFormasDePago = (
        (0, 'Efectivo'),
        (1, 'Tarjeta de Crédito'),
        (2, 'Tarjeta de Débito'),
        (3, 'Tarjeta Junaeb'),
    )
    formasDePago = MultiSelectField(choices=listaFormasDePago, null=True, blank=True)
    #longitud = models.DecimalField(max_digits=8, decimal_places=6, default=-33.457879)
    #latitud = models.DecimalField(max_digits=8, decimal_places=6, default=-70.663949)

    def __init__(self, *args, **kwargs):
        super(Usuario, self).__init__(*args, **kwargs)
        if not self.pk and not self.tipo:
            self.tipo = self.DEFAULT_TYPE

    class Meta:
        db_table = 'vendedor'

class vendedorFijo(Vendedor):
    DEFAULT_TYPE = 2
    horarioIni = models.CharField(max_length=200,blank=True,null=True)
    horarioFin = models.CharField(max_length=200,blank=True,null=True)

    class Meta:
        db_table = 'vendedorFijo'

class vendedorAmbulante(Vendedor):
    activo = models.BooleanField(default=False,blank=True)
    DEFAULT_TYPE = 3
    class Meta:
        db_table = 'vendedorAmbulante'

class alumno(Usuario):
    DEFAULT_TYPE = 1
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'alumno'

class Admin(Usuario):
    DEFAULT_TYPE = 0
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'admin'

class Comida(models.Model):
    idVendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200,primary_key=True)
    listaCategorias = (
        (0, 'Cerdo'),
        (1, 'Chino'),
        (2, 'Completos'),
        (3, 'Egipcio'),
        (4, 'Empanadas'),
        (5, 'Ensalada'),
        (6, 'Japones'),
        (7, 'Pan'),
        (8, 'Papas fritas'),
        (9, 'Pasta'),
        (10, 'Pescado'),
        (11, 'Pollo'),
        (12, 'Postres'),
        (13, 'Sushi'),
        (14, 'Vacuno'),
        (15, 'Vegano'),
        (16, 'Vegetariano'),
    )
    categorias = MultiSelectField(choices=listaCategorias)
    descripcion = models.CharField(max_length=500)
    stock = models.PositiveSmallIntegerField(default=0)
    precio = models.PositiveSmallIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Comida'


class Favoritos(models.Model):
    idAlumno = models.ForeignKey(alumno, on_delete=models.CASCADE)
    idVendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    fechaAhora = str(timezone.now()).split(' ', 1)[0]
    fecha = models.CharField(max_length=200, default=fechaAhora)

    def __str__(self):
        return str(self.idAlumno) + "X" + str(self.idVendedor)

    class Meta:
        db_table = 'Favoritos'


class Imagen(models.Model):
    id = models.AutoField(primary_key=True)
    imagen = models.ImageField(upload_to='avatars')

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'imagen'

class Transacciones(models.Model):
    my_formats = get_format('DATETIME_INPUT_FORMATS')
    idTransaccion = models.AutoField(primary_key=True)
    comida = models.ManyToManyField(Comida,blank=True)
    idVendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE,blank=True,null=True)
    precio = models.IntegerField(blank=True,null=True)
    fechaAhora = str(timezone.now()).split(' ', 1)[0]
    fecha = models.CharField(max_length=200,default=fechaAhora)

    def __str__(self):
        return str(self.idTransaccion)

    class Meta:
        db_table = 'transacciones'


class alertaPolicial(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    fechaAhora = str(timezone.now()).split(' ', 1)[0]
    fecha = models.CharField(max_length=200, default=fechaAhora)
    horaAhora = str(timezone.now()).split(' ', 1)[1].split('.')[0].split(':')[0] + ':' + str(timezone.now()).split(' ', 1)[1].split('.')[0].split(':')[1]
    hora = models.CharField(max_length=200, default=horaAhora)
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'alertaPolicial'



# class Alert(models.Model):
#     id = models.AutoField(primary_key=True)
#     activada = models.BooleanField(default=False,blank=True)
#     longitud = models.DecimalField(max_digits=8, decimal_places=6, default=-33.457879)
#     latitud = models.DecimalField(max_digits=8, decimal_places=6, default=-70.663949)
#
#     def __str__(self):
#         return str(self.id)
#
#     class Meta:
#         db_table = 'alert'
