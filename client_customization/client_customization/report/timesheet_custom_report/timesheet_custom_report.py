from frappe.utils.xlsxutils import XLSXMetadata, XLSXStyleBuilder
import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = []
    
    if filters.get("employee"):
        conditions.append("ts.employee = %(employee)s")
    if filters.get("from_time"):
        conditions.append("tl.from_time >= %(from_time)s")
    if filters.get("to_time"):
        conditions.append("tl.to_time <= %(to_time)s")
        
    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = " AND " + where_clause

    query = f"""
        SELECT
            ts.name AS "timesheet",
            ts.employee AS "employee",
            ts.employee_name AS "employee_name",
            tl.task AS "task",
            p.project_name AS "project",
            t.subject AS "task_subject",
            t.description AS "task_description",
            t.status AS "task_status",
            tl.activity_type AS "activity_type",
            tl.from_time AS "from_time",
            tl.to_time AS "to_time",
            tl.hours AS "hours",
            t.custom_assigned_by AS "assigned_by",
            t.custom_assigned_start_date_ AS "assigned_start_date"
        FROM
            `tabTimesheet` ts
        INNER JOIN
            `tabTimesheet Detail` tl
            ON tl.parent = ts.name
        LEFT JOIN
            `tabTask` t
            ON t.name = tl.task
        LEFT JOIN
            `tabProject` p
            ON p.name = t.project
        WHERE
            ts.docstatus < 2
            {where_clause}
        ORDER BY
            ts.start_date DESC,
            ts.name DESC
    """
    
    columns = [
        {"fieldname": "timesheet", "label": "Timesheet", "fieldtype": "Link", "options": "Timesheet", "width": 150},
        {"fieldname": "employee", "label": "Employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 180},
        {"fieldname": "task", "label": "Task", "fieldtype": "Link", "options": "Task", "width": 150},
        {"fieldname": "project", "label": "Project", "fieldtype": "Data", "width": 150},
        {"fieldname": "task_subject", "label": "Task Subject", "fieldtype": "Data", "width": 200},
        {"fieldname": "task_description", "label": "Task Description", "fieldtype": "Text", "width": 250},
        {"fieldname": "task_status", "label": "Task Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "activity_type", "label": "Activity Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "from_time", "label": "From Time", "fieldtype": "Datetime", "width": 160},
        {"fieldname": "to_time", "label": "To Time", "fieldtype": "Datetime", "width": 160},
        {"fieldname": "hours", "label": "Hours", "fieldtype": "Float", "width": 100},
        {"fieldname": "assigned_by", "label": "Assigned By", "fieldtype": "Data", "width": 150},
        {"fieldname": "assigned_start_date", "label": "Assigned Start Date", "fieldtype": "Datetime", "width": 180}
    ]
    
    data = frappe.db.sql(query, filters, as_dict=1)
    return columns, data

def get_xlsx_styles(metadata: XLSXMetadata) -> dict:
    builder = XLSXStyleBuilder(metadata)

    datetime_style = builder.register_style({
        "num_format": "dd-mm-yyyy hh:mm:ss",
    })

    from_time_col = builder.field_index_map.get("from_time")
    to_time_col = builder.field_index_map.get("to_time")

    if from_time_col is not None:
        builder.style_column(from_time_col, datetime_style)

    if to_time_col is not None:
        builder.style_column(to_time_col, datetime_style)

    return builder.result
