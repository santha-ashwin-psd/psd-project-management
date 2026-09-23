frappe.query_reports["Timesheet Custom Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "from_time",
			"label": __("From Time"),
			"fieldtype": "Datetime"
		},
		{
			"fieldname": "to_time",
			"label": __("To Time"),
			"fieldtype": "Datetime"
		}
	]
};
