from django.conf.urls import url
from main import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login.as_view(),name='login'),
    url(r'^signup/$', views.signup.as_view(),name='signup'),
    url(r'^editarUsuario/$', views.editarUsuario.as_view(), name='editarUsuario'),
    url(r'^loginReq/',views.loginReq, name = 'loginReq'),
    url(r'^logout/', views.logOut, name='logout'),
    url(r'^inicio/', views.inicio, name='inicio'),
    url(r'^verificarEmail/$', views.verificarEmail, name='verificarEmail'),
    url(r'^agregarproductos/$', views.agregarproductos.as_view(),name='agregarproductos'),
    url(r'^editarproductos/$', views.editarproductos.as_view(),name='editarproductos'),
    # url(r'^vendedorprofilepage/$', views.vendedorprofilepage,name='vendedorprofilepage'),
    # url(r'^formView/', views.formView, name='formView'),
    # url(r'^register/', views.register, name='register'),
    # url(r'^loggedin/', views.loggedin, name='loggedin'),
    # url(r'^productoReq/', views.productoReq, name='productoReq'),
    # url(r'^vistaVendedorPorAlumno/', views.vistaVendedorPorAlumno, name='vistaVendedorPorAlumno'),
    url(r'^cambiarEstado/$', views.cambiarEstado,name='cambiarEstado'),
    # url(r'^editarVendedor/$', views.editarVendedor,name='editarVendedor'),
    # url(r'^editarDatos/$', views.editarDatos,name='editarDatos'),
    # url(r'^inicioAlumno/', views.inicioAlumno, name='inicioAlumno'),
    # url(r'^borrarUsuario/', views.borrarUsuario, name='borrarUsuario'),
     url(r'^borrarProducto/', views.borrarProducto, name='borrarProducto'),
    # url(r'^editarProducto/', views.editarProducto, name='editarProducto'),
    # url(r'^cambiarFavorito/', views.cambiarFavorito, name='cambiarFavorito'),
    # url(r'^vistaVendedorPorAlumnoSinLogin/', views.vistaVendedorPorAlumnoSinLogin, name='vistaVendedorPorAlumnoSinLogin'),
    # url(r'^editarPerfilAlumno/', views.editarPerfilAlumno,name='editarPerfilAlumno'),
    # url(r'^procesarPerfilAlumno/', views.procesarPerfilAlumno,name='procesarPerfilAlumno'),
    # url(r'^editarUsuario/', views.editarUsuario, name='editarUsuario'),
    # url(r'^agregarAvatar/', views.agregarAvatar, name='agregarAvatar'),
    # url(r'^signupAdmin/$', views.signupAdmin,name='signupAdmin'),
    # url(r'^registerAdmin/$', views.registerAdmin,name='registerAdmin'),
    # url(r'^getStock/$', views.getStock,name='getStock'),
    # url(r'^verificarEmail/$', views.verificarEmail,name='verificarEmail'),
    # url(r'^adminEdit/$', views.adminEdit,name='adminEdit'),
    # url(r'^editarUsuarioAdmin/$', views.editarUsuarioAdmin,name='editarUsuarioAdmin'),
    # url(r'^loginAdmin/$', views.loginAdmin, name='loginAdmin'),
    # url(r'^createTransaction/$', views.createTransaction, name='createTransaction'),
    # url(r'^fijoDashboard/$', views.fijoDashboard, name='fijoDashboard'),
    # url(r'^ambulanteDashboard/$', views.ambulanteDashboard, name='ambulanteDashboard'),


]
