from django import forms

from .models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'term', 'date', 'max_score']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment:
            self.fields['term'].queryset = assignment.school_class.academic_year.terms.all()