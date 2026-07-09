import frappe
from frappe.model.document import Document


class UdhaarCustomer(Document):
    """Represents a shop's customer for udhaar (credit) tracking.

    Kirana shop owners maintain informal credit relationships with
    regular customers. This DocType tracks each customer's running
    balance and preferred language for WhatsApp communication.
    """

    def validate(self):
        if self.credit_limit and self.current_balance > self.credit_limit:
            frappe.msgprint(
                msg=f"⚠️ {self.customer_name}'s current balance (₹{self.current_balance:,.0f}) "
                    f"exceeds their credit limit (₹{self.credit_limit:,.0f}).",
                title="Credit Limit Breach",
                indicator="red",
            )
