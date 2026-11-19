from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        DIRECTION = 'direction', 'Direction'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'
        PARENT = 'parent', 'Parent'

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return '%s (%s)' % (self.get_full_name() or self.username, self.role)