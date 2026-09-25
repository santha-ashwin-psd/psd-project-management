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



@frappe.whitelist()
def fix_server_scripts():
    import frappe
    # 1. Before Insert
    doc1 = frappe.get_doc("Server Script", "Project Auto Assign Manager")
    doc1.script = """
if not doc.custom_assign_project_user:
    roles = [d.role for d in frappe.db.get_all("Has Role", filters={"parent": frappe.session.user}, fields=["role"])]
    if "Projects Manager" in roles:
        doc.custom_assign_project_user = frappe.session.user
"""
    doc1.save(ignore_permissions=True)

    # 2. After Save (Todo Assignment)
    doc2 = frappe.get_doc("Server Script", "Project Auto Create ToDo")
    doc2.script = """
if doc.has_value_changed("custom_assign_project_user") and doc.custom_assign_project_user:
    exists = frappe.db.exists(
        "ToDo",
        {
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "allocated_to": doc.custom_assign_project_user,
            "status": "Open"
        }
    )
    if not exists:
        try:
            todo = frappe.get_doc({
                "doctype": "ToDo",
                "reference_type": doc.doctype,
                "reference_name": doc.name,
                "allocated_to": doc.custom_assign_project_user,
                "description": "Project assigned via Manager form selector.",
                "status": "Open",
                "priority": "Medium"
            })
            todo.insert(ignore_permissions=True)
        except Exception:
            pass
"""
    doc2.save(ignore_permissions=True)
    frappe.db.commit()
    print("Fixed Server Scripts!")





@frappe.whitelist()
def add_timer_custom_fields():
    import frappe
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    custom_fields = {
        "Timesheet Detail": [
            {
                "fieldname": "custom_is_paused",
                "label": "Is Paused",
                "fieldtype": "Check",
                "insert_after": "completed",
                "hidden": 1,
                "default": "0"
            },
            {
                "fieldname": "custom_pause_start_time",
                "label": "Pause Start Time",
                "fieldtype": "Datetime",
                "insert_after": "custom_is_paused",
                "hidden": 1
            }
        ]
    }
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
    print("Custom fields added successfully.")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def project_task_query(doctype, txt, searchfield, start, page_len, filters):
    """Return tasks limited to a selected project. Intended for the timer Task link get_query.

    Expects filters to include `project`.
    """
    project = None
    if isinstance(filters, dict):
        project = filters.get("project")
    # Fallback for array-like filters from the Link field
    if not project and isinstance(filters, list):
        for f in filters:
            if isinstance(f, dict) and f.get("project"):
                project = f.get("project")

    if not project:
        return []

    # Return matching tasks (respecting permissions via frappe.get_all)
    return frappe.get_all(
        "Task",
        filters={"project": project},
        fields=["name", "subject"],
        as_list=True,
    )

def assign_without_email(user, doctype, name, description):
    from frappe.desk.form.assign_to import add as assign_to
    import frappe.desk.form.assign_to as assign_to_module
    import frappe.desk.doctype.notification_log.notification_log as nl

    original_enqueue = assign_to_module.enqueue_create_notification

    def custom_enqueue(users, doc, dedupe_on=None):
        if isinstance(users, str):
            users = [u.strip() for u in users.split(",") if u.strip()]
        
        original_email_check = nl.is_email_notifications_enabled_for_type
        
        for u in users:
            notification = frappe.new_doc("Notification Log")
            notification.update(doc)
            notification.for_user = u
            
            # Disable email check during insert to prevent emails
            nl.is_email_notifications_enabled_for_type = lambda user, type: False
            try:
                notification.insert(ignore_permissions=True)
            finally:
                nl.is_email_notifications_enabled_for_type = original_email_check

    assign_to_module.enqueue_create_notification = custom_enqueue
    try:
        assign_to({
            "assign_to": [user],
            "doctype": doctype,
            "name": name,
            "description": description
        })
    finally:
        assign_to_module.enqueue_create_notification = original_enqueue


def task_after_insert(doc, method):
    from frappe.desk.form.assign_to import add as assign_to
    
    # 1. Employee User (Gets Assigned, System Notification & Standard Email)
    if doc.custom_assign_employee:
        employee_user = frappe.db.get_value("Employee", doc.custom_assign_employee, "user_id")
        if employee_user:
            try:
                # Add to ToDo and Bell Icon without standard email
                assign_without_email(
                    user=employee_user,
                    doctype=doc.doctype,
                    name=doc.name,
                    description=doc.subject or doc.name
                )
                
                # Send custom HTML notification
                employee_email = frappe.db.get_value("User", employee_user, "email")
                if employee_email:
                    email_template = frappe.get_doc("Email Template", "Task Assignment")
                    assigner_name = frappe.utils.get_fullname(frappe.session.user)
                    subject = frappe.render_template(email_template.subject, {"doc": doc, "assigner_name": assigner_name})
                    message = frappe.render_template(email_template.response, {"doc": doc, "assigner_name": assigner_name})
                    
                    frappe.sendmail(
                        recipients=[employee_email],
                        subject=subject,
                        message=message,
                        with_container=False
                    )
            except Exception:
                frappe.log_error(message=frappe.get_traceback(), title="Task Auto Assignment Error (Employee)")
            
    # 2. Project User / Project Manager (Gets ONLY Bell Notification, NOT Assigned)
    if doc.project:
        project_user = frappe.db.get_value("Project", doc.project, "custom_assign_project_user")
        if project_user and (not employee_user or project_user != employee_user):
            try:
                notification = frappe.new_doc("Notification Log")
                notification.subject = f"New Task added to Project: {doc.subject or doc.name}"
                notification.for_user = project_user
                notification.type = "Alert"
                notification.document_type = doc.doctype
                notification.document_name = doc.name
                notification.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(message=frappe.get_traceback(), title="Task Auto Assignment Error (Project Manager)")


def project_after_save(doc, method):
    frappe.log_error(message=f"Project After Save Triggered for {doc.name}, User: {doc.custom_assign_project_user}, changed: {doc.has_value_changed('custom_assign_project_user')}", title="Project Assignment Debug")
    if doc.has_value_changed("custom_assign_project_user") and doc.custom_assign_project_user:
        exists = frappe.db.exists(
            "ToDo",
            {
                "reference_type": doc.doctype,
                "reference_name": doc.name,
                "allocated_to": doc.custom_assign_project_user,
                "status": "Open"
            }
        )
        frappe.log_error(message=f"ToDo exists: {exists}", title="Project Assignment Debug")
        if not exists:
            try:
                from frappe.desk.form.assign_to import add as assign_to
                # Project Manager gets Standard System Notification and Email
                assign_to({
                    "assign_to": [doc.custom_assign_project_user],
                    "doctype": doc.doctype,
                    "name": doc.name,
                    "description": "Project assigned via Manager form selector."
                })
                frappe.log_error(message=f"Assigned {doc.custom_assign_project_user} successfully", title="Project Assignment Debug")
            except Exception:
                frappe.log_error(message=frappe.get_traceback(), title="Project Auto Assignment Error")
