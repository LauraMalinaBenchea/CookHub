from quizzgen.models import Quizz
from rest_framework import serializers


class QuizzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizz
        fields = ["title", "description"]
