import pandas as pd

# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue

def detect_duplicated_rows(df):
    """
    Detects fully duplicated rows in the DataFrame.
    """
    issues = []
    if df is None or df.empty:
        return issues
        
    num_rows = df.shape[0]
    if num_rows == 0: return issues

    # Get boolean Series indicating whether each row is a duplicate of a previous one
    duplicate_mask = df.duplicated(keep='first') # keep='first' marks subsequent occurrences as True
    duplicated_count = duplicate_mask.sum()

    if duplicated_count > 0:
        percentage = (duplicated_count / num_rows) * 100
        description = f"{duplicated_count} fully duplicated row(s) detected in the dataset."
        
        # Get indices of duplicated rows (the ones marked True by .duplicated())
        duplicated_indices = list(df[duplicate_mask].index)

        issue = DataIssue(
            issue_type="DuplicatedRows",
            column_name=None, # This is a row-level issue, not specific to a column
            description=description,
            row_indices=duplicated_indices, # Store indices of duplicates
            severity="High" if percentage > 10 else "Medium",
            suggested_action="Review and remove duplicated rows to ensure data integrity and prevent skewed analysis."
        )
        issue.set_percentage_metrics(duplicated_count, num_rows)
        issues.append(issue)
        # print(f"DuplicatedRows issue: Count: {duplicated_count}, %: {percentage:.2f}")

    # print(f"Duplicated row issues found: {len(issues)}")
    return issues

# Example test (remove from final library code, use in a test file)
# if __name__ == '__main__':
#     test_df = pd.DataFrame({
#         "name": ["saad", "othmane", "ilias", "saad", "othmane", "john"],
#         "age": [18, 20, 31, 18, 20, 25],
#         "city": ["A", "B", "C", "A", "B", "D"]
#     })
#     print("Test DataFrame:")
#     print(test_df)
#     found_issues = detect_duplicated_rows(test_df)
#     for iss in found_issues:
#         print(iss)
#         print(f"  Indices: {iss.row_indices}")