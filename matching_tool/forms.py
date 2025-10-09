from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'document_type']
        widgets = {
            'document_type': forms.RadioSelect(),
        }