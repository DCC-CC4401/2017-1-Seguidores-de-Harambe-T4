from django.conf.urls import url
from main import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login.as_view(),name='login'),
    url(r'^signup/$', views.signup.as_view(),name='signup'),
    url(r'^editarUsuario/$', views.editarUsuario.as_view(), name='editarUsuario'),
    url(r'^logout/', views.logOut, name='logout'),
    url(r'^inicio/', views.inicio, name='inicio'),
    url(r'^verificarEmail/$', views.verificarEmail, name='verificarEmail'),
    url(r'^agregarproductos/$', views.agregarproductos.as_view(),name='agregarproductos'),
    url(r'^editarproductos/$', views.editarproductos.as_view(),name='editarproductos'),
    url(r'^vistaVendedor/$', views.vistaVendedor.as_view(),name='vistaVendedor'),
    url(r'^cambiarEstado/$', views.cambiarEstado,name='cambiarEstado'),
    url(r'^borrarProducto/', views.borrarProducto, name='borrarProducto'),
    url(r'^cambiarFavorito/', views.cambiarFavorito, name='cambiarFavorito'),
    url(r'^modificarStock/$', views.modificarStock,name='modificarStock'),
    url(r'^createTransaction/$', views.createTransaction, name='createTransaction'),
    url(r'^vistaDashboard/$', views.Dashboard.as_view(), name='vistaDashboard'),
    url(r'^dataDashboard/$', views.dataDashboard, name='dataDashboard'),
    url(r'^checkAlert/$', views.checkAlert, name='checkAlert'),
    url(r'^createAlert/$', views.createAlert, name='createAlert'),
    url(r'^filtrarCategorias/$', views.filtrarCategorias, name='filtrarCategorias'),


]
