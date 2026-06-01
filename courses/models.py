import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings

# Helper para obtener el almacenamiento dinamico (Local o OCI Cloud)
def get_file_storage():
    if hasattr(settings, 'DEFAULT_FILE_STORAGE') and settings.DEFAULT_FILE_STORAGE:
        from django.utils.module_loading import import_string
        storage_class = import_string(settings.DEFAULT_FILE_STORAGE)
        return storage_class()
    return default_storage


# ==============================================================================
# 1. MODELO DE USUARIO PERSONALIZADO 
# ==============================================================================
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


# ==============================================================================
# 2. MODELO DE CATEGORIA 
# ==============================================================================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ==============================================================================
# 3. MODELO DE CURSO 
# ==============================================================================
class Course(models.Model):
    LEVEL_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="courses_taught"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name="courses"
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    duration = models.PositiveIntegerField(help_text="Duración aproximada en horas")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='principiante')
    video_url = models.URLField(blank=True, help_text="URL de video introductorio (YouTube/Vimeo)")
    
    is_listed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("courses:course_detail", kwargs={"identifier": self.identifier})


# ==============================================================================
# 4. MODELO DE LECCION (Estructura de contenido)
# ==============================================================================
class Lesson(models.Model):
    CONTENT_TYPES = [
        ("video", "Video"),
        ("text", "Texto"),
        ("image", "Imagen"),
        ("file", "Archivo Descargable"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    
    text_content = models.TextField(blank=True)
    video_url = models.URLField(blank=True, help_text="URL de video externo si aplica")
    
    attachment = models.FileField(
        upload_to="lessons/%Y/%m/%d/",
        storage=get_file_storage,
        blank=True,
        null=True,
        help_text="Sube archivos multimedia o documentos"
    )
    
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("course", "order")
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ==============================================================================
# 5. MODELO DE INSCRIPCION (R Muchos a Muchos Alumno-Curso)
# ==============================================================================
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ("-enrolled_at",)

    def __str__(self):
        return f"{self.user.email} inscrito en {self.course.title}"


# ==============================================================================
# 6. MODELO DE SEGUIMIENTO DE PROGRESO
# ==============================================================================
class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_position_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "lesson")
        ordering = ("lesson",)

    def mark_completed(self):
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"