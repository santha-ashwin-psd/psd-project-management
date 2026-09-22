import frappe


def project_query(user):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    # Administrator sees all Projects
    if user == "Administrator":
        return ""
        
    # Project Admin sees all Projects
    if "Project Admin" in roles:
        return ""

    # Projects Manager sees assigned Projects OR Projects they created
    if "Projects Manager" in roles:
        return f"(`tabProject`.`custom_assign_project_user` = {frappe.db.escape(user)} OR `tabProject`.`owner` = {frappe.db.escape(user)})"

    # Projects User sees only Projects where they are assigned to a Task
    # (either directly as custom_assign_employee or via custom_employee_group)
    if "Projects User" in roles:
        return f"""
            `tabProject`.`name` IN (
                SELECT `project`
                FROM `tabTask`
                WHERE (
                    `custom_assign_employee` IN (
                        SELECT `name` FROM `tabEmployee` WHERE `user_id` = {frappe.db.escape(user)}
                    )
                    OR
                    (
                        (IFNULL(`custom_assign_employee`, '') = '')
                        AND
                        `custom_employee_group` IN (
                            SELECT `parent` FROM `tabEmployee Group Table` WHERE `employee` IN (
                                SELECT `name` FROM `tabEmployee` WHERE `user_id` = {frappe.db.escape(user)}
                            )
                        )
                    )
                )
            )
        """

    # Everyone else sees no Projects
    return "1=0"


#def task_query(user):
    #if not user:
     #   user = frappe.session.user

    ## Restrict only Projects Users
    #if "Projects User" in frappe.get_roles(user):
     #   return f"`tabTask`.`owner` = {frappe.db.escape(user)}"

    # #Everyone else: no custom restriction
   # return ""


#def timesheet_query(user):
   # if not user:
    #    user = frappe.session.user

    ## Restrict only Projects Users
    #if "Projects User" in frappe.get_roles(user):
     #   return f"`tabTimesheet`.`owner` = {frappe.db.escape(user)}"

    ## Everyone else: no custom restriction
    #return ""











def task_query(user):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if user == "Administrator" or "System Manager" in roles or "Project Admin" in roles:
        return ""

    # Projects Manager can see Tasks of their Projects
    if "Projects Manager" in roles:
        return f"""
            (
                `tabTask`.`project` IN (
                    SELECT `name`
                    FROM `tabProject`
                    WHERE `custom_assign_project_user` = {frappe.db.escape(user)} OR `owner` = {frappe.db.escape(user)}
                )
                OR `tabTask`.`owner` = {frappe.db.escape(user)}
            )
        """

    # Employee + Projects User:
    # Can see Tasks they created OR Tasks assigned to them directly OR via Employee Group.
    if "Projects User" in roles:
        return f"""
            (
                `tabTask`.`owner` = {frappe.db.escape(user)}
                OR
                `tabTask`.`custom_assign_employee` IN (
                    SELECT `name`
                    FROM `tabEmployee`
                    WHERE `user_id` = {frappe.db.escape(user)}
                )
                OR
                (
                    (IFNULL(`tabTask`.`custom_assign_employee`, '') = '')
                    AND
                    `tabTask`.`custom_employee_group` IN (
                        SELECT `parent`
                        FROM `tabEmployee Group Table`
                        WHERE `employee` IN (
                            SELECT `name`
                            FROM `tabEmployee`
                            WHERE `user_id` = {frappe.db.escape(user)}
                        )
                    )
                )
            )
        """

    return "1=0"


def timesheet_query(user):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if user == "Administrator" or "System Manager" in roles or "Project Admin" in roles:
        return ""

    # Projects Manager can see Timesheets of their Projects
    if "Projects Manager" in roles:
        return f"""
            (
                `tabTimesheet`.`name` IN (
                    SELECT `parent`
                    FROM `tabTimesheet Detail`
                    WHERE `project` IN (
                        SELECT `name`
                        FROM `tabProject`
                        WHERE `custom_assign_project_user` = {frappe.db.escape(user)} OR `owner` = {frappe.db.escape(user)}
                    )
                )
                OR
                `tabTimesheet`.`owner` = {frappe.db.escape(user)}
            )
        """

    # Employee + Projects User:
    # Can see Timesheets they created OR Timesheets belonging to them.
    if "Projects User" in roles:
        return f"""
            (
                `tabTimesheet`.`owner` = {frappe.db.escape(user)}
                OR
                `tabTimesheet`.`employee` IN (
                    SELECT `name`
                    FROM `tabEmployee`
                    WHERE `user_id` = {frappe.db.escape(user)}
                )
            )
        """

    return "1=0"
