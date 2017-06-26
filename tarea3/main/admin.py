from django.contrib import admin

from .models import Usuario
from .models import Comida
from .models import Imagen
from .models import Transacciones
from .models import alumno
from .models import vendedorFijo
from .models import vendedorAmbulante
from .models import Admin
from .models import Vendedor
#from .models import Alert
from .models import alertaPolicial

admin.site.register(Usuario)
admin.site.register(Comida)
admin.site.register(Imagen)
admin.site.register(Transacciones)
admin.site.register(alumno)
admin.site.register(vendedorFijo)
admin.site.register(vendedorAmbulante)
admin.site.register(Admin)
admin.site.register(Vendedor)
admin.site.register(alertaPolicial)
#admin.site.register(Alert)