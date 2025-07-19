import re

import docx
import fitz
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt_tab")


def extract_text_from_file(file_obj: str, file_type: str) -> str:
    if file_type == ".pdf":
        return extract_text_from_pdf(file_obj)
    elif file_type == ".docx":
        return extract_text_from_docx(file_obj)
    else:
        return ""


def extract_text_from_pdf(file_obj: str) -> str:
    text = ""
    file_bytes = file_obj.read()
    with fitz.open(stream=file_bytes) as doc:
        for page in doc:
            text += page.get_text()
    file_obj.seek(0)
    return text


def extract_text_from_docx(file_obj: str) -> str:
    doc = docx.Document(file_obj)
    text = "\n".join([para.text for para in doc.paragraphs])
    file_obj.seek(0)
    return text


def split_text_into_relevant_paragraphs(text):
    print("Starting to generate paragraphs")
    raw_paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    irrelevant_paragraph_keywords = [
        "introduction",
        "preface",
        "table of contents",
        "acknowledgements",
        "references",
        "bibliography",
        "index",
        "appendix",
    ]
    paragraphs = []
    for para in raw_paragraphs:
        lower_para = para.lower()
        if any(
            keyword in lower_para for keyword in irrelevant_paragraph_keywords
        ):
            print(f"Skipping irrelevant paragraph {para[:30]}...")
            continue
        cleaned_para = para.strip()
        if cleaned_para:
            paragraphs.append(cleaned_para)
    return paragraphs


def generate_useful_sequences(text):
    paragraphs = split_text_into_relevant_paragraphs(text)
    print("Filtered paragraphs: ", paragraphs)
    useful_sentences = []
    min_word_count = 3
    for paragraph in paragraphs:
        sentences = sent_tokenize(paragraph)
        for sentence in sentences:
            print("Sentence:", sentence)
            # TODO improve logic for usefulness based on nouns, verbs etc
            # TODO add score to sentences based on amount of verbs and nouns
            if len(sentence.split()) >= min_word_count:
                useful_sentences.append(sentence)
    return useful_sentences


def generate_quiz_from_text(text):
    # For demo, naive splitting and dummy questions
    questions = []
    print("Before logic")
    useful_sentences = generate_useful_sequences(text)
    # TODO randomize order
    print("AFter logic")
    for i, para in enumerate(
        useful_sentences[:5]
    ):  # limit number of questions
        question_text = f"What is the main idea of paragraph {i+1}?"
        answers = [
            {"answer_text": para, "correct": True},
            {"answer_text": "Wrong answer 1", "correct": False},
            {"answer_text": "Wrong answer 2", "correct": False},
            {"answer_text": "Wrong answer 3", "correct": False},
        ]
        questions.append({"question_text": question_text, "answers": answers})

    quiz_dict = {
        "title": "Generated Quiz from Uploaded File",
        "description": "Quiz generated automatically from file content.",
        "questions": questions,
    }
    return quiz_dict
