from django.urls import path

from .views import FileUploadView, QuizzDetailUpdateDeleteView, QuizzListView

urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="upload_file"),
    path(
        "new_quizz/<pk>",
        QuizzDetailUpdateDeleteView.as_view(),
        name="quizz_detail",
    ),
    path("quizz_list/", QuizzListView.as_view(), name="quizz_list"),
    path(
        "quizz_detail/<int:pk>/",
        QuizzDetailUpdateDeleteView.as_view(),
        name="quizz_detail",
    ),
]
