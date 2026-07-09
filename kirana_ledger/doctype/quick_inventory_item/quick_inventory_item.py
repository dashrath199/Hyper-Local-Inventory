from frappe.model.document import Document


class QuickInventoryItem(Document):
    """Lightweight inventory item for kirana shops.

    Kirana stock counts are approximate by nature — forcing exact
    stock ledger accounting (ERPNext's default assumption) will make
    shop owners abandon the tool. This DocType accepts approximate
    estimates and a simple reorder flag instead.
    """

    def validate(self):
        if self.reorder_flag and self.current_stock_estimate > 0:
            # Auto-clear reorder flag if stock is available
            self.reorder_flag = 0
