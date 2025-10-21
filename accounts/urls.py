from django.urls import path

from accounts.views import RegisterView, UserProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("user_profile/", UserProfileView.as_view(), name="user_profile"),
]
