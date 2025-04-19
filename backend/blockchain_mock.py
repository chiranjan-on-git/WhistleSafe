import hashlib
import time

def generate_hash(report_data: dict) -> str:
    """
    Simulates creating a blockchain hash of the report.
    Returns a SHA-256 hash string based on the content + timestamp.
    """
    report_string = str(report_data) + str(time.time())
    hash_object = hashlib.sha256(report_string.encode())
    return hash_object.hexdigest()
