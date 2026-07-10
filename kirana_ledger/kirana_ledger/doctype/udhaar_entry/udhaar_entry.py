import frappe
from frappe.model.document import Document


class UdhaarEntry(Document):
    """A single udhaar (credit) or payment entry for a customer.

    Each entry updates the customer's running balance automatically via
    before_save. Entries are submittable (is_submittable = 1) so they
    cannot be accidentally modified after creation.
    """

    def before_save(self):
        """Compute balance_after before saving the entry."""
        self.date = self.date or frappe.utils.today()

        # Fetch the customer's current balance
        customer = frappe.get_doc("Udhaar Customer", self.customer)
        current_balance = customer.current_balance or 0.0

        if self.entry_type == "Credit Given":
            self.balance_after = current_balance + self.amount
        elif self.entry_type == "Payment Received":
            self.balance_after = max(0, current_balance - self.amount)

    def on_submit(self):
        """On submit, update the customer's current balance."""
        self._update_customer_balance()

    def on_cancel(self):
        """On cancel, reverse the balance change."""
        customer = frappe.get_doc("Udhaar Customer", self.customer)
        if self.entry_type == "Credit Given":
            customer.current_balance = max(0, customer.current_balance - self.amount)
        elif self.entry_type == "Payment Received":
            customer.current_balance = customer.current_balance + self.amount
        customer.save()

        # Update last payment date if payment was reversed
        if self.entry_type == "Payment Received":
            customer.last_payment_date = self._get_last_payment_date()
            customer.save()

    def _update_customer_balance(self):
        """Update the linked customer's running balance."""
        customer = frappe.get_doc("Udhaar Customer", self.customer)
        customer.current_balance = self.balance_after

        if self.entry_type == "Payment Received":
            customer.last_payment_date = self.date

        customer.save()

    def _get_last_payment_date(self):
        """Find the most recent payment date for this customer."""
        last_payment = frappe.db.get_value(
            "Udhaar Entry",
            filters={
                "customer": self.customer,
                "entry_type": "Payment Received",
                "docstatus": 1,
                "name": ["!=", self.name],
            },
            fieldname="date",
            order_by="date desc",
        )
        return last_payment
