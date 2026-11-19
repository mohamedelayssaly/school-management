from django.db import models


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        EXCUSED = 'excused', 'Excused'

    student = models.ForeignKey('people.Student', on_delete=models.CASCADE)
    school_class = models.ForeignKey('academics.SchoolClass', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return '%s %s %s' % (self.student, self.date, self.status)