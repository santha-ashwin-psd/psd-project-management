from frappe.utils.xlsxutils import XLSXMetadata, XLSXStyleBuilder
import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    # Ensure all filter keys exist to avoid KeyError when frappe.db.sql formats the query
    filters.setdefault("employee", "")
    filters.setdefault("from_time", "")
    filters.setdefault("to_time", "")

    query = """
    SELECT
        ts.name AS "timesheet",
        ts.employee AS "employee",
        ts.employee_name AS "employee_name",
        tl.task AS "task",
        p.project_name As "project",
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
        AND (%(employee)s = '' OR ts.employee = %(employee)s)
        AND (%(from_time)s = '' OR tl.from_time >= %(from_time)s)
        AND (%(to_time)s = '' OR tl.to_time <= %(to_time)s)
    ORDER BY
        ts.start_date DESC,
        ts.name DESC;
    """

    data = frappe.db.sql(query, filters, as_dict=1)
    
    columns = [
        "Timesheet:Link/Timesheet:150",
        "Employee:Link/Employee:150",
        "Employee Name:Data:180",
        "Task:Link/Task:150",
        "Project:Data:150",
        "Task Subject:Data:200",
        "Task Description:Text:250",
        "Task Status:Data:120",
        "Activity Type:Data:150",
        "From Time:Datetime:160",
        "To Time:Datetime:160",
        "Hours:Float:100",
        "Assigned By:Data:150",
        "Assigned Start Date:Datetime:180"
    ]

    return columns, data

def get_xlsx_styles(metadata: XLSXMetadata) -> dict:
    builder = XLSXStyleBuilder(metadata)

    datetime_style = builder.register_style({
        "num_format": "dd-mm-yyyy hh:mm:ss",
    })

    from_time_col = builder.field_index_map.get("From Time")
    to_time_col = builder.field_index_map.get("To Time")

    if from_time_col is not None:
        builder.style_column(from_time_col, datetime_style)

    if to_time_col is not None:
        builder.style_column(to_time_col, datetime_style)

    return builder.result
