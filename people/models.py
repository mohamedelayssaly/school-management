from django.conf import settings
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_number} - {self.user.get_full_name() or self.user.username}"


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)  # teacher, accountant, director...
    hire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.position}"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "school_class")

    def __str__(self):
        return f"{self.student} in {self.school_class}"


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE)
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} teaches {self.subject} to {self.school_class}"


class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True)
    children = models.ManyToManyField(Student, related_name='parents', blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username











