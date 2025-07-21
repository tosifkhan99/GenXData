import os


def excelWriter(df, params):
    """
    Write DataFrame to an Excel file.

    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters for to_excel method, must include 'path_or_buf', 'excel_writer', or 'output_path'

    Returns:
        None
    """
    try:
        # Support multiple path parameter names for flexibility
        path = (
            params.get("output_path")
            or params.get("path_or_buf")
            or params.get("excel_writer")
        )
        if not path:
            raise ValueError(
                "Missing path parameter (use 'output_path', 'path_or_buf', or 'excel_writer') for Excel writer"
            )

        # Ensure the file has .xlsx extension
        if not path.endswith((".xlsx", ".xls")):
            path = os.path.splitext(path)[0] + ".xlsx"

        # Create a copy of params for to_excel call, removing path-related keys
        excel_params = {
            k: v
            for k, v in params.items()
            if k not in ["output_path", "path_or_buf", "excel_writer"]
        }

        # Default to not including the index
        if "index" not in excel_params:
            excel_params["index"] = False

        # Set default sheet name if not provided
        if "sheet_name" not in excel_params:
            excel_params["sheet_name"] = "Sheet1"

        df.to_excel(path, **excel_params)

    except Exception:
        raise
