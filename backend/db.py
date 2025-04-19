# backend/db.py
import json
import os

# Make path relative to this script file
SCRIPT_DIR = os.path.dirname(__file__)
# Assume reports.json is in the parent directory (project root)
REPORTS_PATH = os.path.join(SCRIPT_DIR, "..", "reports.json")
# Or if you want it inside backend:
# REPORTS_PATH = os.path.join(SCRIPT_DIR, "reports.json")
print(f"--- DB: Using reports path: {REPORTS_PATH} ---") # Added print

def save_report(report):
    data = []
    print(f"--- DB: Attempting to save report: {report.get('hash_id', 'N/A')} ---") # Added print
    try:
        if os.path.exists(REPORTS_PATH):
            print(f"--- DB: File exists, attempting to read {REPORTS_PATH} ---") # Added print
            try:
                with open(REPORTS_PATH, "r") as file:
                    content = file.read()
                    if content.strip(): # Check if file is not empty
                         print(f"--- DB: File content length: {len(content)} ---") # Added print
                         data = json.loads(content) # Use loads for string content
                         if not isinstance(data, list):
                             print("!!! DB ERROR: reports.json does not contain a JSON list!")
                             # Decide how to handle: overwrite? raise error?
                             # For now, let's reset to empty list and log warning
                             print("!!! DB WARNING: Resetting data to empty list.")
                             data = []
                    else:
                        print("--- DB: File is empty, initializing data as list. ---")
                        data = []
            except json.JSONDecodeError as e:
                print(f"!!! DB ERROR: Failed to decode JSON from {REPORTS_PATH}: {e}")
                # Handle corrupted JSON file - maybe backup and start fresh?
                # For now, raise error to stop the process
                raise Exception(f"Corrupted reports.json file: {e}") from e
            except Exception as e:
                print(f"!!! DB ERROR: Failed to read {REPORTS_PATH}: {e}")
                raise # Re-raise other read errors
        else:
            print(f"--- DB: File {REPORTS_PATH} does not exist, initializing data as list. ---") # Added print
            data = [] # Initialize data as empty list if file doesn't exist

        # Ensure data is a list before appending
        if not isinstance(data, list):
             print(f"!!! DB ERROR: Data read from file is not a list (Type: {type(data)}). Resetting.")
             data = [] # Fallback

        data.append(report)
        print(f"--- DB: Appended report. New data length: {len(data)} ---") # Added print

        try:
            print(f"--- DB: Attempting to write to {REPORTS_PATH} ---") # Added print
            with open(REPORTS_PATH, "w") as file:
                json.dump(data, file, indent=2)
            print(f"--- DB: Successfully wrote to {REPORTS_PATH} ---") # Added print
        except Exception as e:
            print(f"!!! DB ERROR: Failed to write to {REPORTS_PATH}: {e}")
            raise # Re-raise write errors

    except Exception as e:
        # Catch any unexpected error during the whole save process
        print(f"!!! DB CRITICAL ERROR in save_report: {e}")
        raise # Re-raise it