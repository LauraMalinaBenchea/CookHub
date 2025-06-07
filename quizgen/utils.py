import docx
import fitz


def extract_text_from_file(file_path: str, file_type: str) -> str:

    if file_type == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return ""


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
