frappe.provide("erpnext.timesheet");

// Globally patch moment to fix NaN Invalid Date bugs in older browsers/Safari
// when standard Frappe timesheet.js calls moment("YYYY-MM-DD HH:mm:ss") without a format string.
if (window.moment && !window._moment_patched_for_frappe) {
    const original_moment = window.moment;
    window.moment = function() {
        if (arguments.length === 1 && typeof arguments[0] === "string") {
            // Check if string is Frappe datetime format: YYYY-MM-DD HH:mm:ss
            if (arguments[0].match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$/)) {
                return original_moment(arguments[0], "YYYY-MM-DD HH:mm:ss");
            }
        }
        return original_moment.apply(this, arguments);
    };
    Object.assign(window.moment, original_moment);
    window._moment_patched_for_frappe = true;
}
const custom_timer = function (frm, row, timestamp = 0) {
	let dialog = new frappe.ui.Dialog({
		title: __("Timer"),
		fields: [
			{
				fieldtype: "Link",
				label: __("Activity Type"),
				fieldname: "activity_type",
				reqd: 1,
				options: "Activity Type",
			},
			{ fieldtype: "Link", label: __("Project"), fieldname: "project", options: "Project" },
			{ fieldtype: "Link", label: __("Task"), fieldname: "task", options: "Task" },
			{ fieldtype: "Float", label: __("Expected Hrs"), fieldname: "expected_hours" },
			{ fieldtype: "Section Break" },
			{ fieldtype: "HTML", fieldname: "timer_html" },
		],
	});
	if (row) {
		dialog.set_values({
			activity_type: row.activity_type,
			project: row.project,
			task: row.task,
			expected_hours: row.expected_hours,
		});
	} else {
		dialog.set_values({
			project: frm.doc.parent_project,
		});
	}
	dialog.get_field("timer_html").$wrapper.append(get_timer_html());

	function get_timer_html() {
		return `
			<div class="stopwatch">
				<span class="hours">00</span>
				<span class="colon">:</span>
				<span class="minutes">00</span>
				<span class="colon">:</span>
				<span class="seconds">00</span>
			</div>
			<div class="playpause text-center">
				<button class= "btn btn-primary btn-start">${__("Start")}</button>
				<button class= "btn btn-primary btn-pause" style="display:none; margin-right: 5px;">${__("Pause")}</button>
				<button class= "btn btn-primary btn-resume" style="display:none; margin-right: 5px;">${__("Resume")}</button>
				<button class= "btn btn-primary btn-complete" style="display:none;">${__("Complete")}</button>
			</div>
		`;
	}

	custom_control_timer(frm, dialog, row, timestamp);
	dialog.show();

	dialog.get_field("task").get_query = function () {
		let project = dialog.get_value("project");
		return {
			query: "client_customization.queries.get_project_tasks",
			filters: {
				project: project,
			},
		};
	};

	dialog.get_field("project").df.on_change = () => {
		let project = dialog.get_value("project");
		let task_field = dialog.get_field("task");
		task_field.set_value("");
		task_field.get_query = function () {
			return {
				query: "client_customization.queries.get_project_tasks",
				filters: {
					project: project,
				},
			};
		};
		task_field.refresh();
	};
};

const custom_control_timer = function (frm, dialog, row, timestamp = 0) {
	var $btn_start = dialog.$wrapper.find(".playpause .btn-start");
	var $btn_pause = dialog.$wrapper.find(".playpause .btn-pause");
	var $btn_resume = dialog.$wrapper.find(".playpause .btn-resume");
	var $btn_complete = dialog.$wrapper.find(".playpause .btn-complete");
	var interval = null;
	var currentIncrement = timestamp;
	var initialized = row ? true : false;
	var clicked = false;
	var flag = true; // Alert only once
	
	dialog.onhide = function() {
		if (interval) clearInterval(interval);
	};
	
	// If row with not completed status, initialize timer with the time elapsed on click of 'Start Timer'.
	if (row) {
		initialized = true;
		$btn_start.hide();
		if (row.custom_is_paused) {
			$btn_pause.hide();
			$btn_resume.show();
			$btn_complete.show();
			updateStopwatch(currentIncrement); // Just show the time without starting interval
		} else {
			$btn_pause.show();
			$btn_resume.hide();
			$btn_complete.show();
			initializeTimer();
		}
	}

	if (!initialized) {
		$btn_pause.hide();
		$btn_resume.hide();
		$btn_complete.hide();
	}

	$btn_start.click(function (e) {
		if (!initialized) {
			// New activity if no activities found
			var args = dialog.get_values();
			if (!args) return;
			if (
				frm.doc.time_logs.length == 1 &&
				!frm.doc.time_logs[0].activity_type &&
				!frm.doc.time_logs[0].from_time
			) {
				frm.doc.time_logs = [];
			}
			row = frappe.model.add_child(frm.doc, "Timesheet Detail", "time_logs");
			row.activity_type = args.activity_type;
			row.from_time = frappe.datetime.get_datetime_as_string();
			row.project = args.project;
			row.task = args.task;
			row.expected_hours = args.expected_hours;
			row.completed = 0;
			let d = moment(row.from_time, "YYYY-MM-DD HH:mm:ss");
			if (row.expected_hours) {
				d.add(row.expected_hours, "hours");
				row.to_time = frappe.datetime.get_datetime_as_string(d);
			}
			frm.refresh_field("time_logs");
			frm.save();
		}

		if (clicked) {
			e.preventDefault();
			return false;
		}

		if (!initialized) {
			initialized = true;
			$btn_start.hide();
			$btn_pause.show();
			$btn_complete.show();
			initializeTimer();
		}
	});

	$btn_pause.click(function () {
		$btn_start.hide();
		$btn_pause.hide();
		$btn_resume.show();
		$btn_complete.show();
		clearInterval(interval);
		
		if (row) {
			var grid_row = frm.fields_dict["time_logs"].grid.get_row(row.idx - 1);
			var args = dialog.get_values();
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_is_paused", 1);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_pause_start_time", frappe.datetime.now_datetime());
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "activity_type", args.activity_type);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "project", args.project);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "task", args.task);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "expected_hours", args.expected_hours);
			frm.save();
		}
	});

	$btn_resume.click(function () {
		$btn_start.hide();
		$btn_pause.show();
		$btn_resume.hide();
		$btn_complete.show();
		initializeTimer();
		
		if (row) {
			var grid_row = frm.fields_dict["time_logs"].grid.get_row(row.idx - 1);
			var args = dialog.get_values();
			let new_from_time = moment(frappe.datetime.now_datetime(), "YYYY-MM-DD HH:mm:ss").subtract(currentIncrement, "seconds").format("YYYY-MM-DD HH:mm:ss");
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "from_time", new_from_time);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_is_paused", 0);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_pause_start_time", null);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "activity_type", args.activity_type);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "project", args.project);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "task", args.task);
			frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "expected_hours", args.expected_hours);
			frm.save();
		}
	});

	// Stop the timer and update the time logged by the timer on click of 'Complete' button
	$btn_complete.click(function () {
		var grid_row = frm.fields_dict["time_logs"].grid.get_row(row.idx - 1);
		var args = dialog.get_values();
		
		let new_from_time = moment(frappe.datetime.now_datetime(), "YYYY-MM-DD HH:mm:ss").subtract(currentIncrement, "seconds").format("YYYY-MM-DD HH:mm:ss");
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "from_time", new_from_time);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "completed", 1);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_is_paused", 0);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "custom_pause_start_time", null);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "activity_type", args.activity_type);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "project", args.project);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "task", args.task);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "expected_hours", args.expected_hours);
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "to_time", frappe.datetime.get_datetime_as_string());
		
		// Overwrite the buggy Frappe calculation that produces NaN/0 in Safari
		frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "hours", currentIncrement / 3600);
		
		frm.save();
		reset();
		dialog.hide();
	});

	function initializeTimer() {
		interval = setInterval(function () {
			var current = setCurrentIncrement();
			updateStopwatch(current);
		}, 1000);
	}

	function updateStopwatch(increment) {
		var hours = Math.floor(increment / 3600);
		var minutes = Math.floor((increment - hours * 3600) / 60);
		var seconds = increment - hours * 3600 - minutes * 60;

		if (hours > 99999) reset();
		if (dialog && dialog.get_value("expected_hours") > 0) {
			if (flag && currentIncrement >= dialog.get_value("expected_hours") * 3600) {
				frappe.utils.play_sound("alert");
				frappe.msgprint(__("Timer exceeded the given hours."));
				flag = false;
			}
		}
		dialog.$wrapper.find(".hours").text(hours < 10 ? "0" + hours.toString() : hours.toString());
		dialog.$wrapper.find(".minutes").text(minutes < 10 ? "0" + minutes.toString() : minutes.toString());
		dialog.$wrapper.find(".seconds").text(seconds < 10 ? "0" + seconds.toString() : seconds.toString());
	}

	function setCurrentIncrement() {
		currentIncrement += 1;
		return currentIncrement;
	}

	function reset() {
		currentIncrement = 0;
		initialized = false;
		clearInterval(interval);
		dialog.$wrapper.find(".hours").text("00");
		dialog.$wrapper.find(".minutes").text("00");
		dialog.$wrapper.find(".seconds").text("00");
		$btn_pause.hide();
		$btn_resume.hide();
		$btn_complete.hide();
		$btn_start.show();
	}
};

// Lock down the custom timer functions so Frappe's standard timer.js cannot overwrite them!
// Lock down the custom timer functions so Frappe's standard timer.js cannot overwrite them!
if (!Object.getOwnPropertyDescriptor(erpnext.timesheet, 'timer') || Object.getOwnPropertyDescriptor(erpnext.timesheet, 'timer').configurable) {
    Object.defineProperty(erpnext.timesheet, 'timer', {
        get: function() { return custom_timer; },
        set: function(v) { console.log("Blocked Frappe from overwriting custom timer!"); },
        configurable: false
    });
}
if (!Object.getOwnPropertyDescriptor(erpnext.timesheet, 'control_timer') || Object.getOwnPropertyDescriptor(erpnext.timesheet, 'control_timer').configurable) {
    Object.defineProperty(erpnext.timesheet, 'control_timer', {
        get: function() { return custom_control_timer; },
        set: function(v) { console.log("Blocked Frappe from overwriting custom control_timer!"); },
        configurable: false
    });
}

frappe.ui.form.on("Timesheet", {
    refresh: function (frm) {
        setTimeout(function() {
            if (frm.doc.docstatus < 1) {
                let button_label = __("Start Timer");
                $.each(frm.doc.time_logs || [], function (i, row) {
                    if (row.from_time <= frappe.datetime.now_datetime() && !row.completed) {
                        button_label = __("Resume Timer");
                    }
                });

                frm.remove_custom_button(__("Start Timer"));
                frm.remove_custom_button(__("Resume Timer"));

                frm.add_custom_button(button_label, function () {
                    var target_row = null;
                    let rows = frm.doc.time_logs || [];

                    for (let i = rows.length - 1; i >= 0; i--) {
                        if (rows[i].custom_is_paused && !rows[i].completed) {
                            target_row = rows[i];
                            break;
                        }
                    }

                    if (!target_row) {
                        for (let i = rows.length - 1; i >= 0; i--) {
                            if (rows[i].from_time <= frappe.datetime.now_datetime() && !rows[i].completed) {
                                target_row = rows[i];
                                break;
                            }
                        }
                    }

                    if (!target_row) {
                        for (let i = rows.length - 1; i >= 0; i--) {
                            if (rows[i].activity_type && !rows[i].from_time) {
                                target_row = rows[i];
                                break;
                            }
                        }
                    }

                    if (target_row) {
                        if (target_row.custom_is_paused) {
                            let timestamp = 0;
                            if (target_row.custom_pause_start_time) {
                                timestamp = moment(target_row.custom_pause_start_time, "YYYY-MM-DD HH:mm:ss").diff(moment(target_row.from_time, "YYYY-MM-DD HH:mm:ss"), "seconds");
                            } else {
                                timestamp = moment(frappe.datetime.now_datetime(), "YYYY-MM-DD HH:mm:ss").diff(moment(target_row.from_time, "YYYY-MM-DD HH:mm:ss"), "seconds");
                            }
                            custom_timer(frm, target_row, timestamp);
                        } else if (!target_row.from_time) {
                            custom_timer(frm, target_row);
                            frappe.model.set_value(target_row.doctype, target_row.name, "from_time", frappe.datetime.now_datetime());
                            frm.refresh_fields("time_logs");
                            frm.save();
                        } else {
                            let timestamp = moment(frappe.datetime.now_datetime(), "YYYY-MM-DD HH:mm:ss").diff(moment(target_row.from_time, "YYYY-MM-DD HH:mm:ss"), "seconds");
                            custom_timer(frm, target_row, timestamp);
                        }
                    } else {
                        custom_timer(frm);
                    }
                }).addClass("btn-primary");
            }
        }, 100);
    }
});
