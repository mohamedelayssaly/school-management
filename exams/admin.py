from django.contrib import admin
from .models import Exam, Grade

admin.site.register([Exam, Grade])