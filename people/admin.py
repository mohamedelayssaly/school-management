from django.contrib import admin

from .models import Employee, Enrollment, Parent, Student, TeachingAssignment

admin.site.register([Student, Employee, Enrollment, TeachingAssignment])


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    filter_horizontal = ('children',)