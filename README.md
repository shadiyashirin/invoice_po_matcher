# AI-Powered Invoice & Purchase Order Matching Tool

This project is a web-based application built with Django and powered by Google's Generative AI. It allows users to upload an invoice and a corresponding purchase order (in PDF or image format) and automatically compares them to find discrepancies.

The tool intelligently extracts key information such as invoice/PO numbers, vendor/issuer names, line items (including descriptions and quantities), and total amounts. It then performs a sophisticated, business-logic-aware comparison to approve the match or flag specific issues for review.

## Key Features

- **File Upload:** Accepts both PDF and image files for invoices and purchase orders.
- **Hybrid Text Extraction:** Uses PyMuPDF for fast and accurate text extraction from digital PDFs and Tesseract OCR for scanned image-based documents.
- **AI-Powered Data Parsing:** Leverages Google's Generative AI (Gemini) to understand the unstructured text and extract structured data in a reliable JSON format, eliminating the need for brittle regex.
- **Intelligent Comparison Logic:**
  - Matches invoice numbers against Purchase Requisition (PR) numbers.
  - Compares partial IDs, ignoring company-specific prefixes.
  - Cross-references vendor and issuer names for a more robust match.
  - Compares line items based on normalized descriptions and quantities.

## Technology Stack

- **Backend:** Python, Django
- **AI:** Google Generative AI (Gemini) via google-generativeai SDK
- **Text Extraction:** PyMuPDF (for PDFs), Pytesseract (for OCR on images)
- **Frontend:** HTML, Bootstrap 5

## Prerequisites

- Python 3.8+
- Tesseract OCR Engine (required by pytesseract)
  - **Windows**: Install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and ensure the installation directory is in your system's PATH.
- A Google AI API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

## Installation & Setup

1. **Clone the repository**:  
   ```bash
   git clone <your-repository-url>  
   cd <your-repository-folder>

2. Create Virtual Environment
   ```bash
   python -m venv venv
    On Windows, use `venv\Scripts\activate`

3. Install Dependencies
   ```bash
   pip install -r requirements.txt

4. Configure Environment Secrets
Create a .env file in the project root for your API key.
   ```bash
   GOOGLE_API_KEY="your-new-secret-google-api-key"

5. Run Database Migrations
    ```bash
    python manage.py migrate

7. Start the Development Server
    ```bash
    python manage.py runserver


