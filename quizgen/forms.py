from django import forms

from .models import UploadedFile


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["file"]  # removed 'file_type'

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext not in ["pdf", "docx"]:
            raise forms.ValidationError(
                "Only .pdf and .docx files are supported."
            )
        return uploaded_file
