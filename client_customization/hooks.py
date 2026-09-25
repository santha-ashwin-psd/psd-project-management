app_name = "client_customization"
app_title = "Client Customization"
app_publisher = "PS Digi"
app_description = "Customizations for client ERPNext requirements"
app_email = "kishoreps362@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "client_customization",
# 		"logo": "/assets/client_customization/logo.png",
# 		"title": "Client Customization",
# 		"route": "/client_customization",
# 		"has_permission": "client_customization.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/client_customization/css/client_customization.css"
# app_include_js = "/assets/client_customization/js/custom_timer_v2.js"

# include js, css files in header of web template
# web_include_css = "/assets/client_customization/css/client_customization.css"
# web_include_js = "/assets/client_customization/js/client_customization.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "client_customization/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "client_customization/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "client_customization.utils.jinja_methods",
# 	"filters": "client_customization.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "client_customization.install.before_install"
# after_install = "client_customization.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "client_customization.uninstall.before_uninstall"
# after_uninstall = "client_customization.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "client_customization.utils.before_app_install"
# after_app_install = "client_customization.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "client_customization.utils.before_app_uninstall"
# after_app_uninstall = "client_customization.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "client_customization.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "client_customization.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["client_customization.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Task": {
		"after_insert": "client_customization.api.task_after_insert"
	},
	"Project": {
		"on_update": "client_customization.api.project_after_save"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"client_customization.tasks.all"
# 	],
# 	"daily": [
# 		"client_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"client_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"client_customization.tasks.weekly"
# 	],
# 	"monthly": [
# 		"client_customization.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "client_customization.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "client_customization.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "client_customization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "client_customization.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["client_customization.utils.before_request"]
# after_request = ["client_customization.utils.after_request"]

# Job Events
# ----------
# before_job = ["client_customization.utils.before_job"]
# after_job = ["client_customization.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"client_customization.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
                "Project-custom_assign_project_user",
                "Task-custom_activity_type",
                "Task-custom_assign_employee",
                "Task-custom_employee_group",
                "Task-custom_assigned_by",
                "Task-custom_assigned_start_date_",
                "Timesheet Detail-custom_is_paused",
                "Timesheet Detail-custom_pause_start_time"
            ]]
        ]
    },
    {
        "dt": "Client Script",
        "filters": [
            ["name", "in", [
                "Project Filter on TASK record",
                "Filter The User",
                "Confirm Employee Assignment",
                "Employee Group Filter",
                "Timesheet Custom Timer"
            ]]
        ]
    },
    {
        "dt": "Server Script",
        "filters": [
            ["name", "in", [
                "Validate Project Assignment Role",
                "Create Timesheet From Task",
                "Employee Group Filter",
                "Project Auto Assign Manager",
                "Project Auto Create ToDo"
            ]]
        ]
    },
    {
        "dt": "Custom DocPerm",
        "filters": [
            ["parent", "in", ["Employee Group", "Project", "User"]]
        ]
    },
    {
        "dt": "Email Template",
        "filters": [
            ["name", "in", ["Task Assignment"]]
        ]
    }
]
permission_query_conditions = {
    "Project": "client_customization.permissions.project_query",
    "Task": "client_customization.permissions.task_query",
    "Timesheet": "client_customization.permissions.timesheet_query"
}


