from django.urls import path

from .views import FileUploadView, QuizDetailUpdateDeleteView, QuizListView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="upload_file"),
    path("quiz_list/", QuizListView.as_view(), name="quiz_list"),
    path(
        "quiz_detail/<int:pk>/",
        QuizDetailUpdateDeleteView.as_view(),
        name="quiz_detail",
    ),
]
