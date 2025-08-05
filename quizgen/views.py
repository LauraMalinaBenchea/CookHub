import os

from rest_framework import generics, status
from rest_framework.response import Response

from .models import Quiz
from .serializers import FileUploadSerializer, QuizSerializer
from .utils import extract_text_from_file, generate_quiz_from_text


class FileUploadView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        print("Before attempt")

        try:
            extracted_text = extract_text_from_file(uploaded_file, ext)
            quiz_data = generate_quiz_from_text(extracted_text)

            quiz_serializer = QuizSerializer(data=quiz_data)
            quiz_serializer.is_valid(raise_exception=True)
            quiz = quiz_serializer.save()
            return Response(
                {
                    "message": "File processed and quiz generated.",
                    "quiz": QuizSerializer(quiz).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )


class QuizListView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()


class QuizDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
