from rest_framework import serializers

from .models import Answer, Question, Quizz


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["answer_text", "correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["question_text", "answers"]

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question


class QuizzSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quizz
        fields = ["id", "title", "description", "questions"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        quizz = Quizz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop("answers")
            question = Question.objects.create(quizz=quizz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return quizz
