# WhistleSafe: Secure & Anonymous Whistleblowing Platform

<p align="center">
  <img src="https://github.com/user-attachments/assets/2c86e970-69c5-4244-aaf2-73609030b5e8" width="600" alt="image"/>
</p>

## Project Overview

WhistleSafe is a secure and anonymous whistleblowing platform designed to empower individuals to report misconduct safely and transparently. It provides a robust system for submitting reports, leveraging Natural Language Processing (NLP) for credibility analysis, and a mock blockchain mechanism for ensuring report integrity and generating unique, traceable IDs. The platform aims to promote accountability by offering a protected channel for disclosures, complete with file attachments and a comprehensive case viewing interface.

## Features

*   **Anonymous Report Submission:** Users can submit reports covering various categories (corruption, fraud, harassment, etc.) without revealing their identity.
*   **NLP-Powered Credibility Analysis:** Reports undergo an automatic analysis using NLTK's VADER sentiment analyzer and custom rules to assess their credibility, filtering out spam or vague submissions.
*   **Mock Blockchain Hashing:** Each accepted report is hashed using a SHA-256 algorithm, generating a unique `hash_id` that serves as a non-repudiable identifier, simulating blockchain's immutable ledger concept.
*   **Secure File Uploads:** Users can attach supporting evidence (documents, images, videos) securely, which are stored on the server and linked to the report.
*   **Report Viewing & Filtering:** An intuitive frontend interface allows administrators or authorized users to view, search, filter (by category, date range, keyword), and sort (by date, credibility score) all submitted reports.
*   **Evidence Download:** Attached files can be downloaded directly from the report viewing interface.
*   **Simple JSON-based Data Storage:** All report metadata is persistently stored in a local `reports.json` file, acting as a lightweight database.
*   **Responsive Frontend:** Built with HTML, CSS, and JavaScript for a user-friendly experience across devices.

## Technologies Used

**Backend:**
*   **Python:** The core programming language.
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.8+.
*   **Uvicorn:** An ASGI server for running FastAPI applications.
*   **`nltk` (Natural Language Toolkit):** Used in the NLP module for sentiment analysis (`VADER`).
*   **`hashlib`:** Python's standard library for cryptographic hashing (SHA-256).
*   **`python-multipart`:** For handling form data and file uploads in FastAPI.

**Frontend:**
*   **HTML5:** Structure of the web pages.
*   **CSS3:** Styling and layout (`style.css`).
*   **JavaScript:** Dynamic interactions, form submission handling (Fetch API), report display, filtering, and sorting.
*   **Font Awesome:** Icons for a better user experience.
*   **Google Fonts:** For modern typography.

**Database:**
*   **JSON File (`reports.json`):** A simple, file-based database for storing report data.

## Project Structure

<img width="380" height="474" alt="image" src="https://github.com/user-attachments/assets/ac8cca0c-db33-4b31-a5f2-a504bd423dc0" width = "400"/>


## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8+ installed
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/WhistleSafe.git
    cd WhistleSafe
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install backend dependencies:**
    The `requirements.txt` file in the `backend` directory lists all necessary Python packages.
    ```bash
    pip install -r backend/requirements.txt
    # If requirements.txt is empty or missing, use:
    # pip install fastapi uvicorn python-multipart nltk
    ```

4.  **Download NLTK data (VADER Lexicon):**
    The NLP module `nlp.py` requires the `vader_lexicon`. This will be downloaded automatically when `nlp.py` is imported and run, but you can also do it manually:
    ```python
    python -c "import nltk; nltk.download('vader_lexicon')"
    ```

5.  **Initialize `reports.json` (if it doesn't exist):**
    The `app.py` script will automatically create an empty `reports.json` file in the project root if it's not found when the FastAPI app starts.

### Running the Application

1.  **Start the FastAPI backend server:**
    Navigate to the root directory of the project (`WhistleSafe/`) and run:
    ```bash
    uvicorn backend.app:app --reload
    ```
    This will start the server, usually accessible at `http://127.0.0.1:8000`. The `--reload` flag enables live reloading on code changes.

2.  **Open the Frontend:**
    Open your web browser and navigate to the `frontend/index.html` file in your project directory.
    You can simply open it directly:
    `file:///path/to/WhistleSafe/frontend/index.html`

    *Note: The frontend JavaScript is configured to communicate with the backend at `http://127.0.0.1:8000`. Ensure the backend server is running before interacting with the frontend.*

## Usage

### Submitting a Report (`blow-whistle.html`)

1.  Navigate to the "Report" page from the homepage, or directly open `frontend/blow-whistle.html`.
2.  Fill in the required fields: `Category`, `Report Title`, and `Description`.
3.  Optionally, provide a `Location` and `Attach Evidence` (files like PDF, DOCX, JPG, PNG, MP4, MOV are supported).
4.  Click "Submit Report".
5.  Upon successful submission, you will receive a confirmation message with a unique `hash_id`. If the report is rejected by the NLP system, you'll receive a reason.

### Viewing Cases (`know-whistle.html`)

1.  Navigate to the "Cases" page from the homepage, or directly open `frontend/know-whistle.html`.
2.  All submitted reports will be displayed.
3.  Use the **Search bar** to find reports by keywords in their heading, body, or location.
4.  Apply **Filters** by `Category` or `Date Range`.
5.  **Sort** reports by `Newest First`, `Oldest First`, `Highest Credibility`, or `Lowest Credibility`.
6.  Click the "View Details" button on any report card to see its full content.
7.  If a report has an attached file, a "Evidence" button will appear, allowing you to download the linked file.

## API Endpoints

The backend FastAPI application exposes the following endpoints:

*   **`GET /`**
    *   **Description:** Basic API status check.
    *   **Returns:** `{"message": "Welcome to the WhistleSafe API!"}`

*   **`POST /submit-report`**
    *   **Description:** Submits a new whistleblowing report.
    *   **Form Data:**
        *   `category` (string, required): e.g., "corruption", "fraud", "harassment".
        *   `heading` (string, required): Title of the report.
        *   `body` (string, required): Detailed description of the incident.
        *   `location` (string, optional): Location where the incident occurred.
        *   `file` (file, optional): Attached evidence file.
    *   **Returns (Success):** `{"status": "accepted", "hash": "generated_hash_id"}`
    *   **Returns (Failure/NLP Rejection):** `{"status": "rejected", "score": 0.1, "reason": "Report too short..."}` or `HTTP 400/500` with error details.

*   **`GET /reports`**
    *   **Description:** Retrieves all submitted reports from `reports.json`.
    *   **Returns:** A JSON array of report objects, sorted by date (newest first by default in frontend).

*   **`GET /download/{filename}`**
    *   **Description:** Downloads an uploaded evidence file.
    *   **Path Parameter:** `filename` (string): The unique filename of the uploaded file (as stored in `report["file"]`).
    *   **Returns:** The requested file as a `FileResponse` with `application/octet-stream` media type, forcing a download.
    *   **Errors:** `HTTP 404 Not Found` if the file does not exist.

---

**WhistleSafe** – Speak Up Safely. Your Voice Matters.
