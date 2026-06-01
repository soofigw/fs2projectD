from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from courses.forms import SignupForm, EmailLoginForm

class CustomSignupView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "¡Tu cuenta fue creada con éxito! Ya puedes iniciar sesión.")
        return super().form_valid(form)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # auth de Usuarios
    path('login/', auth_views.LoginView.as_view(authentication_form=EmailLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='courses:course_list'), name='logout'),
    path('signup/', CustomSignupView.as_view(), name='signup'),
    
    # path de la app de cursos
    path('', include('courses.urls', namespace='courses')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)