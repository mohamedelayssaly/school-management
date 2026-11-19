from django.db import models

# Create your models here.


class AcademicYear(models.Model):
    name=models.CharField(max_length=20)
    start_date=models.DateField()
    end_date=models.DateField()
    is_current=models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Term(models.Model):
    academic_year=models.ForeignKey(AcademicYear,on_delete=models.CASCADE, related_name="terms")
    name=models.CharField(max_length=50)
    start_date=models.DateField()
    end_date=models.DateField()


    def __str__(self):
        return f"{self.academic_year} - {self.name}"
    

class Level(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class SchoolClass(models.Model):
    level=models.ForeignKey(Level, on_delete=models.PROTECT)
    academic_year=models.ForeignKey(AcademicYear,on_delete=models.CASCADE)
    name=models.CharField(max_length=50)

    class Meta:
        verbose_name_plural="scool classes"

    def __str__ (self):
        return f"{self.name} ({self.academic_year})"
    

class Subject(models.Model):
    name=models.CharField(max_length=100)
    coefficient=models.DecimalField(max_digits=4,decimal_places=2, default=1)

    def __str__(self):
        return self.name




















