import frappe
import json

@frappe.whitelist()
def employee_query_for_task(doctype, txt, searchfield, start, page_len, filters):
    if isinstance(filters, str):
        filters = json.loads(filters)

    names = filters.get("name") if filters else None
    if not names:
        return []

    # ignore_permissions=True fixes the client-side PermissionError crash
    employees = frappe.get_all(
        "Employee",
        filters={"name": ["in", names], "status": "Active"},
        fields=["name", "employee_name"],
        limit_start=start,
        limit_page_length=page_len,
        ignore_permissions=True
    )
    return [(e.name, e.employee_name) for e in employees]
