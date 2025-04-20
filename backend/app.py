from fastapi import FastAPI, Form, UploadFile, File, HTTPException # Added HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse # Added FileResponse
# from fastapi.staticfiles import StaticFiles # We are removing StaticFiles for uploads now
import os
import json
from datetime import datetime

# Assuming these relative imports work because uvicorn is run from the root
from .nlp import analyze_report
from .blockchain_mock import generate_hash
from .db import save_report # Ensure db.py uses REPORTS_JSON_PATH correctly

# --- Define paths relative to this script file for robustness ---
SCRIPT_DIR = os.path.dirname(__file__)
UPLOAD_DIR_ABS = os.path.join(SCRIPT_DIR, "uploads")
# Assumes reports.json is in the project root directory (one level up from backend)
REPORTS_JSON_PATH = os.path.join(SCRIPT_DIR, "..", "reports.json")

# --- Ensure necessary directories/files exist ---
os.makedirs(UPLOAD_DIR_ABS, exist_ok=True) # Ensure uploads dir exists
# Optional: Create reports.json if it doesn't exist, containing an empty list
if not os.path.exists(REPORTS_JSON_PATH):
    print(f"--- Creating initial empty reports file at: {REPORTS_JSON_PATH} ---")
    with open(REPORTS_JSON_PATH, "w") as f:
        json.dump([], f)

app = FastAPI()

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REMOVED StaticFiles Mount for uploads ---
# app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR_ABS), name="uploads")


# --- API Endpoints ---

@app.post("/submit-report")
async def submit_report(
     category: str = Form(...),
     heading: str = Form(...),
     body: str = Form(...),
     location: str = Form(None), # Use None as default for optional fields
     file: UploadFile = File(None) # Use None as default for optional file
):
    """Handles submission of a new whistleblowing report."""
    print("--- Received request for /submit-report ---")
    # NLP Validation
    result = analyze_report(heading, body)
    if result["status"] == "rejected":
        print(f"--- NLP Rejected: {result['reason']} ---")
        return JSONResponse(content=result, status_code=400)

    print("--- NLP Accepted ---")
    report = {
        "category": category,
        "heading": heading,
        "body": body,
        "location": location,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Include time
        "score": result["score"],
        "file": None # Initialize file key
    }

    # Hash it - Generate unique ID for the report
    try:
        print("--- Generating Hash ---")
        report["hash_id"] = generate_hash(report)
        print(f"--- Hash Generated: {report['hash_id']} ---")
    except Exception as e:
        print(f"!!! ERROR during hashing: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report hash: {e}")

    # Handle file upload (if provided)
    if file and file.filename:
        print(f"--- Handling File: {file.filename} ---")

        # Create a unique filename using the hash and original filename
        original_filename = file.filename
        unique_filename = f"{report['hash_id']}_{original_filename}"

        print(f"--- Generated Unique Filename: {unique_filename} ---")
        file_location = os.path.join(UPLOAD_DIR_ABS, unique_filename)
        print(f"--- Saving file to: {file_location} ---")

        try:
            contents = await file.read()
            with open(file_location, "wb") as f:
                f.write(contents)
            # Store the UNIQUE filename in the report data
            report["file"] = unique_filename
            print("--- File Saved Successfully ---")
        except Exception as e:
             print(f"!!! ERROR saving file: {e}")
             raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
        finally:
            await file.close()
    else:
        print("--- No file uploaded or file has no name ---")

    # Save report data to the database (reports.json)
    try:
        print(f"--- Saving Report {report.get('hash_id')} to DB ---")
        save_report(report)
        print("--- Report Saved to DB Successfully ---")
    except Exception as e:
        print(f"!!! ERROR saving report to DB: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save report data: {e}")

    print("--- Request /submit-report Completed Successfully ---")
    return {"status": "accepted", "hash": report["hash_id"]}


@app.get("/reports")
def get_reports():
    """Reads and returns all reports from reports.json, sorted by date."""
    print(f"--- Received request for /reports. Reading from: {REPORTS_JSON_PATH} ---")
    try:
        with open(REPORTS_JSON_PATH, "r") as f:
            content = f.read()
            if not content.strip():
                data = []
            else:
                data = json.loads(content)
                if not isinstance(data, list):
                     raise ValueError("Invalid report file format: root element is not a list.")
        print(f"--- Successfully read and returning {len(data)} reports. ---")
        return data
    except FileNotFoundError:
         print(f"--- Report file not found at: {REPORTS_JSON_PATH}. Returning empty list. ---")
         return []
    except json.JSONDecodeError as e:
         print(f"!!! ERROR decoding JSON from {REPORTS_JSON_PATH}: {e}")
         raise HTTPException(status_code=500, detail=f"Error reading report file: Corrupted JSON - {e}")
    except ValueError as e:
         raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
         print(f"!!! UNEXPECTED ERROR reading reports: {e}")
         raise HTTPException(status_code=500, detail=f"An unexpected error occurred reading reports: {e}")


# --- ADDED: Dedicated Download Endpoint ---
@app.get("/download/{filename}")
async def download_file(filename: str):
    """Provides a file for download, forcing the download dialog."""
    print(f"--- Download request for: {filename} ---")
    file_path = os.path.join(UPLOAD_DIR_ABS, filename)
    print(f"--- Looking for file at: {file_path} ---")
    filename = "info"

    if os.path.isfile(file_path):
        # Return FileResponse:
        # - path: the location of the file on the server
        # - media_type: 'application/octet-stream' is a generic type forcing download
        # - filename: Sets the Content-Disposition header to suggest this name to the browser
        print(f"--- File found. Sending {filename} for download. ---")
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)
    else:
        print(f"!!! Download Error: File not found at: {file_path} !!!")
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")


# --- Optional: Root endpoint ---
@app.get("/")
async def read_root():
    """Basic API status check."""
    return {"message": "Welcome to the WhistleSafe API!"}