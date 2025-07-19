import os

from rest_framework import serializers

from .models import Answer, Question, Quiz, UploadedFile


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


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "questions"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            answers_data = question_data.pop("answers")
            question = Question.objects.create(quiz=quiz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return quiz


class FileUploadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    file = serializers.FileField()

    class Meta:
        model = UploadedFile
        fields = ["name", "file"]
        # try:
        #     extracted_text = extract_text_from_file(file_path, file_type)
        #     print("Extracted Text:\n", extracted_text[:1000])
        # For debugging
        # except Exception as e:
        #     print(f"Error extracting text: {e}")

    def validate_file(self, file):
        allowed_extensions = [".pdf", ".docx"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError("Unsupported file extension.")
        max_size = 15 * 1024 * 1024  # 5 MB
        if file.size > max_size:
            raise serializers.ValidationError(
                "File too large. Max size is 15MB."
            )
        return file

    def validate(self, attrs):
        return attrs
