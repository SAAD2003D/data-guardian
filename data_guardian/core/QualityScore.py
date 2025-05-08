import pandas as pd
# from core.data_issue import DataIssue # Not strictly needed if only consuming issue list

class QualityScore:
    def __init__(self, dataframe, issues):
        self.dataframe = dataframe
        self.issues = issues # List of DataIssue objects
        self.num_rows, self.num_cols = dataframe.shape if dataframe is not None else (0,0)
        self.total_cells = self.num_rows * self.num_cols if dataframe is not None else 0

        self.completeness_score = 0.0  # 0-100
        self.consistency_score = 0.0   # 0-100 (e.g., type consistency, format consistency)
        self.uniqueness_score = 0.0    # 0-100 (e.g., lack of unwanted duplicates)
        self.validity_score = 0.0      # 0-100 (e.g., values conform to expected patterns/ranges, few outliers)
        # Accuracy is very hard to measure without a ground truth, so we use Validity as a proxy
        self.overall_score = 0.0       # 0-100

    def _calculate_completeness(self):
        if self.total_cells == 0: return 0.0

        total_missing_cells_count = 0
        missing_value_issues = [iss for iss in self.issues if iss.issue_type == "MissingValue" or iss.issue_type == "SuspiciousValue"]

        for issue in missing_value_issues:
            # Assuming percentage_affected is % of rows in that column, need to scale to whole dataset
            # A more direct way: sum up all pd.isnull().sum().sum() from the raw dataframe
            # and add counts from suspicious strings.
            # For now, we'll approximate based on issue counts and their affected percentages if DataIssue is well-populated.
            # This part needs careful implementation based on how DataIssue.percentage_affected is defined.
            # Let's use a simpler approach: count total NaN cells.
            pass # This logic will be simplified

        if self.dataframe is None: return 0.0
        
        # Standard NaN values
        nan_cells = self.dataframe.isnull().sum().sum()
        
        # Custom null-like strings (need to count them if they weren't converted to NaN at load)
        # This is tricky if they are still strings. For scoring, it's better if they are NaNs.
        # We'll primarily base this on `MissingValue` issues for `NaNs`.
        suspicious_value_cells = 0
        for issue in [iss for iss in self.issues if iss.issue_type == "SuspiciousValue"]:
            # Assuming affected_rows_count is populated in DataIssue
             suspicious_value_cells += issue.affected_rows_count

        total_problematic_cells = nan_cells + suspicious_value_cells
        
        percentage_missing = (total_problematic_cells / self.total_cells) * 100 if self.total_cells > 0 else 0
        self.completeness_score = max(0, 100 - percentage_missing) # Higher is better
        return self.completeness_score


    def _calculate_uniqueness(self):
        # Primarily based on duplicated rows
        # Consider also if entire columns are duplicates of each other (more advanced)
        duplicated_row_issues = [iss for iss in self.issues if iss.issue_type == "DuplicatedRows"]
        penalty = 0
        if duplicated_row_issues and self.num_rows > 0:
            # Assuming the 'percentage_affected' for DuplicatedRows is % of rows that are duplicates
            # Example: if 10% of rows are duplicates, score is 90.
            total_duplicate_percentage = sum(iss.percentage_affected for iss in duplicated_row_issues)
            penalty = total_duplicate_percentage

        self.uniqueness_score = max(0, 100 - penalty)
        return self.uniqueness_score

    def _calculate_consistency(self):
        # Based on InconsistentDataType, potentially string pattern issues (mixed casing)
        # This is a more abstract score. We can penalize based on number of columns affected.
        if self.num_cols == 0: return 100.0

        inconsistent_type_issues = [iss for iss in self.issues if iss.issue_type == "InconsistentDataType"]
        # whitespace_issues = [iss for iss in self.issues if iss.issue_type == "WhiteSpace"] # Can contribute

        # Penalize per column with inconsistent types.
        # Max penalty if all columns have type issues.
        # Each column with type issues reduces score by (100 / num_cols).
        num_cols_with_type_issues = len(set(iss.column_name for iss in inconsistent_type_issues if iss.column_name))
        
        penalty = (num_cols_with_type_issues / self.num_cols) * 100 if self.num_cols > 0 else 0
        
        # Further refine with other consistency issues if needed
        self.consistency_score = max(0, 100 - penalty)
        return self.consistency_score

    def _calculate_validity(self):
        # Based on Outliers, Constant Columns (if undesirable), maybe other pattern violations
        if self.num_cols == 0: return 100.0

        outlier_issues = [iss for iss in self.issues if "Outlier" in iss.issue_type]
        constant_col_issues = [iss for iss in self.issues if iss.issue_type == "ConstantColumn"]

        # Penalty for outliers: more outliers or more columns with outliers = lower score
        # Penalty for constant columns: might be valid, might not. For now, a small penalty.
        
        outlier_penalty_factor = 5 # Penalty per column with outliers
        constant_penalty_factor = 2 # Penalty per constant column

        num_cols_with_outliers = len(set(iss.column_name for iss in outlier_issues if iss.column_name))
        num_constant_cols = len(constant_col_issues)

        penalty = (num_cols_with_outliers * outlier_penalty_factor) + \
                  (num_constant_cols * constant_penalty_factor)
        
        # Cap penalty at 100
        penalty = min(penalty, 100)
        
        self.validity_score = max(0, 100 - penalty)
        return self.validity_score

    def calculate_all_scores(self):
        self._calculate_completeness()
        self._calculate_uniqueness()
        self._calculate_consistency()
        self._calculate_validity()

        # Weighted average for overall score (weights can be configured)
        weights = {
            'completeness': 0.35,
            'uniqueness': 0.25,
            'consistency': 0.20,
            'validity': 0.20
        }
        self.overall_score = (self.completeness_score * weights['completeness'] +
                              self.uniqueness_score * weights['uniqueness'] +
                              self.consistency_score * weights['consistency'] +
                              self.validity_score * weights['validity'])
        self.overall_score = max(0, min(100, self.overall_score)) # Ensure it's within 0-100
        print(f"Scores: Comp={self.completeness_score:.2f}, Uniq={self.uniqueness_score:.2f}, Cons={self.consistency_score:.2f}, Valid={self.validity_score:.2f}, Overall={self.overall_score:.2f}")


    def get_summary(self):
        return (f"  Completeness Score: {self.completeness_score:.2f} / 100\n"
                f"  Uniqueness Score:   {self.uniqueness_score:.2f} / 100\n"
                f"  Consistency Score:  {self.consistency_score:.2f} / 100\n"
                f"  Validity Score:     {self.validity_score:.2f} / 100\n"
                f"  ----------------------------------\n"
                f"  Overall Quality Score: {self.overall_score:.2f} / 100")