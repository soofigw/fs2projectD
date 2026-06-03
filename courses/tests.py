from django.test import TestCase
from django.urls import reverse

from .models import (
    CustomUser,
    Category,
    Course,
    Lesson,
    Enrollment
)


class CourseTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="sofia",
            email="sofia@test.com",
            password="12345678"
        )

        self.category = Category.objects.create(
            name="Programacion",
            slug="programacion"
        )

        self.course = Course.objects.create(
            instructor=self.user,
            category=self.category,
            title="Python desde Cero",
            description="Curso de prueba",
            duration=10,
            level="principiante"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "sofia@test.com")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Programacion")

    def test_course_creation(self):
        self.assertEqual(self.course.title, "Python desde Cero")

    def test_course_str(self):
        self.assertEqual(str(self.course), "Python desde Cero")

    def test_course_detail_view(self):
        response = self.client.get(
            reverse(
                "courses:course_detail",
                kwargs={"identifier": self.course.identifier}
            )
        )
        self.assertEqual(response.status_code, 200)