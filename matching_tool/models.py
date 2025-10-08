
'''class Document(models.Model):
    DOCUMENT_TYPES = (
        ('invoice', 'Invoice'),
        ('purchase_order', 'Purchase Order'),
    )
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_data = models.JSONField(null=True, blank=True)
    
    # Common fields
    document_number = models.CharField(max_length=100, blank=True)
    date = models.DateField(null=True, blank=True)
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_email = models.EmailField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.document_number}"

class Item(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

class DocumentMatch(models.Model):
    invoice = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='invoice_matches')
    purchase_order = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='po_matches')
    match_score = models.FloatField()  # 0-1 scale
    is_perfect_match = models.BooleanField(default=False)
    discrepancies = models.JSONField()  # Store mismatches as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Match: {self.invoice.document_number} - {self.purchase_order.document_number}"
        '''

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
