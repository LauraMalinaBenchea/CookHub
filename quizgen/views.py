from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import UploadedFileForm
from .utils import extract_text_from_file


class FileUploadView(FormView):
    template_name = "quizgen/upload.html"
    form_class = UploadedFileForm
    success_url = reverse_lazy("upload_file")

    def form_valid(self, form):
        uploaded_file = form.save()
        file_path = uploaded_file.file.path

        try:
            extracted_text = extract_text_from_file(file_path)
            print("Extracted Text:\n", extracted_text[:1000])  # For debugging
        except Exception as e:
            print(f"Error extracting text: {e}")

        return super().form_valid(form)
