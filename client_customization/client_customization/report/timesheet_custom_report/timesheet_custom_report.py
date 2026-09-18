from frappe.utils.xlsxutils import XLSXMetadata, XLSXStyleBuilder


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
