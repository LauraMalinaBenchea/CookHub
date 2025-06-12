from django.urls import path

from .views import FileUploadView, QuizzListView, QuizzWithQuestionsCreateView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="upload_file"),
    path(
        "new_quizz/", QuizzWithQuestionsCreateView.as_view(), name="new_quizz"
    ),
    path("quizz_list/", QuizzListView.as_view(), name="quizz_list"),
]
