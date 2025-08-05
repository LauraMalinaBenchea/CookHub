import os

from rest_framework import serializers

from .models import Answer, Question, Quiz, UploadedFile


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "answer_text", "correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "answers"]

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
        print("Created quiz with questions:", quiz.pk)

        for question_data in questions_data:
            answers_data = question_data.pop("answers")
            question = Question.objects.create(quiz=quiz, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return quiz

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions")

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get(
            "description", instance.description
        )
        instance.save()

        # Track existing question IDs for comparison
        existing_question_ids = [q.id for q in instance.questions.all()]

        # Extract IDs of questions sent from
        # client (may be missing for new ones)
        sent_question_ids = [
            q.get("id") for q in questions_data if q.get("id") is not None
        ]

        # Delete questions that were removed by the client
        for question_id in existing_question_ids:
            if question_id not in sent_question_ids:
                Question.objects.filter(id=question_id).delete()

        for question_data in questions_data:
            answers_data = question_data.pop("answers")
            question_id = question_data.get("id", None)

            if question_id:
                # Update existing question
                question = Question.objects.get(id=question_id, quiz=instance)
                question.question_text = question_data.get(
                    "question_text", question.question_text
                )
                question.save()
            else:
                # Create new question
                question = Question.objects.create(
                    quiz=instance, **question_data
                )

            # Now update answers for this question

            existing_answer_ids = [a.id for a in question.answers.all()]
            sent_answer_ids = [
                a.get("id") for a in answers_data if a.get("id") is not None
            ]

            # Delete answers removed by the client
            for answer_id in existing_answer_ids:
                if answer_id not in sent_answer_ids:
                    Answer.objects.filter(id=answer_id).delete()

            for answer_data in answers_data:
                answer_id = answer_data.get("id", None)
                if answer_id:
                    # Update existing answer
                    answer = Answer.objects.get(
                        id=answer_id, question=question
                    )
                    answer.answer_text = answer_data.get(
                        "answer_text", answer.answer_text
                    )
                    answer.correct = answer_data.get("correct", answer.correct)
                    answer.save()
                else:
                    # Create new answer
                    Answer.objects.create(question=question, **answer_data)

        return instance


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
        print("In validate file")
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
