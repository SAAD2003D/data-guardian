class DataIssue:
    def __init__(self, issue_type, column_name=None, description="", row_indices=None, value_found=None, severity="Medium", suggested_action=""):
        self.issue_type = issue_type  # e.g., "MissingValue", "DataTypeError", "Outlier"
        self.column_name = column_name  # Name of the affected column, if applicable
        self.description = description  # Human-readable description of the issue
        self.row_indices = row_indices if row_indices is not None else [] # List of row indices where issue occurs
        self.value_found = value_found # The specific problematic value, if applicable
        self.severity = severity  # e.g., "Low", "Medium", "High"
        self.suggested_action = suggested_action # A brief suggestion for fixing

        # Percentage related fields (can be calculated by analysis functions)
        self.affected_rows_count = 0
        self.total_rows_in_column = 0 # or total rows in dataset for row-level issues
        self.percentage_affected = 0.0

    def set_percentage_metrics(self, affected_count, total_count):
        self.affected_rows_count = affected_count
        self.total_rows_in_column = total_count
        if total_count > 0:
            self.percentage_affected = (affected_count / total_count) * 100
        else:
            self.percentage_affected = 0.0

    def __str__(self):
        col_info = f" in column '{self.column_name}'" if self.column_name else ""
        percent_info = f" ({self.percentage_affected:.2f}% affected)" if self.percentage_affected > 0 else ""
        return (f"Issue Type: {self.issue_type}{col_info}\n"
                f"  Description: {self.description}\n"
                f"  Severity: {self.severity}{percent_info}\n"
                f"  Affected Rows: {len(self.row_indices) if self.row_indices else 'N/A (or all)'}")

    # Getter methods (if you want to keep attributes "private-by-convention")
    def get_issue_type(self):
        return self.issue_type

    def get_column_name(self):
        return self.column_name

    def get_description(self):
        return self.description

    def get_percentage_affected(self):
        return self.percentage_affected

    def get_severity(self):
        return self.severity

    def get_suggested_action(self):
        return self.suggested_action

    def get_row_indices(self):
        return self.row_indices