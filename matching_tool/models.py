
# matching_app/models.py

from django.db import models

class UploadedDocument(models.Model):
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('po', 'Purchase Order'),
    ]
    file = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # We can add fields for extracted data later if we want to store it
    # vendor = models.CharField(max_length=255, blank=True, null=True)
    # total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.file.name
