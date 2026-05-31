from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Course, Lesson, Enrollment, LessonProgress

# Registramos tu CustomUser usando la estructura de herencia nativa
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "is_staff", "is_active")
    ordering = ("email",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)} # Autocompila el slug mientras escribes el nombre

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "instructor", "level", "duration", "is_listed")
    list_filter = ("level", "category", "is_listed")
    search_fields = ("title", "description")

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "content_type", "order")
    list_filter = ("content_type", "course")
    ordering = ("course", "order")

admin.site.register(Enrollment)
admin.site.register(LessonProgress)