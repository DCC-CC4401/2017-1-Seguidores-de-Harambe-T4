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

        return index(request)

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
    #la alerta existe, se procede a verificar la hora y fecha
    fechaAhora = str(timezone.now()).split(' ', 1)[0]
    horaAhora = str(timezone.now()).split(' ', 1)[1].split('.')[0].split(':')[0] + ':' + \
                str(timezone.now()).split(' ', 1)[1].split('.')[0].split(':')[1]
    print("defirencia de hora: " + str((abs(int(alerta.hora.split(':')[1])) - (int(horaAhora.split(':')[1])))))
    if(alerta.fecha != fechaAhora or alerta.hora.split(':')[0] != horaAhora.split(':')[0]
       or (abs(int(alerta.hora.split(':')[1])) - (int(horaAhora.split(':')[1]))) >=5):
        alerta.delete()
        return JsonResponse({"alertar": "false"})
    alerta.delete()
    return JsonResponse({"alertar": "true"})







@csrf_exempt
def createAlert(request):
    idUsuario = request.POST.get("alertId")
    usuario = Usuario.objects.get(id=idUsuario)
    try:
        alertaUsuarioAlertor = alertaPolicial.objects.get(usuario=usuario)
    except alertaPolicial.DoesNotExist:
        print(usuario)
        nuevaAlertaPolicialUsuario = alertaPolicial(usuario=usuario)
        nuevaAlertaPolicialUsuario.save()
    longitud = usuario.longitud
    latitud = usuario.latitud
    usuariosTodos = Usuario.objects.all()


    for u in usuariosTodos:
        if haversine(u.longitud,u.latitud,longitud,latitud):
            usuarioAlertar = Usuario.objects.get(id=u.id)
            print(usuarioAlertar)
            try:
                #veo si ya existe una alerta epndiente para ese usaurio
                alerta = alertaPolicial.objects.get(usuario=usuarioAlertar)
            except alertaPolicial.DoesNotExist:
                # si no existe creo nomas
                nuevaAlertaPolicial = alertaPolicial(usuario=usuarioAlertar)
                nuevaAlertaPolicial.save()
                return HttpResponse(status=204)
            #si ya existia la borro
            alerta.delete()
            nuevaAlertaPolicial = alertaPolicial(usuario=usuarioAlertar)
            nuevaAlertaPolicial.save()
            return HttpResponse(status=204)


