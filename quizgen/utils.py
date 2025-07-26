import re

import docx
import fitz
import nltk
import spacy
from nltk.tokenize import sent_tokenize

from quizgen.constants import (
    IRRELEVANT_PARAGRAPH_KEYWORDS,
    RELEVANT_ENTITIES_LABELS,
)

nlp = spacy.load("en_core_web_sm")


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
    """
    Removes irrelevant paragraphs and returns a list of relevant paragraphs.
    """
    raw_paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = []
    for para in raw_paragraphs:
        lower_para = para.lower()
        if any(
            keyword in lower_para for keyword in IRRELEVANT_PARAGRAPH_KEYWORDS
        ):
            continue
        cleaned_para = para.strip()
        if cleaned_para:
            paragraphs.append(cleaned_para)
    return paragraphs


def contains_named_entities(sentence):
    doc = nlp(sentence)
    return any(ent.label_ in RELEVANT_ENTITIES_LABELS for ent in doc.ents)


def has_basic_structure(sentence):
    doc = nlp(sentence)
    has_noun = any(token.pos_ == "NOUN" for token in doc)
    has_verb = any(token.pos_ == "VERB" for token in doc)
    return has_noun and has_verb


def is_answerable(sentence: str) -> bool:
    doc = nlp(sentence)
    # Check for at least one relevant entity
    relevant_entities = [
        ent for ent in doc.ents if ent.label_ in RELEVANT_ENTITIES_LABELS
    ]
    if not relevant_entities:
        return False

    # Check if sentence has at least one verb and noun
    has_noun = any(token.pos_ == "NOUN" for token in doc)
    has_verb = any(token.pos_ == "VERB" for token in doc)
    if not (has_noun and has_verb):
        return False

    # Length check
    length = len(sentence.split())
    if length < 5:
        return False

    return True


def score_sentence(sentence: str) -> int:
    doc = nlp(sentence)
    score = 0

    ent_count = sum(
        1 for ent in doc.ents if ent.label_ in RELEVANT_ENTITIES_LABELS
    )
    score += ent_count * 2

    has_noun = any(token.pos_ == "NOUN" for token in doc)
    has_verb = any(token.pos_ == "VERB" for token in doc)
    if has_noun and has_verb:
        score += 2

    length = len(sentence.split())
    if 7 <= length <= 25:
        score += 2
    elif length > 25:
        score += 1

    important_verbs = {
        "invade",
        "conquer",
        "sign",
        "agree",
        "born",
        "declare",
        "discover",
        "fight",
        "argue",
        "debate",
        "start",
        "end",
    }
    verbs = {token.lemma_ for token in doc if token.pos_ == "VERB"}
    if verbs.intersection(important_verbs):
        score += 2

    # 5. Answerability check: can we generate a meaningful question and answer?
    # For example, presence of PERSON or DATE makes question generation easier
    if any(ent.label_ in {"PERSON", "DATE", "GPE", "ORG"} for ent in doc.ents):
        score += 1  # bonus point

    return score


def get_top_relevant_sentences(sentences, top_n=10):
    scored = [(s, score_sentence(s)) for s in sentences]
    scored = sorted(scored, key=lambda x: x[1], reverse=True)
    return [s for s, score in scored[:top_n]]


def generate_useful_sequences(text):
    paragraphs = split_text_into_relevant_paragraphs(text)
    useful_sentences = []
    for para in paragraphs:
        sentences = sent_tokenize(para)
        for sentence in sentences:
            score = score_sentence(sentence)
            if score >= 5 and is_answerable(sentence):
                useful_sentences.append((sentence, score))
    return useful_sentences


def generate_question_from_sentence_2(sentence: str) -> str:
    doc = nlp(sentence)

    # Collect entities by label
    entities = {ent.label_: ent.text for ent in doc.ents}

    # Try patterns by entity type
    if "PERSON" in entities:
        # Ask who the person is or did something
        return "Who was {entities['PERSON']}?"

    if "DATE" in entities:
        # Find subject or event near date, ask when
        # TODO change this to be of the form: in what year... happened?
        return "When did the events described happen?"

    if "GPE" in entities:
        # Ask where something happened
        return "Where did the events take place?"

    if "ORG" in entities:
        return "What is {entities['ORG']}?"

    # Look for keywords like 'invaded', 'conquered', 'signed', 'declared war'
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    if "invade" in verbs or "conquer" in verbs:
        return "What military action is described in this sentence?"

    if "sign" in verbs or "agree" in verbs:
        return "What agreement is described in this sentence?"

    # Specific pattern for 'born' (you had before)
    for token in doc:
        if (
            token.lemma_ == "bear"
            and token.head.text == "born"
            or token.text.lower() == "born"
        ):
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return f"When was {ent.text} born?"

    # Fallback generic question
    return f"What is the main idea of the sentence: '{sentence}'?"


def simple_fact_question(sentence):
    doc = nlp(sentence)
    person = None
    date = None
    gpe = None
    verb = None

    # Find entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            person = ent.text
        elif ent.label_ == "DATE":
            date = ent.text
        elif ent.label_ == "GPE":
            gpe = ent.text

    # Find first main verb (simplify by picking first verb)
    for token in doc:
        if token.pos_ == "VERB":
            verb = token.lemma_
            break

    # Construct questions based on what we have
    if person and date:
        return f"When did {person} {verb}?"
    elif person and verb:
        return f"Who {verb}?"
    elif date:
        return f"What happened in {date}?"
    elif gpe:
        return f"What happened in {gpe}?"
    else:
        # fallback question
        return f"What is the main idea of: '{sentence}'?"


# Output: "When did Hitler invade?"


def generate_quiz_from_text(text):
    questions = []
    useful_sentences = generate_useful_sequences(text)
    # TODO randomize order
    for i, (sentence, score) in enumerate(useful_sentences[5:]):
        # TODO: max nr of sentences should be given during generation
        generated_question = simple_fact_question(sentence)
        question_text = generated_question

        answers = [
            # max 200 as field allows
            {"answer_text": sentence[:200], "correct": True},
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
