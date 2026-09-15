import frappe


def project_query(user):
    if not user:
        user = frappe.session.user

    # Administrator sees all Projects
    if user == "Administrator":
        return ""

    # Projects Manager sees all Projects
    if "Projects Manager" in frappe.get_roles(user):
        return ""

    # Projects User sees only assigned Projects
    if "Projects User" in frappe.get_roles(user):
        return f"`tabProject`.`custom_assign_project_user` = {frappe.db.escape(user)}"

    # Everyone else sees no Projects
    return "1=0"


def task_query(user):
    if not user:
        user = frappe.session.user

    # Restrict only Projects Users
    if "Projects User" in frappe.get_roles(user):
        return f"`tabTask`.`owner` = {frappe.db.escape(user)}"

    # Everyone else: no custom restriction
    return ""


def timesheet_query(user):
    if not user:
        user = frappe.session.user

    # Restrict only Projects Users
    if "Projects User" in frappe.get_roles(user):
        return f"`tabTimesheet`.`owner` = {frappe.db.escape(user)}"

    # Everyone else: no custom restriction
    return ""
