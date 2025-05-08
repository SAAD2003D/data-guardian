import pandas as pd
import os

def load_dataset(file_path, file_type=None):
    """
    Loads a dataset from a CSV or Excel file.
    Tries multiple encodings for CSV files.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    if file_type is None: # Try to infer file type from extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.csv':
            file_type = 'csv'
        elif ext.lower() in ['.xls', '.xlsx']:
            file_type = 'excel'
        else:
            print(f"Error: Unknown file type for {file_path}. Please specify 'csv' or 'excel'.")
            return None

    df = None
    if file_type == 'csv':
        encodings = ['utf-8', 'ISO-8859-1', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"CSV file loaded successfully with encoding '{encoding}'.")
                break  # Stop if successfully loaded
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError with encoding '{encoding}'. Trying next...")
                continue
            except pd.errors.EmptyDataError:
                print(f"Error: The file '{file_path}' is empty.")
                return None
            except pd.errors.ParserError:
                print(f"Error: Could not parse the file '{file_path}'. Check CSV format.")
                return None # Or try with different delimiters if needed
            except Exception as e:
                print(f"An unexpected error occurred while loading CSV: {e}")
                return None
        if df is None:
            print(f"Error: Could not load CSV file '{file_path}' with any attempted encodings.")

    elif file_type == 'excel':
        try:
            # You might want to allow specifying sheet_name as a parameter
            df = pd.read_excel(file_path, sheet_name=0)
            print("Excel file loaded successfully.")
        except FileNotFoundError: # Should be caught by os.path.isfile, but good to have
            print(f"Error: Excel file not found at {file_path}")
            return None
        except pd.errors.EmptyDataError:
            print(f"Error: The Excel file (or first sheet) '{file_path}' is empty.")
            return None
        except Exception as e: # xlrd may raise other errors for corrupted files
            print(f"An unexpected error occurred while loading Excel: {e}")
            return None
    else:
        print(f"Error: Unsupported file type '{file_type}'.")
        return None

    return df