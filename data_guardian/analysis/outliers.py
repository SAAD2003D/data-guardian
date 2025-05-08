import pandas as pd
import numpy as np


# --- This sys.path manipulation is generally discouraged. ---

# --- End of discouraged sys.path manipulation ---
from ..core.DataIssue import DataIssue

def find_numerical_outliers(df, method='iqr', threshold=1.5, columns=None):
    """
    Finds numerical outliers in specified columns or all numerical columns.
    Methods: 'iqr' or 'zscore'.
    Threshold: IQR multiplier or Z-score threshold.
    """
    issues = []
    if df is None or df.empty:
        return issues

    if columns is None:
        # Automatically select numerical columns
        numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
    else:
        numerical_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

    if not numerical_cols:
        # print("No numerical columns found or specified for outlier detection.")
        return issues

    num_rows = df.shape[0]

    for col_name in numerical_cols:
        series = df[col_name].dropna() # Work with non-null values
        if series.empty:
            continue

        outlier_indices = []
        description_prefix = ""

        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outliers_mask = (series < lower_bound) | (series > upper_bound)
            outlier_indices = list(series[outliers_mask].index)
            description_prefix = f"IQR method (multiplier {threshold})"
            
        elif method == 'zscore':
            mean = series.mean()
            std = series.std()
            if std == 0: # Avoid division by zero if all values are the same
                continue 
            
            z_scores = np.abs((series - mean) / std)
            outliers_mask = z_scores > threshold
            outlier_indices = list(series[outliers_mask].index)
            description_prefix = f"Z-score method (threshold {threshold})"
        else:
            # print(f"Unknown outlier detection method: {method} for column {col_name}")
            continue

        if outlier_indices:
            outlier_count = len(outlier_indices)
            percentage = (outlier_count / num_rows) * 100 # Percentage of total rows
            
            # Get a few sample outlier values
            sample_outliers = df.loc[outlier_indices, col_name].head(3).tolist()
            
            description = (f"{outlier_count} numerical outlier(s) detected in column '{col_name}' using {description_prefix}. "
                           f"Examples: {sample_outliers}{'...' if outlier_count > 3 else ''}.")
            issue = DataIssue(
                issue_type="NumericalOutlier",
                column_name=col_name,
                description=description,
                row_indices=outlier_indices,
                value_found=sample_outliers, # Store sample outliers
                severity="Medium" if percentage < 5 else "High",
                suggested_action=f"Investigate outliers in '{col_name}'. They may be errors or genuinely extreme values. Consider transformation, capping, or removal if they are errors."
            )
            issue.set_percentage_metrics(outlier_count, num_rows)
            issues.append(issue)
            # print(f"NumericalOutlier issue: {col_name}, Count: {outlier_count}, Method: {method}")

    # print(f"Numerical outlier issues found: {len(issues)}")
    return issues

def find_categorical_outliers(df, threshold=0.01, columns=None):
    """
    Finds categorical outliers (very rare categories) in specified or all categorical/object columns.
    Threshold: categories making up less than this percentage of non-null values are considered outliers.
    """
    issues = []
    if df is None or df.empty:
        return issues

    if columns is None:
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    else:
        categorical_cols = [col for col in columns if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])]
    
    if not categorical_cols:
        # print("No categorical columns found or specified for outlier detection.")
        return issues

    num_rows = df.shape[0]

    for col_name in categorical_cols:
        series = df[col_name].dropna()
        if series.empty:
            continue

        value_counts = series.value_counts(normalize=True) # Get proportions
        rare_categories = value_counts[value_counts < threshold]

        if not rare_categories.empty:
            rare_category_names = rare_categories.index.tolist()
            
            # Get original indices of rows with these rare categories
            rare_mask = series.isin(rare_category_names)
            rare_indices = list(series[rare_mask].index)
            rare_count = len(rare_indices)
            percentage = (rare_count / num_rows) * 100

            description = (f"{rare_count} instance(s) of rare categories (each < {threshold*100:.2f}% of observations) "
                           f"found in column '{col_name}'. Examples: {rare_category_names[:3]}"
                           f"{'...' if len(rare_category_names) > 3 else ''}.")
            
            issue = DataIssue(
                issue_type="CategoricalOutlier", # Or "RareCategory"
                column_name=col_name,
                description=description,
                row_indices=rare_indices,
                value_found=rare_category_names, # Store the rare category names
                severity="Low" if threshold > 0.01 else "Medium", # Higher threshold = more things are "rare"
                suggested_action=f"Review rare categories in '{col_name}'. They might be typos, special cases, or require grouping into an 'Other' category."
            )
            issue.set_percentage_metrics(rare_count, len(series)) # % of non-null values in that column
            issues.append(issue)
            # print(f"CategoricalOutlier issue: {col_name}, Rare categories: {rare_category_names}")

    # print(f"Categorical outlier issues found: {len(issues)}")
    return issues