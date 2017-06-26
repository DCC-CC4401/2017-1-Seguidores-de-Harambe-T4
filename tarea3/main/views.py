import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.utils import timezone
from .forms import *
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .forms import GestionProductosForm
from .forms import editarProductosForm
from .models import Usuario
from .models import Comida
from .models import Favoritos
from .models import Imagen
from .models import Transacciones
from django.db.models import Count
from django.db.models import Sum
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout
import simplejson
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from multiselectfield import MultiSelectField
from django.core.files.storage import default_storage
from datetime import time
from .utilities import haversine



#Vista inicial
def index(request):
    vendedores = stringVendedoresActivosConStock()
    return render(request, 'main/index.html',{'vendedores':vendedores})

def stringVendedoresActivosConStock():
    string_vend = ""
    vendedores = list(Vendedor.objects.all())
    for vendedor in vendedores:
        id = Vendedor.objects.get(nombre=vendedor).id
        categorias = categoriasVendedor(id)
        if esActivo(id) and tieneStock(id):
            v = Vendedor.objects.get(nombre=vendedor)
            nombre = v.nombre
            latitud = v.latitud
            longitud = v.longitud
            avatar = v.avatar
            string_vend+= nombre + "," + str(avatar) + "," + str(latitud) + "," + str(longitud) + "," + str(id) + "," + categorias + ";"
    if string_vend != "":
        string_vend = string_vend[:-1]
    return string_vend

def stringVendedoresActivosConStockParaAlumnos(id_alumno):
    string_vend = ""
    vendedores = list(Vendedor.objects.all())
    for vendedor in vendedores:
        id = Vendedor.objects.get(nombre=vendedor).id
        categorias = categoriasVendedor(id)
        if esActivo(id) and tieneStock(id):
            fav = "no"
            if list(Favoritos.objects.filter(idAlumno=id_alumno,idVendedor=id)) != []:
                fav = "si"
            v = Vendedor.objects.get(nombre=vendedor)
            nombre = v.nombre
            latitud = v.latitud
            longitud = v.longitud
            avatar = v.avatar
            string_vend+= nombre + "," + str(avatar) + "," + str(latitud) + "," + str(longitud) + "," + str(id) + "," + categorias + "," + fav + ";"
    if string_vend != "":
        string_vend = string_vend[:-1]
    return string_vend

def categoriasVendedor(id_vendedor):
    comidas = list(Comida.objects.filter(idVendedor=id_vendedor))
    categorias = ""
    comidas = list(Comida.objects.filter(idVendedor=id_vendedor))
    for c in comidas:
        for i in str(Comida.objects.get(nombre=c).categorias).split(", "):
            categorias += i + ":"
    if categorias == "" or categorias == ":":
        return "None"
    return categorias[:-1]


def tieneStock(id_vendedor):
    comidas = list(Comida.objects.filter(idVendedor=id_vendedor))
    for c in comidas:
        if Comida.objects.get(nombre=c).stock > 0:
            return True
    return False


#registrarse
class signup(View):
    form_class = LoginForm
    template_name = 'main/signup.html'

    def get(self, request):
        return render(request, self.template_name, {"formLoggin": LoginForm()})

    @csrf_exempt
    def post(self, request):
        tipo = int(request.POST.get("tipo"))
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        avatar = request.FILES.get("avatar")
        contraseña = request.POST.get("password")
        djangoUser = User(username=nombre, password=contraseña, email=email)
        djangoUser.save()

        if (tipo == 0):
            adminNuevo = Admin(nombre=nombre, user=djangoUser, email=email, avatar=avatar, tipo=tipo)
            adminNuevo.save()

        elif (tipo == 1):
            alumnoNuevo = alumno(nombre=nombre, user=djangoUser, email=email, avatar=avatar, tipo=tipo)
            alumnoNuevo.save()

        elif (tipo == 2 or tipo == 3):
            horaInicial = request.POST.get("horaIni")
            horaFinal = request.POST.get("horaFin")
            formasDePago = []
            if not (request.POST.get("formaDePago0") is None):
                formasDePago.append(request.POST.get("formaDePago0"))
            if not (request.POST.get("formaDePago1") is None):
                formasDePago.append(request.POST.get("formaDePago1"))
            if not (request.POST.get("formaDePago2") is None):
                formasDePago.append(request.POST.get("formaDePago2"))
            if not (request.POST.get("formaDePago3") is None):
                formasDePago.append(request.POST.get("formaDePago3"))
                if (tipo == 2):
                    longitud = float(request.POST.get("longitud"))
                    latitud = float(request.POST.get("latitud"))
                    nuevoVendedorFijo = vendedorFijo(nombre=nombre, user=djangoUser, email=email, avatar=avatar,
                                                     tipo=tipo,
                                                     longitud=longitud, latitud=latitud, horarioIni=horaInicial,
                                                     horarioFin=horaFinal)
                    nuevoVendedorFijo.save()
                else:
                    nuevoVendedorAmbulante = vendedorAmbulante(nombre=nombre, user=djangoUser, email=email,
                                                               avatar=avatar, tipo=tipo)
                    nuevoVendedorAmbulante.save()
        return render(request, 'main/login.html')

    # verificarEmail request -> JsonResponse
    # Funcion auxiliar que verifica si un mail esta disponible o no dinamicamente, recibiendo un request de ajax

#login
class login(View):
    form_class = LoginForm
    template_name = 'main/login.html'
    def get(self,request):
        return render(request, self.template_name, {"formLoggin" : LoginForm()})

    def post(self,request):
        login = LoginForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        if login.is_valid():

            #autenticar el usuario
            try:
                user = User.objects.get(email=email)
                username = User.objects.get(email=email).username
            except User.DoesNotExist:
                return render(request, self.template_name, {"error": "Usuario o contraseña invalidos","formLoggin" : LoginForm()})
            userAuth = authenticate(username=username, password=password)
            if userAuth is None:
                return render(request, self.template_name, {"error": "Usuario o contraseña invalidos", "formLoggin": LoginForm()})
            usuario = Usuario.objects.get(user=user)
            tipo = usuario.tipo

            #en caso de que se autentique, guardar sesion y enviar a la pagina
            request.session['id'] = int(usuario.id)
            print (request.session['id'])
            request.session['user'] = str(usuario.user)
            request.session['nombre'] = str(usuario.nombre)
            request.session['avatar'] = str(usuario.avatar)
            request.session['email'] = email
            request.session['tipo'] = tipo
            return inicio(request)

#volver a inicio
def inicio(request):
    tipo = request.session['tipo']
    user = User.objects.get(email=request.session['email'])
    usuario = Usuario.objects.get(user=user)
    if tipo == 0:
        adminForm = LoginUsuario(instance=usuario)
        return render(request, '#', {"formLogin": adminForm})
    if tipo == 1:
        vendedores = stringVendedoresActivosConStockParaAlumnos(request.session['id'])
        alumnoForm = LoginUsuario(instance=usuario)
        return render(request, 'main/baseUsuario.html', {"formLogin": alumnoForm, 'vendedores':vendedores})
    if tipo == 2:
        usuario = vendedorFijo.objects.get(vendedor_ptr_id=request.session['id'])
        request.session['horarioIni'] = str(usuario.horarioIni)
        request.session['horarioFin'] = str(usuario.horarioFin)
        vfijo = LoginVendedorFijo(instance=usuario)
        usuario = Vendedor.objects.get(usuario_ptr_id=request.session['id'])
        request.session['formasDePago'] = usuario.formasDePago
        request.session['favoritos'] = obtenerFavoritosVendedor(request.session['id'])
        request.session['activo'] = esActivo(request.session['id'])
        productos = obtenerProductos(request.session['id'])
        return render(request, 'main/baseUsuario.html', {"formLogin": vfijo, 'listaDeProductos': productos})
    else:
        request.session['activo'] = esActivo(request.session['id'])
        usuario = Vendedor.objects.get(usuario_ptr_id=request.session['id'])
        request.session['formasDePago'] = usuario.formasDePago
        vambulante = LoginVendedorAmbulante(instance=usuario)
        request.session['favoritos'] = obtenerFavoritosVendedor(request.session['id'])
        productos = obtenerProductos(request.session['id'])
        return render(request, 'main/baseUsuario.html', {"formLogin": vambulante, 'listaDeProductos': productos})


#editar usuario logeado
class editarUsuario(View):
    #acceder a pagina de edicion
    def get(self,request):
        usuario = Usuario.objects.get(nombre=request.session['nombre'])
        UserForm = editarPerfilUsuario(instance=usuario)
        if request.session['tipo'] == 1:
            UserForm = editarPerfilUsuario(instance=usuario)
            favoritos = obtenerFavoritos(request)
            return render(request, 'main/editar-perfil.html', {'UserInfo': UserForm,'favoritos': favoritos[0] ,'nombres':favoritos[1]})

        elif request.session['tipo'] == 2:
            usuario = vendedorFijo.objects.get(nombre=request.session['nombre'])
            UserForm = editarPerfilVendedorFijo(instance=usuario)
            return render(request, 'main/editar-perfil.html', {'UserInfo': UserForm, 'pagosActuales': usuario.formasDePago})

        elif request.session['tipo'] == 3:
            usuario = vendedorAmbulante.objects.get(nombre=request.session['nombre'])
            UserForm = editarPerfilVendedorAmbulante(instance=usuario)
            return render(request, 'main/editar-perfil.html',
                          {'UserInfo': UserForm, 'pagosActuales': usuario.formasDePago})

        return render(request,'main/editar-perfil.html', {'UserInfo': UserForm})



    #cuando se editan los datos
    def post(self,request):
        nombreOriginal = request.session['nombre']
        nuevoNombre = request.POST.get("nombre")
        nuevaImagen = request.FILES.get("avatar")
        print(request.POST)
        #cambiar nombre
        if nuevoNombre != "" and nuevoNombre != nombreOriginal:
            if Usuario.objects.filter(nombre=nuevoNombre).exists():
                data = {"respuesta": "repetido"}
                return JsonResponse(data)
            Usuario.objects.filter(nombre=nombreOriginal).update(nombre=nuevoNombre)
            request.session['nombre'] = nuevoNombre

        #cambiar imagen
        if nuevaImagen != None:
            filename = nombreOriginal + ".jpg"
            with default_storage.open('../media/avatars/' + filename, 'wb+') as destination:
                for chunk in nuevaImagen.chunks():
                    destination.write(chunk)
            Usuario.objects.filter(nombre=request.session['nombre']).update(avatar='avatars/' + filename)
            request.session['avatar'] = str(Usuario.objects.get(nombre=request.session['nombre']).avatar)

        #eliminar favoritos en caso de ser alumno
        if request.session['tipo'] == 1:
            count = int(request.POST.get("switchs")) - 1
            while(count >= 0):
                Favoritos.objects.filter(idAlumno_id=request.session['id'],idVendedor_id=request.POST.get("switch" + str(count))).delete()
                count -= 1
        # cambiar formas de pago
        if request.session['tipo'] == 2 or request.session['tipo'] == 3:
            formasDePago = ""
            alternativas = {0: "Efectivo", 1: "Tarjeta de Crédito", 2: "Tarjeta de Débito", 3: "Tarjeta Junaeb"}
            for x in range(0,4):
                if request.POST.get("formaDePago"+str(x)) == 'on':
                    formasDePago += str(x)+','
            if (formasDePago != ""):
                Vendedor.objects.filter(nombre=request.session['nombre']).update(formasDePago=formasDePago[:-1])
                request.session['formasDePago'] = formasDePago
        # cambiar horario fijo
        if request.session['tipo'] == 2:
            horaInicial = request.POST.get("horarioIni")
            horaFinal = request.POST.get("horarioFin")
            print(horaInicial, horaFinal)
            if horaInicial != '':
                vendedorFijo.objects.filter(nombre=request.session['nombre']).update(horarioIni=horaInicial)
                request.session['horarioIni'] = horaInicial
            if horaFinal != '':
                vendedorFijo.objects.filter(nombre=request.session['nombre']).update(horarioFin=horaFinal)
                request.session['horarioFin'] = horaFinal
        return inicio(request)

#agregar producto a vendedor
class agregarproductos(View):
    def get(self,request):
        return render(request, 'main/gestionar-productos.html', {'productoForm': editarProductosForm(),'contexto' : 'Agregar Producto','boton': 'Agregar Producto'})

    def post(self,request):
        print(request.POST)
        print(request.FILES)
        id_vendedor = request.session['id']
        nombre = request.POST['nombre']
        descripcion = request.POST['nombre']
        precio = request.POST['precio']
        stock = request.POST['stock']
        imagen = request.FILES['imagen']
        categorias = []
        for i in range(0,17):
            try:
                categoria =request.POST['categoria'+str(i)]
                categorias.append(str(i))
            except:
                pass
        producto = Comida(idVendedor_id = id_vendedor, categorias = categorias, nombre = nombre, descripcion = descripcion, precio = precio, stock = stock, imagen = imagen)
        producto.save()
        return inicio(request)

#editar producto de vendedor
class editarproductos(View):
    def get(self,request):
        nombre = request.GET['nombre']
        id = request.session['id']
        producto = Comida.objects.get(nombre=nombre)
        form = editarProductosForm(instance=producto)
        return render(request, 'main/gestionar-productos.html', {'productoForm': form ,'contexto' : 'Editar Producto','boton': 'Guardar Cambios'})

    def post(self,request):
        nombreOriginal = request.GET['nombre']
        id = request.session['id']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        try:
            imagen = request.FILES['imagen']
        except:
            imagen = Comida.objects.get(nombre=nombreOriginal).imagen
        categorias = []
        for i in range(0,17):
            try:
                categoria =request.POST['categoria'+str(i)]
                categorias.append(str(i))
            except:
                pass
        try:
            Comida.objects.filter(nombre=nombreOriginal).update(nombre=nombre,descripcion=descripcion,precio=precio,stock=stock,imagen=imagen,categorias=categorias)
        except:
            return self.get(request)


        return inicio(request)
#borrar producto de vendedor
@csrf_exempt
def borrarProducto(request):
    nombre = request.POST['nombre']
    Comida.objects.filter(nombre= nombre).delete()
    return inicio(request)

#deslogearse
def logOut(request):
    logout(request)
    return index(request)

class vistaVendedor(View):
    def get(self,request):
        idVendedor = int(request.GET['id'])
        try:
            usuario = Usuario.objects.get(id=idVendedor)
            tipo = usuario.tipo
            if tipo == 3:
                vendedor = vendedorAmbulante.objects.get(vendedor_ptr_id = idVendedor)
                form = editarPerfilVendedorAmbulante(instance=vendedor)

            elif tipo == 2:
                vendedor = vendedorFijo.objects.get(vendedor_ptr_id=idVendedor)
                form = editarPerfilVendedorFijo(instance=vendedor)
            else:
                return inicio(request)
            formasDePago = vendedor.formasDePago
            print(formasDePago)
            productos = obtenerProductos(idVendedor)
            if 'id' not in request.session:
                favoritos = obtenerFavoritosVendedor(idVendedor)
                login = False
            else:
                try:
                    Favoritos.objects.get(idAlumno_id=request.session['id'],idVendedor_id=idVendedor)
                    favoritos = "1"
                except:
                    favoritos = "0"
                login = True
            activo = esActivo(idVendedor)
            return render(request,'main/vistaVendedor.html',{'form': form,'tipo':tipo,'formasDePago':formasDePago,'listaDeProductos': productos,'favoritos': favoritos,'login': login,'id' : idVendedor,'activo':activo})

        except:
            return inicio(request)

#funciones auxiliares
def obtenerFavoritos(request):
    id = request.session['id']
    print (id)
    nombre = request.session['nombre']
    favoritos =[]
    nombres = []
    vendedores = Favoritos.objects.filter(idAlumno_id=id)
    for fav in vendedores:
        favoritos.append(fav.idVendedor_id)
        usuario = Usuario.objects.filter(id = fav.idVendedor_id)
        nombre = usuario.get().nombre
        nombres.append(nombre)
    return [favoritos,nombres]

def obtenerProductos(id):
    listaDeProductos = []
    i = 0
    for producto in Comida.objects.filter(idVendedor_id = int(id)):
        listaDeProductos.append([])
        listaDeProductos[i].append(producto.nombre)
        categoria = str(producto.categorias)
        listaDeProductos[i].append(categoria)
        listaDeProductos[i].append(producto.stock)
        listaDeProductos[i].append(producto.precio)
        listaDeProductos[i].append(producto.descripcion)
        listaDeProductos[i].append(str(producto.imagen))
        i += 1
    if listaDeProductos == []:
        listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')

    return listaDeProductos

def obtenerFavoritosVendedor(idVendedor):
    favoritos = 0
    favoritos = Favoritos.objects.filter(idVendedor_id = idVendedor)
    favoritos = favoritos.count()
    return favoritos

def esActivo(idVendedor):
    tipo = int(Usuario.objects.get(id=idVendedor).tipo)
    if tipo == 2:
        usuario = vendedorFijo.objects.get(vendedor_ptr_id=idVendedor)
        horarioIni = usuario.horarioIni
        horarioIni = time(int(horarioIni[:2]),int(horarioIni[3:5]))
        horarioFin = usuario.horarioFin
        horarioFin = time(int(horarioFin[:2]), int(horarioFin[3:5]))
        if horarioIni <= time(datetime.datetime.now().hour,datetime.datetime.now().minute) <= horarioFin:
            return True
        else:
            return False
    elif tipo == 3:
        usuario = vendedorAmbulante.objects.get(vendedor_ptr_id=idVendedor)
        return  bool(usuario.activo)

def cambiarEstado(request):
    if request.method == 'GET':
        if request.is_ajax():
            print("sucess")
            estado = request.GET.get('estado')
            id_vendedor = request.GET.get('id')
            if estado == "true":
                vendedorAmbulante.objects.filter(vendedor_ptr_id=id_vendedor).update(activo=True)
                request.session['activo'] = True
            else:
                vendedorAmbulante.objects.filter(vendedor_ptr_id=id_vendedor).update(activo=False)
                request.session['activo'] = False
            data = {"estado": estado}
            return JsonResponse(data)

class signup(View):
    form_class = LoginForm
    template_name = 'main/signup.html'

    def get(self, request):
        return render(request, self.template_name, {"formLoggin": LoginForm()})

    @csrf_exempt
    def post(self, request):
        tipo = int(request.POST.get("tipo"))
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        avatar = request.FILES.get("avatar")
        password = request.POST.get("password")
        contraseña = make_password(request.POST.get("password"))
        djangoUser = User(username=nombre, password=contraseña, email=email)
        djangoUser.save()

        if (tipo == 0):
            adminNuevo = Admin(nombre=nombre, user=djangoUser, email=email, avatar=avatar, tipo=tipo)
            adminNuevo.save()

        elif (tipo == 1):
            alumnoNuevo = alumno(nombre=nombre, user=djangoUser, email=email, avatar=avatar, tipo=tipo)
            alumnoNuevo.save()

        elif (tipo == 2 or tipo == 3):
            horaInicial = request.POST.get("horaIni")
            horaFinal = request.POST.get("horaFin")
            formasDePago = []
            if not (request.POST.get("formaDePago0") is None):
                formasDePago.append(request.POST.get("formaDePago0"))
            if not (request.POST.get("formaDePago1") is None):
                formasDePago.append(request.POST.get("formaDePago1"))
            if not (request.POST.get("formaDePago2") is None):
                formasDePago.append(request.POST.get("formaDePago2"))
            if not (request.POST.get("formaDePago3") is None):
                formasDePago.append(request.POST.get("formaDePago3"))

            if (tipo == 2):
                longitud = float(request.POST.get("longitud"))
                latitud = float(request.POST.get("latitud"))
                nuevoVendedorFijo = vendedorFijo(nombre=nombre, user=djangoUser, email=email, avatar=avatar,
                                                     tipo=tipo,
                                                     longitud=longitud, latitud=latitud, horarioIni=horaInicial,
                                                     horarioFin=horaFinal)
                nuevoVendedorFijo.save()
            else:
                nuevoVendedorAmbulante = vendedorAmbulante(nombre=nombre, user=djangoUser, email=email,
                                                               avatar=avatar, tipo=tipo)
                nuevoVendedorAmbulante.save()

        return inicio(request)

    # verificarEmail request -> JsonResponse
    # Funcion auxiliar que verifica si un mail esta disponible o no dinamicamente, recibiendo un request de ajax

@csrf_exempt
def verificarEmail(request):
    if request.is_ajax() or request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            data = {"respuesta": "disponible"}
            return JsonResponse(data)
        data = {"respuesta": "repetido"}
        return JsonResponse(data)

def modificarStock(request):
    if request.method == "GET":
        producto = request.GET.get("nombre")
        stock = int(Comida.objects.get(nombre=producto).stock)
        if request.GET.get("op") == "suma":
            nuevoStock = stock + 1
            Comida.objects.filter(nombre=producto).update(stock=nuevoStock)
        if request.GET.get("op") == "resta":
            nuevoStock = stock - 1
            if stock == 0:
                return JsonResponse({"stock": stock})
            Comida.objects.filter(nombre=producto).update(stock=nuevoStock)
    return JsonResponse({"stock": stock})

def cambiarFavorito(request):
    if request.method == "GET":
        if request.is_ajax():
            favorito = request.GET.get('favorito')
            agregar = request.GET.get('agregar')
            if agregar == "si":
                print("paso")
                print(favorito)
                nuevoFavorito = Favoritos()
                nuevoFavorito.idAlumno_id = request.session['id']
                nuevoFavorito.idVendedor_id = favorito
                nuevoFavorito.save()
                respuesta = {"respuesta": "si"}
            else:
                Favoritos.objects.filter(idAlumno_id=request.session['id']).filter(idVendedor_id=favorito).delete()
                respuesta = {"respuesta": "no"}
            return JsonResponse(respuesta)

@csrf_exempt
def filtrarCategorias(request):
    if request.method == "POST":
        if request.is_ajax():
            filtros = request.POST.lists()
            listaFiltrada = []
            for key,values in filtros:
                listaFiltrada.append(values[0])
            return JsonResponse({"filtros":listaFiltrada})



#vista que carga la pagina para editar datos de alumno
#envia toda la informacion del usuario y los favoritos respectivos
# def editarPerfilAlumno(request):
#     avatar = request.session['avatar']
#     id = request.session['id']
#     nombre =request.session['nombre']
#     favoritos =[]
#     nombres = []
#     for fav in Favoritos.objects.raw("SELECT * FROM Favoritos"):
#         if id == fav.idAlumno:
#             favoritos.append(fav.idVendedor)
#             vendedor = Usuario.objects.filter(id =fav.idVendedor).get()
#             nombre = vendedor.nombre
#             nombres.append(nombre)
#     return render(request,'main/editar-perfil-alumno.html',{"id": id, "avatarSesion": avatar,"nombre": nombre,"favoritos": favoritos, "nombres": nombres, "nombresesion":request.session['nombre']})
#
#
# #vista que procesa el perfil de alumno por ajax
# #recibe por POST los parametros a modificar
# #modifica tanto la tabla de usuarios como la de favoritos
# def procesarPerfilAlumno(request):
#     if request.method == "POST":
#         nombreOriginal = request.session['nombre']
#         nuevoNombre = request.POST.get("nombre")
#         count = request.POST.get("switchs")
#         aEliminar= []
#         nuevaImagen = request.FILES.get("comida")
#         for i in range(int(count)):
#             fav = request.POST.get("switch"+str(i))
#             if fav != "":
#                 aEliminar.append(fav)
#         print(request.POST)
#         print(request.FILES)
#         print(aEliminar)
#
#         if nuevoNombre != "":
#             if Usuario.objects.filter(nombre=nuevoNombre).exists():
#                 data = {"respuesta": "repetido"}
#                 return JsonResponse(data)
#             Usuario.objects.filter(nombre=nombreOriginal).update(nombre=nuevoNombre)
#
#         for i in aEliminar:
#             for fav in Favoritos.objects.raw("SELECT * FROM Favoritos"):
#                 if request.session['id'] == fav.idAlumno:
#                     if int(i) == fav.idVendedor:
#                         Favoritos.objects.filter(idAlumno=request.session['id']).filter(idVendedor=int(i)).delete()
#         if nuevaImagen != None:
#             filename = nombreOriginal + ".jpg"
#             with default_storage.open('../media/avatars/' + filename, 'wb+') as destination:
#                 for chunk in nuevaImagen.chunks():
#                     destination.write(chunk)
#             Usuario.objects.filter(id=request.session['id']).update(avatar='/avatars/' + filename)
#
#         return JsonResponse({"ejemplo": "correcto"})


#def signup(request):
#    return render(request, 'main/signup.html', {})

def loginReq(request):
    #inicaliar variables
    tipo = 0
    nombre=''
    url = ''
    id = 0
    horarioIni = 0
    horarioFin = 0
    encontrado = False
    email = request.POST.get("email")
    avatar = ''
    contraseña = ''
    password = request.POST.get("password")
    listaDeProductos = []
    formasDePago = []
    activo = False

    #buscar vendedor en base de datos
    MyLoginForm = LoginForm(request.POST)
    if MyLoginForm.is_valid():
        vendedores = []
        for p in Usuario.objects.raw('SELECT * FROM usuario'):
            if p.contraseña == password and p.email == email:
                tipo = p.tipo
                nombre = p.nombre
                if (tipo == 0):
                    url = 'main/baseAdmin.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar
                    contraseña = p.contraseña
                    break
                elif (tipo == 1):
                    url = 'main/baseAlumno.html'
                    id = p.id
                    avatar = p.avatar
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar

                    break
                elif (tipo == 2):
                    url = 'main/vendedor-fijo.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    horarioIni = p.horarioIni
                    horarioFin = p.horarioFin
                    request.session['horarioIni'] = horarioIni
                    request.session['horarioFin'] = horarioFin
                    avatar = p.avatar
                    activo = p.activo
                    formasDePago = p.formasDePago
                    request.session['formasDePago'] = formasDePago
                    request.session['activo'] = activo
                    break
                elif (tipo == 3):
                    url = 'main/vendedor-ambulante.html'
                    id = p.id
                    tipo = p.tipo
                    encontrado = True
                    avatar = p.avatar
                    activo = p.activo
                    formasDePago = p.formasDePago
                    request.session['formasDePago'] = formasDePago
                    request.session['activo'] = activo
                    break

        #si no se encuentra el usuario, se retorna a pagina de login
        if encontrado==False:
            return render(request, 'main/login.html', {"error": "Usuario o contraseña invalidos"})

        #crear datos de sesion
        request.session['id'] = id
        request.session['tipo'] = tipo
        request.session['email'] = email
        request.session['nombre'] = nombre
        request.session['avatar'] = str(avatar)
        # si son vendedores, crear lista de productos
        for p in Usuario.objects.raw('SELECT * FROM usuario'):
            if p.tipo == 2 or p.tipo == 3:
                vendedores.append(p.id)
        vendedoresJson = simplejson.dumps(vendedores)

        #obtener alimentos en caso de que sea vendedor fijo o ambulante
        if tipo == 2 or tipo == 3:
            i = 0
            for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id) +'"'):
                listaDeProductos.append([])
                listaDeProductos[i].append(producto.nombre)
                categoria = str(producto.categorias)
                listaDeProductos[i].append(categoria)
                listaDeProductos[i].append(producto.stock)
                listaDeProductos[i].append(producto.precio)
                listaDeProductos[i].append(producto.descripcion)
                listaDeProductos[i].append(str(producto.imagen))
                i += 1

        listaDeProductos = simplejson.dumps(listaDeProductos,ensure_ascii=False).encode('utf8')

        #limpiar argumentos de salida segun tipo de vista
        argumentos ={"email": email, "tipo": tipo, "id": id,"vendedores": vendedoresJson, "nombre": nombre, "horarioIni": horarioIni, "horarioFin" : horarioFin, "avatar" : avatar, "listaDeProductos" : listaDeProductos}
        if (tipo == 0):
            request.session['contraseña'] = contraseña
            return adminPOST(id, avatar, email, nombre,contraseña, request)
        if (tipo == 1):
            argumentos = {"nombresesion": nombre,  "tipo": tipo, "id": id,"vendedores": vendedoresJson, "avatarSesion": avatar}
        if (tipo == 2):
            request.session['listaDeProductos'] = str(listaDeProductos)
            request.session['favoritos'] = obtenerFavoritos(id)
            argumentos = {"nombre": nombre,  "tipo": tipo, "id": id,"horarioIni": horarioIni, "favoritos":obtenerFavoritos(id), "horarioFin" : horarioFin, "avatar" : avatar, "listaDeProductos" : listaDeProductos, "activo" : activo, "formasDePago" : formasDePago, "activo" : activo}
        if (tipo ==3):
            request.session['listaDeProductos'] = str(listaDeProductos)
            request.session['favoritos'] = obtenerFavoritos(id)
            argumentos ={"nombre": nombre,  "tipo": tipo, "id": id,"avatar" : avatar, "favoritos":obtenerFavoritos(id), "listaDeProductos" : listaDeProductos, "activo" : activo, "formasDePago" : formasDePago}

        #enviar a vista respectiva de usuario
        return render(request, url, argumentos)

    #retornar en caso de datos invalidos
    else:
        return render(request, 'main/login.html', {"error" : "Usuario o contraseña invalidos"})




class Dashboard(View):
    template_name = 'main/vistaDashboard.html'

    @csrf_exempt
    def post(self, request):
        print(request.POST)
        id = int(request.POST.get("vendedorId"))

        # transacciones hechas por hoy
        #transaccionesDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(conteo=Count('fecha'))
        #temp_transaccionesDiarias = list(transaccionesDiarias)
        transaccionesDiariasArr = []

        #for element in temp_transaccionesDiarias:
        #    aux = []
        #    aux.append(element['fecha'])
        #    aux.append(element['conteo'])
        #    transaccionesDiariasArr.append(aux)
        #transaccionesDiariasArr = simplejson.dumps(transaccionesDiariasArr)

    # print(transaccionesDiariasArr)

        #ganancias de hoy
        gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(ganancia=Sum('precio'))
        temp_gananciasDiarias = list(gananciasDiarias)
        gananciasDiariasArr = []
        for element in temp_gananciasDiarias:
            aux = []
            aux.append(element['fecha'])
            aux.append(element['ganancia'])
            gananciasDiariasArr.append(aux)
        gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
        print(gananciasDiariasArr)


        #todos los productos del vendedor
        productos = Comida.objects.filter(idVendedor=id).values('nombre','precio')
        temp_productos = list(productos)
        productosArr = []
        productosPrecioArr = []
        for element in temp_productos:
            aux = []
            productosArr.append(element['nombre'])
            aux.append(element['nombre'])
            aux.append(element['precio'])
            productosPrecioArr.append(aux)
        productosArr = simplejson.dumps(productosArr)
        productosPrecioArr = simplejson.dumps(productosPrecioArr)
        print(productosPrecioArr)

        #productos vendidos hoy con su cantidad respectiva
        fechaHoy = str(timezone.now()).split(' ', 1)[0]
        print("FECHA HOY:" + fechaHoy)
        productosHoy = Transacciones.objects.filter(idVendedor=id,fecha=fechaHoy).values('comida').annotate(conteo=Count('comida'))
        temp_productosHoy = list(productosHoy)
        productosHoyArr = []
        for element in temp_productosHoy:
             aux = []
             aux.append(element['comida'])
             aux.append(element['conteo'])
             productosHoyArr.append(aux)
        productosHoyArr = simplejson.dumps(productosHoyArr)
        print(productosHoyArr)
        return render(request, 'main/dashboard.html', {"transacciones":transaccionesDiariasArr,"ganancias":gananciasDiariasArr,"productos":productosArr,"productosHoy":productosHoyArr,"productosPrecio":productosPrecioArr})


@csrf_exempt
def dataDashboard(request):
    if request.is_ajax():
        print("DATA DASHBOARD")
        print(request.POST)
        id = int(request.POST.get("id"))
        fechaHoy = request.POST.get('dateDay')
        #print("FECHA HOY:" + fechaHoy)
        productosHoy = Transacciones.objects.filter(idVendedor=id, fecha=fechaHoy).values('comida').annotate(
            conteo=Count('comida'))
        temp_productosHoy = list(productosHoy)
        productosHoyArr = []
        for element in temp_productosHoy:
            aux = []
            aux.append(element['comida'])
            aux.append(element['conteo'])
            productosHoyArr.append(aux)
        productosHoyArr = simplejson.dumps(productosHoyArr)
        print(productosHoyArr)
        respuesta = {"datos": productosHoyArr}
        return JsonResponse(respuesta)


# def ambulanteDashboard(request):
#     print(request.POST)
#     id = request.POST.get("ambulanteId")
#     #id = str(id)
#
#
#     #transacciones hechas por hoy
#     transaccionesDiarias=Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(conteo=Count('fecha'))
#     temp_transaccionesDiarias = list(transaccionesDiarias)
#     transaccionesDiariasArr = []
#     for element in temp_transaccionesDiarias:
#         aux = []
#         aux.append(element['fecha'])
#         aux.append(element['conteo'])
#         transaccionesDiariasArr.append(aux)
#     transaccionesDiariasArr=simplejson.dumps(transaccionesDiariasArr)
#     #print(transaccionesDiariasArr)
#
#     #ganancias de hoy
#     gananciasDiarias = Transacciones.objects.filter(idVendedor=id).values('fecha').annotate(ganancia=Sum('precio'))
#     temp_gananciasDiarias = list(gananciasDiarias)
#     gananciasDiariasArr = []
#     for element in temp_gananciasDiarias:
#         aux = []
#         aux.append(element['fecha'])
#         aux.append(element['ganancia'])
#         #print("AUX")
#         #print(aux)
#         gananciasDiariasArr.append(aux)
#     gananciasDiariasArr = simplejson.dumps(gananciasDiariasArr)
#     #print(gananciasDiariasArr)
#
#
#     #todos los productos del vendedor
#     productos = Comida.objects.filter(idVendedor=id).values('nombre','precio')
#     temp_productos = list(productos)
#     productosArr = []
#     productosPrecioArr = []
#     for element in temp_productos:
#         aux = []
#         productosArr.append(element['nombre'])
#         aux.append(element['nombre'])
#         aux.append(element['precio'])
#         productosPrecioArr.append(aux)
#     productosArr = simplejson.dumps(productosArr)
#     productosPrecioArr = simplejson.dumps(productosPrecioArr)
#     print(productosPrecioArr)
#
#     #productos vendidos hoy con su cantidad respectiva
#     fechaHoy = str(timezone.now()).split(' ', 1)[0]
#     productosHoy = Transacciones.objects.filter(idVendedor=id,fecha=fechaHoy).values('nombreComida').annotate(conteo=Count('nombreComida'))
#     temp_productosHoy = list(productosHoy)
#     productosHoyArr = []
#     for element in temp_productosHoy:
#         aux = []
#         aux.append(element['nombreComida'])
#         aux.append(element['conteo'])
#         productosHoyArr.append(aux)
#     productosHoyArr = simplejson.dumps(productosHoyArr)
#     #print(productosHoyArr)
#
#
#     return render(request, 'main/ambulanteDashboard.html', {"transacciones":transaccionesDiariasArr,"ganancias":gananciasDiariasArr,"productos":productosArr,"productosHoy":productosHoyArr,"productosPrecio":productosPrecioArr})
#
#
# def adminEdit(request):
#     print(request.POST)
#     nombre = request.POST.get("adminName")
#     print(nombre)
#     contraseña = request.POST.get("adminPassword")
#     print(contraseña)
#     id = request.POST.get("adminId")
#     print(id)
#     email = request.POST.get("adminEmail")
#     print(email)
#     avatar = request.POST.get("adminAvatar")
#     print(avatar)
#     return render(request, 'main/adminEdit.html', {"nombre" : nombre,"contraseña":contraseña,"id":id,"email":email,"avatar":avatar})
#

#
# def signupAdmin(request):
#     return render(request, 'main/signupAdmin.html', {})
#
# def loggedin(request):
#     return render(request, 'main/loggedin.html', {})
#
# def loginAdmin(request):
#     print("POST: ")
#     print(request.POST)
#     id = request.POST.get("userID")
#     email = request.POST.get("email")
#     avatar = "avatars/"+request.POST.get("fileName")
#     nombre = request.POST.get("name")
#     contraseña = request.POST.get("password")
#     return adminPOST(id,avatar,email,nombre,contraseña,request)
#
#
# def adminPOST(id,avatar,email,nombre,contraseña,request):
#     #ids de todos los usuarios no admins
#     datosUsuarios = []
#     i = 0
#     numeroUsuarios= Usuario.objects.count()
#     numeroDeComidas = Comida.objects.count()
#     for usr in Usuario.objects.raw('SELECT * FROM usuario WHERE tipo != 0'):
#         datosUsuarios.append([])
#         datosUsuarios[i].append(usr.id)
#         datosUsuarios[i].append(usr.nombre)
#         datosUsuarios[i].append(usr.email)
#         datosUsuarios[i].append(usr.tipo)
#         datosUsuarios[i].append(str(usr.avatar))
#         datosUsuarios[i].append(usr.activo)
#         datosUsuarios[i].append(usr.formasDePago)
#         datosUsuarios[i].append(usr.horarioIni)
#         datosUsuarios[i].append(usr.horarioFin)
#         datosUsuarios[i].append(usr.contraseña)
#
#         i += 1
#     listaDeUsuarios = simplejson.dumps(datosUsuarios, ensure_ascii=False).encode('utf8')
#     hola = "hola"
#     # print(listaDeUsuarios)
#
#     # limpiar argumentos de salida segun tipo de vista
#     argumentos = {"nombre":nombre,"id":id,"avatar":avatar,"email":email,"lista":listaDeUsuarios,"numeroUsuarios":numeroUsuarios,"numeroDeComidas":numeroDeComidas,"contraseña":contraseña}
#     return render(request, 'main/baseAdmin.html', argumentos)
#

#
#
#
#
#
# def gestionproductos(request):
#     if request.session.has_key('id'):
#         email = request.session['email']
#         tipo = request.session['tipo']
#         id = request.session['id']
#         if tipo == 3:
#             path = "main/baseVAmbulante.html"
#         if tipo == 2:
#             path = "main/baseVFijo.html"
#     return render(request, 'main/gestionar-productos.html', {"path" : path})
#
# def vendedorprofilepage(request):
#     return render(request, 'main/vendedor-profile-page.html', {})
#
# def formView(request):
#    if request.session.has_key('id'):
#       email = request.session['email']
#       tipo = request.session['tipo']
#       id = request.session['id']
#       if (tipo == 0):
#           url = 'main/baseAdmin.html'
#       elif (tipo == 1):
#           url = 'main/baseAlumno.html'
#       elif (tipo == 2):
#           url = 'main/vendedor-fijo.html'
#       elif (tipo == 3):
#           url = 'main/vendedor-ambulante.html'
#       return render(request, url, {"email" : email, "tipo" : tipo, "id": id})
#    else:
#       return render(request, 'main/base.html', {})
#

#
# def register(request):
#     tipo = request.POST.get("tipo")
#     nombre = request.POST.get("nombre")
#     email = request.POST.get("email")
#     password = request.POST.get("password")
#     horaInicial = request.POST.get("horaIni")
#     horaFinal = request.POST.get("horaFin")
#     avatar = request.FILES.get("avatar")
#     print(avatar)
#     formasDePago =[]
#     if not (request.POST.get("formaDePago0") is None):
#         formasDePago.append(request.POST.get("formaDePago0"))
#     if not (request.POST.get("formaDePago1") is None):
#         formasDePago.append(request.POST.get("formaDePago1"))
#     if not (request.POST.get("formaDePago2") is None):
#         formasDePago.append(request.POST.get("formaDePago2"))
#     if not (request.POST.get("formaDePago3") is None):
#         formasDePago.append(request.POST.get("formaDePago3"))
#     usuarioNuevo = Usuario(nombre=nombre,email=email,tipo=tipo,contraseña=password,avatar=avatar,formasDePago=formasDePago,horarioIni=horaInicial,horarioFin=horaFinal)
#     usuarioNuevo.save()
#     return loginReq(request)
#
# #vista que procesa el formulario para agregar productos
# def productoReq(request):
#     horarioIni = 0
#     horarioFin = 0
#     avatar = ""
#     #verificar que se hayan enviado los datos por POST
#     if request.method == "POST":
#         if request.session.has_key('id'):
#             id = request.session['id']
#             email = request.session['email']
#             tipo = request.session['tipo']
#             if tipo == 3:
#                 path = "main/baseVAmbulante.html"
#                 url ="main/vendedor-ambulante.html"
#             if tipo == 2:
#                 path = "main/baseVFijo.html"
#                 url = "main/vendedor-fijo.html"
#             Formulario = GestionProductosForm(request.POST)
#             if Formulario.is_valid():
#                 producto = Comida()
#                 producto.idVendedor = id
#                 producto.nombre = request.POST.get("nombre")
#                 producto.imagen = request.FILES.get("comida")
#                 producto.precio = request.POST.get("precio")
#                 producto.stock = request.POST.get("stock")
#                 producto.descripcion = request.POST.get("descripcion")
#                 producto.categorias = request.POST.get("categoria")
#                 producto.save()
#             else:
#                 return render(request, 'main/gestionar-productos.html', {"path" : path, "respuesta": "¡Ingrese todos los datos!"})
#
#     # obtener alimentos en caso de que sea vendedor fijo o ambulante
#     i = 0
#     listaDeProductos=[]
#     for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id) + '"'):
#         listaDeProductos.append([])
#         listaDeProductos[i].append(producto.nombre)
#         categoria = str(producto.categorias)
#         listaDeProductos[i].append(categoria)
#         listaDeProductos[i].append(producto.stock)
#         listaDeProductos[i].append(producto.precio)
#         listaDeProductos[i].append(producto.descripcion)
#         listaDeProductos[i].append(str(producto.imagen))
#         i += 1
#     listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')
#
#     for p in Usuario.objects.raw('SELECT * FROM usuario'):
#         if p.id == id:
#             avatar = p.avatar
#             horarioIni = p.horarioIni
#             horarioFin = p.horarioFin
#             nombre = p.nombre
#     return render(request, url, {"email": email, "tipo": tipo, "id": id, "nombre": nombre, "horarioIni": horarioIni, "horarioFin" : horarioFin, "avatar" : avatar, "listaDeProductos" : listaDeProductos})
#
#
# #vista de vendedor para alumnos logeados
# #recibe los datos del vendedor por medio de POST y los envia a la template respectiva
# def vistaVendedorPorAlumno(request):
#     if request.method == 'POST':
#         id = int(request.POST.get("id"))
#         for p in Usuario.objects.raw('SELECT * FROM usuario'):
#             if p.id == id:
#                 favorito = 0
#                 for f in Favoritos.objects.raw('SELECT * FROM Favoritos'):
#                     if request.session['id'] == f.idAlumno:
#                         if id == f.idVendedor:
#                             favorito = 1
#                 tipo = p.tipo
#                 nombre = p.nombre
#                 avatar = p.avatar
#                 formasDePago = p.formasDePago
#                 horarioIni = p.horarioIni
#                 horarioFin = p.horarioFin
#                 if tipo == 3:
#                     url = 'main/vendedor-ambulante-vistaAlumno.html'
#                     break
#                 if tipo == 2:
#                     url = 'main/vendedor-fijo-vistaAlumno.html'
#                     break
#     # obtener alimentos
#     i = 0
#     listaDeProductos = []
#     for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id) + '"'):
#         listaDeProductos.append([])
#         listaDeProductos[i].append(producto.nombre)
#         categoria = str(producto.categorias)
#         listaDeProductos[i].append(categoria)
#         listaDeProductos[i].append(producto.stock)
#         listaDeProductos[i].append(producto.precio)
#         listaDeProductos[i].append(producto.descripcion)
#         listaDeProductos[i].append(str(producto.imagen))
#         i += 1
#     avatarSesion = request.session['avatar']
#     listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')
#     return render(request, url, {"nombre": nombre, "nombresesion":request.session['nombre'], "tipo": tipo, "id": id, "avatar" : avatar, "listaDeProductos" :listaDeProductos,"avatarSesion": avatarSesion,"favorito": favorito, "formasDePago": formasDePago, "horarioIni": horarioIni, "horarioFin" : horarioFin, })
#
# #vista de vendedor para usuarios sin logearse
# #recibe los datos del vendedor por medio de POST y los envia a la template respectiva
# def vistaVendedorPorAlumnoSinLogin(request):
#     if request.method == 'POST':
#         id = int(request.POST.get("id"))
#         for p in Usuario.objects.raw('SELECT * FROM usuario'):
#             if p.id == id:
#                 tipo = p.tipo
#                 nombre = p.nombre
#                 avatar = p.avatar
#                 formasDePago = p.formasDePago
#                 horarioIni = p.horarioIni
#                 horarioFin = p.horarioFin
#                 activo = p.activo
#                 if tipo == 3:
#                     url = 'main/vistaVendedor.html'
#                     break
#                 if tipo == 2:
#                     url = 'main/vendedor-fijo-vistaAlumno-sinLogin.html'
#                     break
#                     # obtener alimentos
#     i = 0
#     listaDeProductos = []
#     for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id) + '"'):
#         listaDeProductos.append([])
#         listaDeProductos[i].append(producto.nombre)
#         categoria = str(producto.categorias)
#         listaDeProductos[i].append(categoria)
#         listaDeProductos[i].append(producto.stock)
#         listaDeProductos[i].append(producto.precio)
#         listaDeProductos[i].append(producto.descripcion)
#         listaDeProductos[i].append(str(producto.imagen))
#         i += 1
#     listaDeProductos = simplejson.dumps(listaDeProductos, ensure_ascii=False).encode('utf8')
#     return render(request, url, {"nombre": nombre, "tipo": tipo, "id": id,"avatar" : avatar, "listaDeProductos" :listaDeProductos, "formasDePago": formasDePago,  "horarioIni": horarioIni, "horarioFin" : horarioFin, "activo" : activo})
#
#
#
#
# @csrf_exempt
# def editarVendedor(request):
#     if request.session.has_key('id'):
#         id = request.session['id']
#         nombre = request.session['nombre']
#         formasDePago = request.session['formasDePago']
#         avatar = request.session['avatar']
#         tipo = request.session['tipo']
#         activo = request.session['activo']
#         listaDeProductos = request.session['listaDeProductos']
#         favoritos = request.session['favoritos']
#         if (tipo == 2):
#             horarioIni = request.session['horarioIni']
#             horarioFin = request.session['horarioFin']
#             argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "horarioIni": horarioIni, "horarioFin": horarioFin,
#                           "avatar": avatar, "listaDeProductos": listaDeProductos, "activo": activo, "formasDePago": formasDePago, "favoritos": favoritos}
#             url = 'main/editar-vendedor-fijo.html'
#         elif (tipo == 3):
#             argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "avatar": avatar, "listaDeProductos": listaDeProductos,
#                   "activo": activo, "formasDePago": formasDePago, "favoritos": favoritos}
#             url = 'main/editar-vendedor-ambulante.html'
#         return render(request, url, argumentos)
#     else:
#         return render(request, 'main/base.html', {})
#
#
# @csrf_exempt
# def editarDatos(request):
#     id_vendedor = request.POST.get("id_vendedor")
#     usuario = Usuario.objects.filter(id=id_vendedor)
#
#     nombre = request.POST.get("nombre")
#     tipo = request.POST.get("tipo")
#
#     if (tipo == "2"):
#         horaInicial = request.POST.get("horaIni")
#         horaFinal = request.POST.get("horaFin")
#         print(tipo, horaInicial, horaFinal)
#         if (not(horaInicial is None)):
#             usuario.update(horarioIni=horaInicial)
#         if (not(horaFinal is None)):
#             usuario.update(horarioFin=horaFinal)
#             # actualizar vendedores fijos
#         for p in Usuario.objects.raw('SELECT * FROM usuario'):
#             if p.tipo == 2:
#                 hi = p.horarioIni
#                 hf = p.horarioFin
#                 horai = hi[:2]
#                 horaf = hf[:2]
#                 mini = hi[3:5]
#                 minf = hf[3:5]
#                 print(datetime.datetime.now().time())
#                 tiempo = str(datetime.datetime.now().time())
#                 print(tiempo)
#                 hora = tiempo[:2]
#                 minutos = tiempo[3:5]
#                 estado = ""
#                 if horaf >= hora and hora >= horai:
#                     if horai == hora:
#                         if minf >= minutos and minutos >= mini:
#                             estado = "activo"
#                         else:
#                             estado = "inactivo"
#                     elif horaf == hora:
#                         if minf >= minutos and minutos >= mini:
#                             estado = "activo"
#                         else:
#                             estado = "inactivo"
#                     else:
#                         estado = "activo"
#                 else:
#                     estado = "inactivo"
#                 if estado == "activo":
#                     Usuario.objects.filter(nombre=p.nombre).update(activo=1)
#                 else:
#                     Usuario.objects.filter(nombre=p.nombre).update(activo=0)
#     avatar = request.FILES.get("avatar")
#     formasDePago = ""
#     if not (request.POST.get("formaDePago0") is None) and request.POST.get("formaDePago0")!="":
#         formasDePago += '0,'
#     if not (request.POST.get("formaDePago1") is None) and request.POST.get("formaDePago1")!="":
#         formasDePago += '1,'
#     if not (request.POST.get("formaDePago2") is None) and request.POST.get("formaDePago2")!="":
#         formasDePago += '2,'
#     if not (request.POST.get("formaDePago3") is None) and request.POST.get("formaDePago3")!="":
#         formasDePago += '3,'
#
#     if (nombre is not None and nombre!=""):
#         usuario.update(nombre=nombre)
#     if (formasDePago != ""):
#         usuario.update(formasDePago=formasDePago[:-1])
#     if (avatar is not None and avatar!=""):
#         with default_storage.open('../media/avatars/' + str(avatar), 'wb+') as destination:
#             for chunk in avatar.chunks():
#                 destination.write(chunk)
#         usuario.update(avatar='/avatars/'+ str(avatar))
#
#     print(id_vendedor)
#     return redirigirEditar(id_vendedor, request)
#
#
# def redirigirEditar(id_vendedor,request):
#     for usr in Usuario.objects.raw('SELECT * FROM usuario WHERE id == "' + str(id_vendedor) +'"'):
#         id = usr.id
#         nombre = usr.nombre
#         email = usr.email
#         tipo = usr.tipo
#         avatar = usr.avatar
#         activo = usr.activo
#         formasDePago = usr.formasDePago
#         horarioIni = usr.horarioIni
#         horarioFin = usr.horarioFin
#         favoritos = obtenerFavoritos(id_vendedor)
#
#         request.session['id'] = id
#         request.session['nombre'] = nombre
#         request.session['formasDePago'] = formasDePago
#         request.session['avatar'] = str(avatar)
#         request.session['tipo'] = tipo
#         request.session['activo'] = activo
#         request.session['horarioIni'] = horarioIni
#         request.session['horarioFin'] = horarioFin
#         request.session['favoritos'] = favoritos
#
#         listaDeProductos = []
#         i = 0
#         url = ''
#         argumentos = {}
#         for producto in Comida.objects.raw('SELECT * FROM comida WHERE idVendedor = "' + str(id_vendedor) +'"'):
#             listaDeProductos.append([])
#             listaDeProductos[i].append(producto.nombre)
#             categoria = str(producto.categorias)
#             listaDeProductos[i].append(categoria)
#             listaDeProductos[i].append(producto.stock)
#             listaDeProductos[i].append(producto.precio)
#             listaDeProductos[i].append(producto.descripcion)
#             listaDeProductos[i].append(str(producto.imagen))
#             i += 1
#
#         listaDeProductos = simplejson.dumps(listaDeProductos,ensure_ascii=False).encode('utf8')
#         request.session['listaDeProductos'] = str(listaDeProductos)
#         if (tipo == 2):
#             url = 'main/vendedor-fijo.html'
#             argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "horarioIni": horarioIni, "horarioFin": horarioFin,
#                           "avatar": avatar, "listaDeProductos": listaDeProductos, "activo": activo,
#                           "formasDePago": formasDePago, "favoritos": favoritos}
#         elif (tipo == 3):
#             url = 'main/vendedor-ambulante.html'
#             argumentos = {"nombre": nombre, "tipo": tipo, "id": id, "avatar": avatar,
#                           "listaDeProductos": listaDeProductos,
#                           "activo": activo, "formasDePago": formasDePago, "favoritos": favoritos}
#         print("chao")
#         return render(request, url, argumentos)
#
# #vista de inicio para alumnos que iniciaron sesion
# #carga la lista de vendedores para mostrar
# def inicioAlumno(request):
#     id = request.session['id']
#     #crear lista de vendedores a mostrar
#     vendedores =[]
#     for p in Usuario.objects.raw('SELECT * FROM usuario'):
#         if p.id == id:
#             avatar = p.avatar
#         if p.tipo == 2 or p.tipo == 3:
#             vendedores.append(p.id)
#     vendedoresJson = simplejson.dumps(vendedores)
#     return render(request, 'main/baseAlumno.html',{"id": id,"vendedores": vendedoresJson,"avatarSesion": avatar, "nombresesion": request.session['nombre']})
#
# #vista que elimina un producto por medio de ajax
# #recibe el nombre del producto por medio de GET
# @csrf_exempt
# def borrarProducto(request):
#     if request.method == 'GET':
#         if request.is_ajax():
#             comida = request.GET.get('eliminar')
#             Comida.objects.filter(nombre=comida).delete()
#             data = {"eliminar" : comida}
#             return JsonResponse(data)
#
#
# #vista que modifica un producto por medio de ajax
# #recibe los parametros del producto por medio de POST
# @csrf_exempt
# def editarProducto(request):
#     if request.method == 'POST':
#         if request.is_ajax():
#             form = editarProductosForm(data=request.POST, files=request.FILES)
#             print(request.POST)
#             print(request.FILES)
#             nombreOriginal = request.POST.get("nombreOriginal")
#             nuevoNombre = request.POST.get('nombre')
#             nuevoPrecio = (request.POST.get('precio'))
#             nuevoStock = (request.POST.get('stock'))
#             nuevaDescripcion = request.POST.get('descripcion')
#             nuevaCategoria = (request.POST.get('categoria'))
#             nuevaImagen = request.FILES.get("comida")
#             if nuevoPrecio != "" :
#                    Comida.objects.filter(nombre=nombreOriginal).update(precio=int(nuevoPrecio))
#             if nuevoStock != "" :
#                    Comida.objects.filter(nombre=nombreOriginal).update(stock=int(nuevoStock))
#             if nuevaDescripcion != "":
#                    Comida.objects.filter(nombre=nombreOriginal).update(descripcion=nuevaDescripcion)
#             if  nuevaCategoria != None:
#                    Comida.objects.filter(nombre=nombreOriginal).update(categorias=(nuevaCategoria))
#             if nuevaImagen != None:
#                 filename = nombreOriginal + ".jpg"
#                 with default_storage.open('../media/productos/' + filename, 'wb+') as destination:
#                     for chunk in nuevaImagen.chunks():
#                         destination.write(chunk)
#                 Comida.objects.filter(nombre =nombreOriginal).update(imagen='/productos/'+filename)
#
#             if nuevoNombre != "":
#                 if Comida.objects.filter(nombre=nuevoNombre).exists():
#                     data = {"respuesta": "repetido"}
#                     return JsonResponse(data)
#                 else:
#                     Comida.objects.filter(nombre=nombreOriginal).update(nombre=nuevoNombre)
#
#             data = {"respuesta" : nombreOriginal}
#             return JsonResponse(data)
#
# #vista para usar con ajax
# #recibe el id del vendedor y si es que se debe agregar a favorito o eliminar por medio de GET
# #modifica la tabla favorito para el usuario que tenga iniciada sesion

# def cambiarEstado(request):
#     if request.method == 'GET':
#         if request.is_ajax():
#             estado = request.GET.get('estado')
#             id_vendedor = request.GET.get('id')
#             if estado == "true":
#                 Usuario.objects.filter(id=id_vendedor).update(activo=True)
#             else:
#                 Usuario.objects.filter(id=id_vendedor).update(activo=False)
#             data = {"estado": estado}
#             return JsonResponse(data)
#
#
#
# @csrf_exempt
# def borrarUsuario(request):
#     if request.method == 'GET':
#         if request.is_ajax():
#             uID = request.GET.get('eliminar')
#             Usuario.objects.filter(id=uID).delete()
#             data = {"eliminar" : uID}
#             return JsonResponse(data)
#
# @csrf_exempt
# def agregarAvatar(request):
#     if request.is_ajax() or request.method == 'FILES':
#         imagen = request.FILES.get("image")
#         print(request.FILES)
#         nuevaImagen = Imagen(imagen=imagen)
#         nuevaImagen.save()
#         return HttpResponse("Success")
#
#
# def editarUsuarioAdmin(request):
#     if request.method == 'GET':
#             nombre = request.GET.get("name")
#             contraseña = request.GET.get('password')
#             email = request.GET.get('email')
#             avatar = request.GET.get('avatar')
#             userID = request.GET.get('userID')
#
#             if  (nombre!=None):
#                 print ("nombre:"+nombre)
#             if (contraseña != None):
#                 print ("contraseña:"+contraseña)
#             if (email != None):
#                 print ("email:"+email)
#             if (avatar != None):
#                 print ("avatar:"+avatar)
#             if (userID != None):
#                 print("id:"+userID)
#             if email != None:
#                 Usuario.objects.filter(id=userID).update(email=email)
#                 print("cambio Mail")
#             if nombre != None:
#                 Usuario.objects.filter(id=userID).update(nombre=nombre)
#                 print("cambio Nombre")
#             if contraseña != None:
#                 Usuario.objects.filter(id=userID).update(contraseña=contraseña)
#                 print("cambio contraseña")
#             if avatar != None:
#                 Usuario.objects.filter(id=userID).update(avatar=avatar)
#                 print("cambio avatar")
#
#             data = {"respuesta": userID}
#             return JsonResponse(data)
#
#
# def editarUsuario(request):
#     if request.method == 'GET':
#
#             nombre = request.GET.get("name")
#             contraseña = request.GET.get('password')
#             tipo = request.GET.get('type')
#             email = request.GET.get('email')
#             avatar = request.GET.get('avatar')
#             forma0 = request.GET.get('forma0')
#             forma1 = request.GET.get('forma1')
#             forma2 = request.GET.get('forma2')
#             forma3 = request.GET.get('forma3')
#             horaIni = request.GET.get('horaIni')
#             horaFin = request.GET.get('horaFin')
#             userID = request.GET.get('userID')
#
#             nuevaListaFormasDePago = ""
#             if(nombre!=None):
#                 print ("nombre:"+nombre)
#             if (contraseña != None):
#                 print ("contraseña:"+contraseña)
#             if (tipo != None):
#                 print ("tipo:"+tipo)
#             if (email != None):
#                 print ("email:"+email)
#             if (avatar != None):
#                 print ("avatar:"+avatar)
#             if (horaIni != None):
#                 print("horaIni:"+horaIni)
#             if (horaFin != None):
#                 print("horaFin:" + horaFin)
#             if (userID != None):
#                 print("id:"+userID)
#             if (forma0 != None):
#                 print("forma0:" + forma0)
#                 nuevaListaFormasDePago+="0"
#             if (forma1 != None):
#                 print("forma1:" + forma1)
#                 if(len(nuevaListaFormasDePago)!=0):
#                     nuevaListaFormasDePago += ",1"
#                 else:
#                     nuevaListaFormasDePago += "1"
#             if (forma2 != None):
#                 print("forma2:" + forma2)
#                 if (len(nuevaListaFormasDePago) != 0):
#                     nuevaListaFormasDePago += ",2"
#                 else:
#                     nuevaListaFormasDePago += "2"
#             if (forma3 != None):
#                 print("forma3:" + forma3)
#                 if (len(nuevaListaFormasDePago) != 0):
#                     nuevaListaFormasDePago += ",3"
#                 else:
#                     nuevaListaFormasDePago += "3"
#
#
#             litaFormasDePago = (
#                 (0, 'Efectivo'),
#                 (1, 'Tarjeta de Crédito'),
#                 (2, 'Tarjeta de Débito'),
#                 (3, 'Tarjeta Junaeb'),
#             )
#             if email != None:
#                 Usuario.objects.filter(id=userID).update(email=email)
#                 print("cambio Mail")
#             if nombre != None:
#                 Usuario.objects.filter(id=userID).update(nombre=nombre)
#                 print("cambio Nombre")
#             if contraseña != None:
#                 Usuario.objects.filter(id=userID).update(contraseña=contraseña)
#                 print("cambio contraseña")
#             if tipo != None:
#                 Usuario.objects.filter(id=userID).update(tipo=tipo)
#                 print("cambio tipo")
#             if avatar != None:
#                 Usuario.objects.filter(id=userID).update(avatar=avatar)
#                 print("cambio avatar")
#             if horaIni != None:
#                 Usuario.objects.filter(id=userID).update(horarioIni=horaIni)
#                 print("cambio hora ini")
#             if horaFin != None:
#                 Usuario.objects.filter(id=userID).update(horarioFin=horaFin)
#                 print("cambio hora fin")
#             Usuario.objects.filter(id=userID).update(formasDePago=nuevaListaFormasDePago)
#             print("cambio formas de pago")
#
#             data = {"respuesta" : userID}
#             return JsonResponse(data)
#
# def registerAdmin(request):
#     tipo = request.POST.get("tipo")
#     nombre = request.POST.get("nombre")
#     email = request.POST.get("email")
#     password = request.POST.get("password")
#     horaInicial = request.POST.get("horaIni")
#     horaFinal = request.POST.get("horaFin")
#     avatar = request.FILES.get("avatar")
#     #print(avatar)
#     formasDePago = []
#     if not (request.POST.get("formaDePago0") is None):
#         formasDePago.append(request.POST.get("formaDePago0"))
#     if not (request.POST.get("formaDePago1") is None):
#         formasDePago.append(request.POST.get("formaDePago1"))
#     if not (request.POST.get("formaDePago2") is None):
#         formasDePago.append(request.POST.get("formaDePago2"))
#     if not (request.POST.get("formaDePago3") is None):
#         formasDePago.append(request.POST.get("formaDePago3"))
#     usuarioNuevo = Usuario(nombre=nombre, email=email, tipo=tipo, contraseña=password, avatar=avatar,
#                                formasDePago=formasDePago, horarioIni=horaInicial, horarioFin=horaFinal)
#     usuarioNuevo.save()
#     id = request.session['id']
#     email = request.session['email']
#     avatar = request.session['avatar']
#     nombre = request.session['nombre']
#     contraseña = request.session['contraseña']
#     print(id)
#     print(email)
#     print(avatar)
#     print(nombre)
#     return adminPOST(id,avatar,email,nombre,contraseña,request)
#
# @csrf_exempt
# def verificarEmail(request):
#     if request.is_ajax() or request.method == 'POST':
#         email = request.POST.get("email")
#         print(email)
#         if Usuario.objects.filter(email=email).exists():
#             data = {"respuesta": "repetido"}
#             return JsonResponse(data)
#         else:
#             data = {"respuesta": "disponible"}
#             return JsonResponse(data)
#

#
def createTransaction(request):
    print("GET:")
    print(request.GET)
    nombreProducto = request.GET.get("nombre")
    precio=0
    idVendedor = request.GET.get("idUsuario")
    vendedor =  Vendedor.objects.get(id=idVendedor)


    if Comida.objects.filter(nombre=nombreProducto).exists():
        comida = Comida.objects.get(nombre=nombreProducto)
        precio = Comida.objects.filter(nombre=nombreProducto).values('precio')[0]
        listaAux=list(precio.values())
        precio=listaAux[0]
        print(precio)
    else:
        return HttpResponse('error message')
    print(nombreProducto)
    transaccionNueva = Transacciones(idVendedor=vendedor,precio=precio)
    transaccionNueva.save()
    transaccionNueva.comida.add(comida)
    return JsonResponse({"transaccion": "realizada"})


@csrf_exempt
def checkAlert(request):
    #print("POST:")
    #print(request.POST)
    #print("meemboyz")
    idUsuario = request.POST.get("id")
    usuario = Usuario.objects.get(id=idUsuario)
    #print(usuario)
    try:
        alerta = alertaPolicial.objects.get(usuario=usuario)
    except alertaPolicial.DoesNotExist:
        return JsonResponse({"alertar": "false"})

    alerta.delete()
    return JsonResponse({"alertar": "true"})







@csrf_exempt
def createAlert(request):
    #print("POST:")
    #print(request.POST)
    #print("meemboyz")
    idUsuario = request.POST.get("alertId")
    usuario = Usuario.objects.get(id=idUsuario)
    #nuevaAlertaPolicialUsuario = alertaPolicial(usuario=usuario)
    #nuevaAlertaPolicialUsuario.save()
    #print(usuario.longitud)
    #print(usuario.latitud)
    longitud = usuario.longitud
    latitud = usuario.latitud
    usuariosTodos = Usuario.objects.all()

    #print(usuariosTodos)
    for u in usuariosTodos:
        if haversine(u.longitud,u.latitud,longitud,latitud):
            usuarioAlertar = Usuario.objects.get(id=u.id)
            print(usuarioAlertar)
            nuevaAlertaPolicial = alertaPolicial(usuario=usuarioAlertar)
            nuevaAlertaPolicial.save()
    return HttpResponse(status=204)
