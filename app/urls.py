from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from courses.forms import SignupForm, EmailLoginForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm

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

    path(
    'password-change/',
        auth_views.PasswordChangeView.as_view(
            form_class=CustomPasswordChangeForm,
            template_name='registration/password_change_form.html'
        ),
        name='password_change'
    ),

    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html'
        ),
        name='password_change_done'
    ),
    
    # path de la app de cursos
    path('', include('courses.urls', namespace='courses')),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt'
        ),
        name='password_reset'
    ),


    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=CustomSetPasswordForm,
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)