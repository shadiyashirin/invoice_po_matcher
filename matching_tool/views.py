'''from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
import os
from datetime import datetime
from .models import Document, DocumentMatch, Item
from .forms import DocumentUploadForm'''

'''# Try to import OCR, but make it optional
try:
    from .ocr_service import OCRProcessor
    from .matching_service import DocumentMatcher
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"OCR not available: {e}")
    OCR_AVAILABLE = False

def upload_documents(request):
    if not OCR_AVAILABLE:
        return render(request, 'matching_tool/upload.html', {
            'invoice_form': DocumentUploadForm(prefix='invoice'),
            'po_form': DocumentUploadForm(prefix='purchase_order'),
            'error': "OCR functionality not available. Please install required packages."
        })
    
    if request.method == 'POST':
        invoice_form = DocumentUploadForm(request.POST, request.FILES, prefix='invoice')
        po_form = DocumentUploadForm(request.POST, request.FILES, prefix='purchase_order')
        
        if invoice_form.is_valid() and po_form.is_valid():
            try:
                # Save documents
                invoice = invoice_form.save(commit=False)
                invoice.document_type = 'invoice'
                invoice.save()
                
                purchase_order = po_form.save(commit=False)
                purchase_order.document_type = 'purchase_order'
                purchase_order.save()
                
                # Process with OCR
                ocr_processor = OCRProcessor()
                
                # Process invoice
                invoice_data = ocr_processor.process_document(invoice.file.path, 'invoice')
                invoice.document_number = invoice_data.get('document_number', '')
                
                # Handle date conversion safely
                date_str = invoice_data.get('date')
                if date_str:
                    try:
                        invoice.date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError as e:
                        print(f"Date conversion error for invoice: {e}")
                        invoice.date = None
                
                invoice.vendor_name = invoice_data.get('vendor_name', '')
                invoice.vendor_email = invoice_data.get('vendor_email', '')
                invoice.total_amount = invoice_data.get('total_amount', 0)
                invoice.extracted_data = invoice_data
                invoice.save()
                
                # Save invoice items
                for item_data in invoice_data.get('items', []):
                    Item.objects.create(
                        document=invoice,
                        description=item_data['description'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        total_price=item_data['total_price']
                    )
                
                # Process purchase order
                po_data = ocr_processor.process_document(purchase_order.file.path, 'purchase_order')
                purchase_order.document_number = po_data.get('document_number', '')
                
                # Handle date conversion safely for PO
                po_date_str = po_data.get('date')
                if po_date_str:
                    try:
                        purchase_order.date = datetime.strptime(po_date_str, '%Y-%m-%d').date()
                    except ValueError as e:
                        print(f"Date conversion error for PO: {e}")
                        purchase_order.date = None
                
                purchase_order.vendor_name = po_data.get('vendor_name', '')
                purchase_order.vendor_email = po_data.get('vendor_email', '')
                purchase_order.total_amount = po_data.get('total_amount', 0)
                purchase_order.extracted_data = po_data
                purchase_order.save()
                
                # Save PO items
                for item_data in po_data.get('items', []):
                    Item.objects.create(
                        document=purchase_order,
                        description=item_data['description'],
                        quantity=item_data['quantity'],
                        unit_price=item_data['unit_price'],
                        total_price=item_data['total_price']
                    )
                
                # Perform matching
                matcher = DocumentMatcher()
                match_result = matcher.match_documents(invoice, purchase_order)
                
                # Save match result
                document_match = DocumentMatch.objects.create(
                    invoice=invoice,
                    purchase_order=purchase_order,
                    match_score=match_result['match_score'],
                    is_perfect_match=match_result['is_perfect_match'],
                    discrepancies=match_result['discrepancies']
                )
                
                # FIX: Use simple URL name without app namespace
                return redirect(f'/results/{document_match.id}/')
                
            except Exception as e:
                # More detailed error message
                error_msg = f"Error processing documents: {str(e)}"
                if "date" in str(e).lower():
                    error_msg += ". There was an issue with date parsing. Please check the document format."
                
                return render(request, 'matching_tool/upload.html', {
                    'invoice_form': invoice_form,
                    'po_form': po_form,
                    'error': error_msg
                })
    else:
        invoice_form = DocumentUploadForm(prefix='invoice')
        po_form = DocumentUploadForm(prefix='purchase_order')
    
    return render(request, 'matching_tool/upload.html', {
        'invoice_form': invoice_form,
        'po_form': po_form
    })

def match_results(request, match_id):
    try:
        document_match = get_object_or_404(DocumentMatch, id=match_id)
        
        context = {
            'match': document_match,
            'invoice': document_match.invoice,
            'purchase_order': document_match.purchase_order,
            'invoice_items': document_match.invoice.items.all(),
            'po_items': document_match.purchase_order.items.all(),
        }
        
        return render(request, 'matching_tool/match_results.html', context)
    except DocumentMatch.DoesNotExist:
        return render(request, 'matching_tool/error.html', {'error': 'Match not found'})

def document_list(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    matches = DocumentMatch.objects.all().order_by('-created_at')
    
    return render(request, 'matching_tool/document_list.html', {
        'documents': documents,
        'matches': matches
    })'''


# matching_app/views.py

'''from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from .utils import extract_data, compare_documents

def upload_documents(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_documents')
    else:
        form = DocumentForm()

    documents = Document.objects.all()
    invoices = documents.filter(document_type='invoice')
    pos = documents.filter(document_type='po')

    return render(request, 'matching_tool/upload.html', {
        'form': form,
        'invoices': invoices,
        'pos': pos
    })

def match_results(request):
    invoice_id = request.GET.get('invoice_id')
    po_id = request.GET.get('po_id')

    if not invoice_id or not po_id:
        return redirect('upload_documents')

    try:
        invoice = Document.objects.get(id=invoice_id)
        po = Document.objects.get(id=po_id)

        invoice_data = extract_data(str(invoice.file))
        po_data = extract_data(str(po.file))

        if invoice_data and po_data:
            comparison_results = compare_documents(invoice_data, po_data)
        else:
            comparison_results = {'status': 'Error', 'differences': ['Could not extract data from one or both documents.']}

        context = {
            'invoice': invoice,
            'po': po,
            'invoice_data': invoice_data,
            'po_data': po_data,
            'results': comparison_results
        }
        return render(request, 'matching_tool/match_results.html', context)
    except Document.DoesNotExist:
        return redirect('upload_documents')'''

from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .ocr_service import extract_text_from_file, parse_document_with_ai
import re

# --- UPDATED HELPER FUNCTIONS ---

def get_id_suffix(s):
    """Extracts the part of the ID string after the first hyphen."""
    if not s or not isinstance(s, str) or '-' not in s:
        return None
    return s.split('-', 1)[1]

def normalize_description(desc):
    """Simplifies a product description to its core name for better matching."""
    if not desc:
        return ""
    words = desc.lower().split()[:2]
    return re.sub(r'[^a-z0-9]', '', "".join(words))

def compare_line_items(invoice_items, po_items):
    """
    Compares two lists of line items and returns a detailed dictionary 
    with a match status and a list of specific discrepancies.
    """
    result = {
        'match': True,
        'mismatched_details': []
    }
    
    # Create maps of items {normalized_description: quantity}
    invoice_map = {normalize_description(item.get('description')): int(item.get('quantity', 1)) for item in invoice_items if item.get('description')}
    po_map = {normalize_description(item.get('description')): int(item.get('quantity', 1)) for item in po_items if item.get('description')}

    # Get a set of all unique item descriptions from both documents
    all_item_keys = set(invoice_map.keys()) | set(po_map.keys())

    if not all_item_keys and not (invoice_items or po_items):
        return result # Both are empty, so they match.

    for key in all_item_keys:
        invoice_qty = invoice_map.get(key, 0)
        po_qty = po_map.get(key, 0)
        
        if invoice_qty != po_qty:
            result['match'] = False
            # Find the original, non-normalized description for a user-friendly message
            original_desc = "[Unknown Item]"
            for item in invoice_items + po_items:
                if normalize_description(item.get('description')) == key:
                    original_desc = item.get('description')
                    break
            
            result['mismatched_details'].append(
                f'Item "{original_desc}": Invoice has quantity {invoice_qty}, but PO has quantity {po_qty}.'
            )

    return result


def upload_and_match_view(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('invoice_file') and request.FILES.get('po_file'):
        # File handling logic remains the same...
        invoice_file = request.FILES['invoice_file']
        po_file = request.FILES['po_file']
        fs = FileSystemStorage()
        invoice_path = fs.save(invoice_file.name, invoice_file)
        po_path = fs.save(po_file.name, po_file)
        invoice_full_path = fs.path(invoice_path)
        po_full_path = fs.path(po_path)

        invoice_text = extract_text_from_file(invoice_full_path)
        po_text = extract_text_from_file(po_full_path)
        invoice_data = parse_document_with_ai(invoice_text)
        po_data = parse_document_with_ai(po_text)

        results = {
            'invoice_data': invoice_data, 'po_data': po_data,
            'matches': {}, 'mismatch_details': [], 'is_perfect_match': False
        }
        
        if invoice_data.get('error') or po_data.get('error'):
            # Error handling remains the same...
            pass
        else:
            # ID and Vendor comparison logic remains the same...
            inv_id_suffix = get_id_suffix(invoice_data.get('invoice_id'))
            po_pr_id_suffix = get_id_suffix(po_data.get('pr_id'))
            po_id_suffix = get_id_suffix(po_data.get('po_id'))
            id_match = False
            if inv_id_suffix and (inv_id_suffix == po_pr_id_suffix or inv_id_suffix == po_id_suffix):
                id_match = True
            results['matches']['id'] = id_match
            if not id_match:
                results['mismatch_details'].append("Invoice and PO/PR numbers do not match.")

            invoice_issuer = invoice_data.get('issuer', '').lower()
            po_vendor = po_data.get('vendor', '').lower()
            vendor_match = invoice_issuer and po_vendor and (invoice_issuer in po_vendor or po_vendor in invoice_issuer)
            results['matches']['vendor'] = vendor_match
            if not vendor_match:
                results['mismatch_details'].append("Vendor names do not match.")

            # --- NEW LINE ITEM COMPARISON ---
            item_comparison_result = compare_line_items(invoice_data.get('line_items', []), po_data.get('line_items', []))
            items_match = item_comparison_result['match']
            results['matches']['items'] = items_match
            if not items_match:
                # Add the detailed item mismatches to our main list of discrepancies
                results['mismatch_details'].extend(item_comparison_result['mismatched_details'])

            # Total comparison logic remains the same...
            total_match = invoice_data.get('total_amount') is not None and \
            po_data.get('total_amount') is not None and \
            round(float(invoice_data['total_amount']), 2) == round(float(po_data['total_amount']), 2)
            results['matches']['total'] = total_match
            if not total_match and invoice_data.get('total_amount') is not None and po_data.get('total_amount') is not None:
                diff = abs(float(invoice_data['total_amount']) - float(po_data['total_amount']))
                results['mismatch_details'].append(f"Price difference of ${diff:.2f}!")

            if all(results['matches'].values()):
                results['is_perfect_match'] = True

        context['results'] = results
        fs.delete(invoice_path)
        fs.delete(po_path)

    return render(request, 'matching_tool/upload.html', context)

