from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Course, Lesson

class StyledFormMixin:
    """Inyecta automáticamente las clases de Bootstrap 5 a todos los inputs"""
    def _style_fields(self):
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                
            field.widget.attrs.setdefault("placeholder", field.label or "")

# Formulario para Cursos (Con los campos de tu Opción D: duración y nivel)
class CourseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "category", "description", "duration", "level", "video_url", "is_listed"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

# Formulario para Lecciones
class LessonForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content_type", "text_content", "video_url", "attachment"]
        widgets = {
            "text_content": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

# Formulario de Registro (CustomUser)
class SignupForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

# Formulario de Login adaptado a Bootstrap 5
class EmailLoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Correo electrónico"
        self._style_fields()