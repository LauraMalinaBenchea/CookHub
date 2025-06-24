import os

from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from rest_framework import generics, status
from rest_framework.response import Response

from .forms import UploadedFileForm
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


class QuizzListView(generics.ListCreateAPIView):
    serializer_class = QuizzSerializer
    queryset = Quizz.objects.all()

    def get(self, request):
        quizzes = Quizz.objects.all()
        serializer = QuizzSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizzSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizzDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quizz.objects.all()
    serializer_class = QuizzSerializer
