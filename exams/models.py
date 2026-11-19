from django.db import models


class Exam(models.Model):
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE)
    term = models.ForeignKey("academics.Term", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20)

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.school_class})"


class Grade(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="grades")
    student = models.ForeignKey("people.Student", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_absent = models.BooleanField(default=False)

    class Meta:
        unique_together = ("exam", "student")

    def __str__(self):
        return f"{self.student}: {self.score}"