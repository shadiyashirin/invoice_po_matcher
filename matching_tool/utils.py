# matching_app/utils.py

import pytesseract
from PIL import Image
import re
from django.conf import settings
import os

def extract_data(file_path):
    try:
        image_path = os.path.join(settings.MEDIA_ROOT, file_path)
        text = pytesseract.image_to_string(Image.open(image_path))

        # Simple regex patterns for data extraction
        data = {}
        data['doc_number'] = re.search(r'(INV|PO)\s*#?\s*:\s*(\S+)', text, re.IGNORECASE)
        data['vendor'] = re.search(r'Vendor:\s*(\S+\s+\S+)', text, re.IGNORECASE)
        data['total'] = re.search(r'Total:\s*\$([0-9,.]+)', text, re.IGNORECASE)
        data['items'] = re.findall(r'(\S.*\s*\$([0-9.]+))', text)

        extracted_data = {}
        extracted_data['doc_number'] = data['doc_number'].group(2) if data['doc_number'] else 'N/A'
        extracted_data['vendor'] = data['vendor'].group(1) if data['vendor'] else 'N/A'
        extracted_data['total'] = float(data['total'].group(1).replace(',', '')) if data['total'] else 0.0

        # This part is simplified; a more robust solution would be needed for production
        extracted_data['items'] = [item[0] for item in data['items']]

        return extracted_data
    except Exception as e:
        print(f"Error during OCR extraction: {e}")
        return None

def compare_documents(invoice_data, po_data):
    results = {
        'status': 'Perfect Match',
        'differences': []
    }

    if invoice_data['doc_number'] != po_data['doc_number']:
        results['differences'].append('Document numbers do not match.')
        results['status'] = 'Mismatch'

    if invoice_data['vendor'] != po_data['vendor']:
        results['differences'].append('Vendor names do not match.')
        results['status'] = 'Mismatch'

    if invoice_data['total'] != po_data['total']:
        diff = abs(invoice_data['total'] - po_data['total'])
        results['differences'].append(f'Price difference of ${diff:.2f}.')
        results['status'] = 'Mismatch'

    # Simple item list comparison
    if set(invoice_data['items']) != set(po_data['items']):
        results['differences'].append('Items do not match.')
        results['status'] = 'Mismatch'

    return results