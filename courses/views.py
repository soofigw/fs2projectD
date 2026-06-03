from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, Http404
import json
from django.db.models import F

from .models import Course, Lesson, Enrollment, LessonProgress, Category, Lesson
from .forms import CourseForm, LessonForm

# ==============================================================================
# VISTAS DE CURSOS (CRUD COMPLETO)
# ==============================================================================

class CourseListView(ListView):
    """Muestra el catálogo de cursos disponibles (Punto 5 de la rúbrica)"""
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        # Permite buscar cursos por título y filtrar por categoría o nivel
        queryset = Course.objects.filter(is_listed=True)
        query = self.request.GET.get("q")
        category_slug = self.request.GET.get("category")
        level = self.request.GET.get("level")

        if query:
            queryset = queryset.filter(title__icontains=query)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if level:
            queryset = queryset.filter(level=level)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class CourseDetailView(DetailView):
    """Muestra la estructura interna de un curso e identifica si el alumno está inscrito"""
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user


        is_instructor = (
            user.is_authenticated and
            course.instructor == user
        )
        is_enrolled = False
        progress_pct = 0

        if user.is_authenticated and not is_instructor:
            is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
            if is_enrolled:
                # Calcula el porcentaje matemático de progreso del alumno
                total_lessons = course.lessons.count()
                if total_lessons > 0:
                    completed_lessons = LessonProgress.objects.filter(
                        user=user, lesson__course=course, completed=True
                    ).count()
                    progress_pct = int((completed_lessons / total_lessons) * 100)

        context["is_enrolled"] = is_enrolled
        context["progress_percentage"] = progress_pct
        context["lessons"] = course.lessons.all()
        context["is_instructor"] = is_instructor
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """Permite a los instructores crear nuevos cursos (CRUD - Crear)"""
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, "¡Curso creado exitosamente!")
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Permite modificar los datos del curso (CRUD - Editar)"""
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"

    def test_func(self):
        # Valida que solo el dueño del curso pueda editarlo (Permisos por Rol)
        return self.get_object().instructor == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "¡Curso actualizado con éxito!")
        return super().form_valid(form)

class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Permite eliminar un curso (CRUD - Eliminar)"""
    model = Course
    template_name = "courses/course_confirm_delete.html"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"
    success_url = reverse_lazy("courses:course_list")

    def test_func(self):
        # Solo el instructor dueño del curso puede eliminarlo
        return self.get_object().instructor == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "¡Curso eliminado correctamente!")
        return super().delete(request, *args, **kwargs)

# ==============================================================================
# SISTEMA DE INSCRIPCIÓN AUTOMÁTICA
# ==============================================================================

class EnrollCourseView(LoginRequiredMixin, View):
    """Inscribe al usuario logueado en el curso actual y genera sus filas de progreso"""
    def post(self, request, identifier):
        course = get_object_or_404(Course, identifier=identifier)
        
        # Uso de transacción atómica para proteger la integridad de la BD (Criterio de Linus)
        with transaction.atomic():
            enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
            
            if created:
                # Inicializa el progreso en falso para cada lección del curso
                lessons = course.lessons.all()
                for lesson in lessons:
                    LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
                messages.success(request, f"Te has inscrito con éxito al curso: {course.title}")
            else:
                messages.info(request, "Ya te encuentras inscrito en este curso.")
                
        return redirect(course.get_absolute_url())


# ==============================================================================
# VISUALIZACIÓN DE LECCIONES Y CONTROL DE AVANCE
# ==============================================================================

class LessonDetailView(LoginRequiredMixin, DetailView):
    """Muestra el contenido multimedia de la lección e interactúa con el progreso"""
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_object(self, queryset=None):
        # Busca la lección combinando el identificador del curso y el orden asignado
        course_id = self.kwargs.get("course_id")
        order = self.kwargs.get("order")
        return get_object_or_404(Lesson, course__identifier=course_id, order=order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        user = self.request.user

        # Verifica si el alumno realmente está inscrito para dejarlo ver el contenido
        is_enrolled = Enrollment.objects.filter(user=user, course=lesson.course).exists()
        if not is_enrolled and lesson.course.instructor != user:
            raise Http404("No tienes acceso a esta lección porque no estás inscrito en el curso.")

        # Obtiene o inicializa la fila de seguimiento de progreso de esta lección
        progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)

        # Sistema de paginación para los botones "Siguiente" y "Anterior"
        next_lesson = Lesson.objects.filter(course=lesson.course, order__gt=lesson.order).first()
        prev_lesson = Lesson.objects.filter(course=lesson.course, order__lt=lesson.order).last()

        context["progress"] = progress
        context["next_lesson"] = next_lesson
        context["prev_lesson"] = prev_lesson
        return context


class ToggleLessonCompleteView(LoginRequiredMixin, View):
    """Marca una lección como completada o pendiente y actualiza la fecha de progreso"""
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        progress = get_object_or_404(LessonProgress, user=request.user, lesson=lesson)
        
        if progress.completed:
            progress.completed = False
            progress.completed_at = None
        else:
            progress.mark_completed()
        
        progress.save()
        
        # Redirecciona a la misma lección actual para refrescar el estado visual
        return redirect(reverse("courses:lesson_detail", kwargs={
            "course_id": lesson.course.identifier,
            "order": lesson.order
        }))
    
class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    fields = [
        "title",
        "content_type",
        "text_content",
        "video_url",
        "attachment"
    ]

    template_name = "courses/lesson_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields:
            form.fields[field].widget.attrs.update({
                "class": "form-control"
            })

        return form

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course,
            identifier=self.kwargs["identifier"]
        )

        if self.course.instructor != request.user:
            return redirect("courses:course_detail",
                            identifier=self.course.identifier)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course

        ultimo_orden = (
            Lesson.objects.filter(course=self.course)
            .count()
        )

        form.instance.order = ultimo_orden + 1

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "courses:course_detail",
            kwargs={"identifier": self.course.identifier}
        )
    
class LessonUpdateView(LoginRequiredMixin, UpdateView):

    model = Lesson

    fields = [
        "title",
        "content_type",
        "text_content",
        "video_url",
        "attachment"
    ]

    template_name = "courses/lesson_form.html"

    def get_form(self, form_class=None):

        form = super().get_form(form_class)

        for field in form.fields:
            form.fields[field].widget.attrs.update({
                "class": "form-control"
            })

        return form

    def dispatch(self, request, *args, **kwargs):

        lesson = self.get_object()

        if lesson.course.instructor != request.user:
            return redirect(
                "courses:course_detail",
                identifier=lesson.course.identifier
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):

        return reverse(
            "courses:course_detail",
            kwargs={
                "identifier": self.object.course.identifier
            }
        )


class LessonDeleteView(LoginRequiredMixin, DeleteView):

    model = Lesson

    template_name = "courses/lesson_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):

        lesson = self.get_object()

        if lesson.course.instructor != request.user:
            return redirect(
                "courses:course_detail",
                identifier=lesson.course.identifier
            )

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):

        lesson = self.get_object()

        course = lesson.course
        deleted_order = lesson.order

        response = super().delete(request, *args, **kwargs)

        Lesson.objects.filter(
            course=course,
            order__gt=deleted_order
        ).update(order=F("order") - 1)

        return response

    def get_success_url(self):

        return reverse(
            "courses:course_detail",
            kwargs={
                "identifier": self.object.course.identifier
            }
        )