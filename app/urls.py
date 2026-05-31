from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.get_dirs() if hasattr(admin.site, 'get_dirs') else admin.site.urls),
    # Conectamos las URLs de tu app courses como la página de inicio global
    path('', include('courses.urls', namespace='courses')),
]

# Servir archivos multimedia en desarrollo (Imágenes subidas de lecciones)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)