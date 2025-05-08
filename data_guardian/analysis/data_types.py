import pandas as pd
import re # For regex


# --- This sys.path manipulation is generally discouraged. ---

# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue

def analyze_data_types(df):
    """
    Analyzes data types, focusing on:
    1. Columns Pandas inferred as 'object' that might be numeric/boolean.
    2. Columns with mixed data types that Pandas couldn't cleanly cast.
    """
    issues = []
    if df is None or df.empty:
        return issues
    
    num_rows = df.shape[0]
    if num_rows == 0: return issues

    for col_name in df.columns:
        column_series = df[col_name]
        actual_dtype = column_series.dtype

        # Check 1: Object columns that could potentially be numeric or boolean
        if actual_dtype == 'object':
            # Attempt to infer a more specific type
            try:
                # Try converting to numeric, ignoring errors to see how many convert
                numeric_converted = pd.to_numeric(column_series, errors='coerce')
                num_convertible = numeric_converted.notna().sum()
                num_non_nan_original = column_series.notna().sum()

                if num_non_nan_original > 0 and num_convertible == num_non_nan_original:
                    # All non-null values were convertible to numeric
                    description = (f"Column '{col_name}' is type 'object' but all its non-null values "
                                   f"can be converted to numeric. Consider explicit type conversion.")
                    issue = DataIssue(
                        issue_type="PotentialNumericType",
                        column_name=col_name,
                        description=description,
                        severity="Low",
                        suggested_action=f"Convert column '{col_name}' to a numeric type (e.g., int, float) if appropriate."
                    )
                    issue.set_percentage_metrics(num_rows, num_rows) # Affects the whole column interpretation
                    issues.append(issue)
                    # print(f"PotentialNumericType issue: {col_name}")
                    continue # Skip further type checks for this column if it's all numeric-like

                elif num_non_nan_original > 0 and num_convertible > 0 and num_convertible < num_non_nan_original:
                    # Mixed types: some numeric, some not, within an object column
                    num_non_convertible = num_non_nan_original - num_convertible
                    percentage_non_convertible = (num_non_convertible / num_non_nan_original) * 100
                    description = (f"Column '{col_name}' (object type) contains mixed data: "
                                   f"~{num_convertible} numeric-like values and "
                                   f"~{num_non_convertible} non-numeric string values.")
                    
                    # Get original indices of non-convertible values
                    non_convertible_mask = pd.to_numeric(column_series, errors='coerce').isna() & column_series.notna()
                    non_convertible_indices = list(df[non_convertible_mask].index)

                    issue = DataIssue(
                        issue_type="MixedDataTypeInObjectColumn",
                        column_name=col_name,
                        description=description,
                        row_indices=non_convertible_indices,
                        severity="Medium",
                        suggested_action=f"Investigate non-numeric values in '{col_name}'. Standardize or clean them if the column should be numeric, or confirm mixed type is intentional."
                    )
                    issue.set_percentage_metrics(num_non_convertible, num_non_nan_original)
                    issues.append(issue)
                    # print(f"MixedDataTypeInObjectColumn issue: {col_name}")


            except Exception as e:
                # print(f"Could not perform detailed type analysis on object column {col_name}: {e}")
                pass # Continue to next column or check

        # Add more specific type checks if needed, e.g., for date formats, boolean-like strings
        # Your original regex pattern r'^(?=.*\d)[\d\s]+$' seemed to look for strings that are numbers with spaces.
        # This is one kind of "inconsistent type" if the column is meant to be purely numeric.
        # The pd.to_numeric check above is more general.
        # If you want specific pattern violations:
        # pattern_for_numbers_with_spaces = r'^(?=.*\d)[\d\s]+$' # Example
        # if actual_dtype == 'object':
        #     non_matching_count = column_series.astype(str).str.match(pattern_for_numbers_with_spaces, na=False).eq(False).sum()
        #     if non_matching_count > 0 and non_matching_count < column_series.notna().sum(): # some match, some don't
        #         # create issue
        #         pass

    # print(f"Data type issues found: {len(issues)}")
    return issues