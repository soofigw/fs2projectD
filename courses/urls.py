from django.urls import path
from . import views

# app_name nos sirve para hacer el tipado inverso en los templates (ej: {% url 'courses:course_list' %})
app_name = "courses"

urlpatterns = [
    # Catálogo principal y detalles de curso
    path("", views.CourseListView.as_view(), name="course_list"),
    path("course/<uuid:identifier>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("course/<uuid:identifier>/enroll/", views.EnrollCourseView.as_view(), name="enroll_course"),
    
    # CRUD de Cursos para instructores
    path("course/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("course/<uuid:identifier>/edit/", views.CourseUpdateView.as_view(), name="course_update"),
    
    # Visualización de Lecciones individuales (Estructura Udemy por Orden)
    path("course/<uuid:course_id>/lesson/<int:order>/", views.LessonDetailView.as_view(), name="lesson_detail"),
    path("lesson/<int:lesson_id>/toggle-complete/", views.ToggleLessonCompleteView.as_view(), name="toggle_complete"),
]