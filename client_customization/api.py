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



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def employee_group_query(doctype, txt, searchfield, start, page_len, filters):
    valid_employees = filters.get("name", [])
    if isinstance(valid_employees, list) and len(valid_employees) > 1:
        valid_employees = valid_employees[1]

    if not valid_employees:
        return []

    search_filters = []
    if txt:
        search_filters = [
            ["Employee", "name", "like", f"%{txt}%"],
            ["Employee", "employee_name", "like", f"%{txt}%"],
            ["Employee", "user_id", "like", f"%{txt}%"]
        ]

    return frappe.get_all(
        "Employee",
        filters={
            "name": ["in", valid_employees], 
            "status": "Active"
        },
        or_filters=search_filters if txt else None,
        fields=["name", "employee_name", "user_id"],
        as_list=True
    )
