# data_guardian/__init__.py
__version__ = "0.1.0" # Keep in sync with pyproject.toml

from .core.DatasetProfile import DatasetProfile
from .core.DataIssue import DataIssue
from .core.QualityScore import QualityScore
from .reporting.html_reporter import HTMLReporter
from .reporting.pdf_reporter import PDFReporter

# You might also expose core analysis functions if users might want to call them directly
# from .analysis.missing_values import analyze_null_values
# ... etc.

print(f"Data Guardian Library v{__version__} loaded.") # Optional: for user awareness