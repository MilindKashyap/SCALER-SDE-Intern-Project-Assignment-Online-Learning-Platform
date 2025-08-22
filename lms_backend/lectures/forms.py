from django import forms
from lectures.models import Lecture, ReadingLecture, QuizLecture
from quizzes.models import Question

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ('title', 'type')

class ReadingLectureForm(forms.ModelForm):
    class Meta:
        model = ReadingLecture
        fields = ('content_url', 'file')

class QuestionForm(forms.ModelForm):
    options = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter options, one per line'}),
                              help_text="Enter each option on a new line.")

    class Meta:
        model = Question
        fields = ('text', 'options', 'correct_index')

    def clean_options(self):
        options_data = self.cleaned_data['options']
        # Convert newline separated options to a list
        return [opt.strip() for opt in options_data.split('\n') if opt.strip()]

class QuizLectureForm(forms.ModelForm):
    class Meta:
        model = QuizLecture
        fields = []
