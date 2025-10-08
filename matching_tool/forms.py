from django import forms
from .models import Document

'''class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }'''

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'document_type']
        widgets = {
            'document_type': forms.RadioSelect(),
        }