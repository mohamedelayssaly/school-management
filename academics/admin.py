from django.contrib import admin
from .models import AcademicYear, Term, Level, SchoolClass, Subject

admin.site.register([AcademicYear, Term, Level, SchoolClass, Subject])