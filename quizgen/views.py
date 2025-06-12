import os

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import QuestionFormSet, QuizzForm, UploadedFileForm
from .models import Quizz
from .serializers import QuizzSerializer
from .utils import extract_text_from_file


class FileUploadView(FormView):
    template_name = "quizgen/upload.html"
    form_class = UploadedFileForm
    success_url = reverse_lazy("upload_file")

    def form_valid(self, form):
        uploaded_file = form.save()
        file_path = uploaded_file.file.path
        file_type = os.path.splitext(file_path)[1].lower()
        file_type.lstrip(".") if file_type in [".pdf", ".docx"] else "unknown"

        try:
            extracted_text = extract_text_from_file(file_path, file_type)
            print("Extracted Text:\n", extracted_text[:1000])  # For debugging
        except Exception as e:
            print(f"Error extracting text: {e}")

        return super().form_valid(form)


class QuizzWithQuestionsCreateView(View):
    def get(self, request):
        quizz_form = QuizzForm()
        question_formset = QuestionFormSet()
        return render(
            request,
            "quizgen/quizz_with_questions.html",
            {"form": quizz_form, "formset": question_formset},
        )

    def post(self, request):
        quizz_form = QuizzForm(request.POST)
        question_formset = QuestionFormSet(request.POST)

        if quizz_form.is_valid() and question_formset.is_valid():
            quizz = quizz_form.save()
            questions = question_formset.save(commit=False)
            for question in questions:
                question.quizz = quizz
                question.save()
            return redirect("quizz_list")

        return render(
            request,
            "quizgen/quizz_with_questions.html",
            {"quizz_form": quizz_form, "question_formset": question_formset},
        )


class QuizzListView(APIView):

    serializer_class = QuizzSerializer

    def get(self, request):
        detail = [
            {"title": quizz.title, "description": quizz.description}
            for quizz in Quizz.objects.all()
        ]
        return Response(detail)

    def post(self, request):
        serializer = QuizzSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
