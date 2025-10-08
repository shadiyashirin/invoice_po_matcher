from difflib import SequenceMatcher
import Levenshtein

class DocumentMatcher:
    def __init__(self):
        pass
    
    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def match_documents(self, invoice, purchase_order):
        """Match invoice and purchase order documents"""
        discrepancies = []
        match_score = 0.0
        weights = {
            'vendor': 0.2,
            'items': 0.5,
            'total': 0.3
        }
        
        # Check vendor match
        vendor_similarity = self.calculate_similarity(
            invoice.vendor_name, 
            purchase_order.vendor_name
        )
        if vendor_similarity < 0.8:
            discrepancies.append(f"Vendor mismatch: {invoice.vendor_name} vs {purchase_order.vendor_name}")
        
        # Check total amount match
        total_match = invoice.total_amount == purchase_order.total_amount
        if not total_match:
            discrepancies.append(f"Total amount mismatch: ${invoice.total_amount} vs ${purchase_order.total_amount}")
        
        # Check items match
        item_discrepancies = self.match_items(invoice.items.all(), purchase_order.items.all())
        discrepancies.extend(item_discrepancies)
        
        # Calculate overall match score
        vendor_score = vendor_similarity * weights['vendor']
        total_score = (1.0 if total_match else 0.0) * weights['total']
        items_score = self.calculate_items_similarity(invoice.items.all(), purchase_order.items.all()) * weights['items']
        
        match_score = vendor_score + total_score + items_score
        
        return {
            'match_score': match_score,
            'is_perfect_match': len(discrepancies) == 0 and match_score > 0.95,
            'discrepancies': discrepancies
        }
    
    def match_items(self, invoice_items, po_items):
        """Match items between invoice and purchase order"""
        discrepancies = []
        
        # Convert to lists for easier processing
        inv_items = list(invoice_items)
        po_items_list = list(po_items)
        
        # Check if number of items match
        if len(inv_items) != len(po_items_list):
            discrepancies.append(f"Number of items mismatch: {len(inv_items)} vs {len(po_items_list)}")
        
        # Match individual items
        for i, inv_item in enumerate(inv_items):
            if i < len(po_items_list):
                po_item = po_items_list[i]
                
                # Check description similarity
                desc_similarity = self.calculate_similarity(inv_item.description, po_item.description)
                if desc_similarity < 0.8:
                    discrepancies.append(f"Item description mismatch: '{inv_item.description}' vs '{po_item.description}'")
                
                # Check quantity
                if inv_item.quantity != po_item.quantity:
                    discrepancies.append(f"Quantity mismatch for '{inv_item.description}': {inv_item.quantity} vs {po_item.quantity}")
                
                # Check unit price
                if inv_item.unit_price != po_item.unit_price:
                    discrepancies.append(f"Unit price mismatch for '{inv_item.description}': ${inv_item.unit_price} vs ${po_item.unit_price}")
            else:
                discrepancies.append(f"Extra item in invoice: '{inv_item.description}'")
        
        # Check for missing items in invoice
        if len(po_items_list) > len(inv_items):
            for i in range(len(inv_items), len(po_items_list)):
                discrepancies.append(f"Missing item in invoice: '{po_items_list[i].description}'")
        
        return discrepancies
    
    def calculate_items_similarity(self, invoice_items, po_items):
        """Calculate overall similarity between item lists"""
        if not invoice_items and not po_items:
            return 1.0
        if not invoice_items or not po_items:
            return 0.0
        
        total_similarity = 0.0
        min_len = min(len(invoice_items), len(po_items))
        
        for i in range(min_len):
            inv_item = list(invoice_items)[i]
            po_item = list(po_items)[i]
            
            desc_sim = self.calculate_similarity(inv_item.description, po_item.description)
            qty_sim = 1.0 if inv_item.quantity == po_item.quantity else 0.0
            price_sim = 1.0 if inv_item.unit_price == po_item.unit_price else 0.0
            
            item_sim = (desc_sim + qty_sim + price_sim) / 3.0
            total_similarity += item_sim
        
        return total_similarity / max(len(invoice_items), len(po_items))