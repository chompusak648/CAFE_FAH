import os
import uuid
from backend.rag.ingest import process_file
from backend.config import UPLOAD_DIR

def ingest_all_uploads():
    if not os.path.exists(UPLOAD_DIR):
        print(f"Upload directory {UPLOAD_DIR} does not exist.")
        return

    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    print(f"Found {len(files)} files in {UPLOAD_DIR}")

    for filename in files:
        file_path = os.path.join(UPLOAD_DIR, filename)
        doc_id = str(uuid.uuid4())
        print(f"--- Ingesting {filename} (doc_id: {doc_id}) ---")
        try:
            process_file(file_path, doc_id)
        except Exception as e:
            print(f"Error ingesting {filename}: {e}")

if __name__ == "__main__":
    ingest_all_uploads()
