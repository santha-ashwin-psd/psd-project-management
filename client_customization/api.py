import frappe

@frappe.whitelist()
def get_users_by_role(role, exclude_role=None):
    users = [
        d.parent for d in frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            fields=["parent"]
        )
    ]
    
    if exclude_role:
        exclude_users = [
            d.parent for d in frappe.get_all(
                "Has Role",
                filters={"role": exclude_role, "parenttype": "User"},
                fields=["parent"]
            )
        ]
        users = [u for u in users if u not in exclude_users]
        
    if "Administrator" in users:
        users.remove("Administrator")
        
    return users

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def project_assign_user_query(doctype, txt, searchfield, start, page_len, filters):
    valid_users = filters.get("name", [])
    if isinstance(valid_users, list) and len(valid_users) > 1:
        valid_users = valid_users[1]

    return frappe.get_all(
        "User", 
        filters={"name": ["in", valid_users], "enabled": 1, "user_type": "System User"}, 
        fields=["name", "full_name"], 
        as_list=True
    )

def fix_perm():
    import frappe
    exists = frappe.db.exists("Custom DocPerm", {"parent": "Project", "role": "Projects Manager"})
    if not exists:
        doc = frappe.new_doc("Custom DocPerm")
        doc.parent = "Project"
        doc.parenttype = "DocType"
        doc.parentfield = "permissions"
        doc.role = "Projects Manager"
        doc.read = 1
        doc.write = 1
        doc.create = 1
        doc.delete = 1
        doc.submit = 0
        doc.cancel = 0
        doc.amend = 0
        doc.export = 1
        doc.import_ = 1
        doc.report = 1
        doc.share = 1
        doc.print = 1
        doc.email = 1
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        doc = frappe.get_doc("Custom DocPerm", exists)
        doc.create = 1
        doc.write = 1
        doc.save(ignore_permissions=True)
        frappe.db.commit()

def fix_projects_user_perm():
    import frappe
    exists = frappe.db.exists("Custom DocPerm", {"parent": "Project", "role": "Projects User"})
    if not exists:
        doc = frappe.new_doc("Custom DocPerm")
        doc.parent = "Project"
        doc.parenttype = "DocType"
        doc.parentfield = "permissions"
        doc.role = "Projects User"
        doc.read = 1
        doc.write = 0
        doc.create = 0
        doc.delete = 0
        doc.submit = 0
        doc.cancel = 0
        doc.amend = 0
        doc.export = 0
        doc.import_ = 0
        doc.report = 1
        doc.share = 0
        doc.print = 1
        doc.email = 0
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
    else:
        doc = frappe.get_doc("Custom DocPerm", exists)
        doc.read = 1
        doc.create = 0
        doc.write = 0
        doc.delete = 0
        doc.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def employee_group_query(doctype, txt, searchfield, start, page_len, filters):
    valid_employees = filters.get("name", [])
    if isinstance(valid_employees, list) and len(valid_employees) > 1:
        valid_employees = valid_employees[1]

    if not valid_employees:
        return []

    return frappe.get_all(
        "Employee",
        filters={"name": ["in", valid_employees], "status": "Active"},
        fields=["name", "employee_name"],
        as_list=True
    )
