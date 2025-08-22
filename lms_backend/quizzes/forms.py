from django import forms
from .models import Grade, Question

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('score',)

class QuizAttemptForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz_lecture = kwargs.pop('quiz_lecture')
        super().__init__(*args, **kwargs)
        self.fields['quiz_lecture_id'] = forms.IntegerField(widget=forms.HiddenInput(), initial=quiz_lecture.pk)

        for i, question in enumerate(quiz_lecture.questions.all()):
            choices = [(str(j), option) for j, option in enumerate(question.options)]
            self.fields[f'question_{question.pk}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )
