
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

