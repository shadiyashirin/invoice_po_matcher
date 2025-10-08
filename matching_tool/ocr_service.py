import pytesseract
from PIL import Image
import pathlib
import fitz
import json
import re
from django.conf import settings
import google.generativeai as genai

# The text extraction function remains the same
def extract_text_from_file(file_path):
    file_extension = pathlib.Path(file_path).suffix.lower()
    try:
        if file_extension == '.pdf':
            full_text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    full_text += page.get_text()
            return full_text
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            return pytesseract.image_to_string(Image.open(file_path))
        else:
            return ""
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ""


# The upgraded AI parsing function with more detailed extraction
def parse_document_with_ai(text):
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash')

    # --- UPGRADED PROMPT TO INCLUDE PR NUMBER ---
    prompt = f"""
    Analyze the following document text and extract the specified information.
    Provide the output ONLY in a clean JSON format.
    The keys should be: "issuer", "vendor", "invoice_id", "po_id", "pr_id", "total_amount", and "line_items".
    - "issuer": The company that issued the document.
    - "vendor": The supplier or vendor.
    - "invoice_id": The invoice number (e.g., "INV-123"). Null if not present.
    - "po_id": The purchase order number (e.g., "PO-456"). Null if not present.
    - "pr_id": The purchase requisition number (e.g., "PR-789" or "PR No"). This is important. Null if not present.
    - "total_amount": The final total amount as a float. Null if not present.
    - "line_items": An array of objects with "description", "quantity", and "price". An empty array [] if none.

    DOCUMENT TEXT:
    ---
    {text}
    ---
    """

    try:
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        
        if match:
            json_response = match.group(0)
            data = json.loads(json_response)
            # Ensure pr_id key exists
            if 'pr_id' not in data:
                data['pr_id'] = None
            return data
        else:
            raise ValueError("No valid JSON found in the AI response.")

    except Exception as e:
        print(f"An error occurred with the AI model or JSON parsing: {e}")
        return {
            'error': str(e), 'issuer': None, 'vendor': None, 'invoice_id': None,
            'po_id': None, 'pr_id': None, 'total_amount': None, 'line_items': []
        }

