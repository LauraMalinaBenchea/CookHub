from django import forms
from django.forms import inlineformset_factory

from .models import Answer, Question, Quizz, UploadedFile


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["file"]

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext not in ["pdf", "docx"]:
            raise forms.ValidationError(
                "Only .pdf and .docx files are supported."
            )
        return uploaded_file


class QuizzForm(forms.ModelForm):
    class Meta:
        model = Quizz
        fields = ["title", "description"]


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question_text"]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["answer_text", "correct"]


QuestionFormSet = inlineformset_factory(
    Quizz, Question, form=QuestionForm, extra=1, can_delete=True
)
AnswerFormSet = inlineformset_factory(
    Question, Answer, form=AnswerForm, extra=2, can_delete=True
)
