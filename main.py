import os
import sys
from google.cloud import storage
from test_bucket import download_files_from_bucket, process_files_to_pdf
from ocr import batch_process_documents, extract_text_from_document, process_document






def process_document(blob_or_path):
    """
    Given a document (PDF/image), classify it, extract name/surname/date,
    enrich via anagrafica, etc.
    Return a dict with all intermediate metadata needed.
    """
    # TODO: implement
    return {
        "person_number": None,
        "document_type": None,
        "country": None,
        "date_from": None,
        "date_to": None,
        "document_name": None,
        "original_file": None,   # path or blob name
        # etc...
    }

def generate_documents_of_record_records(docs):
    """
    Given list of processed docs, build the list of lines/records
    for the DocumentsOfRecord section.
    """
    # TODO: implement
    return []

def generate_document_attachment_records(docs):
    """
    Given list of processed docs, build the list of lines/records
    for the DocumentAttachment section.
    """
    # TODO: implement
    return []

def write_dat_file(dor_records, da_records, output_path):
    """
    Write the two METADATA sections and all MERGE lines to
    output_path in UTF-8, pipe-delimited.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Section 1 header
        f.write("METADATA|DocumentsOfRecord|PersonNumber|DocumentType|Country|"
                "DocumentCode|DocumentName|DateFrom|DateTo|SourceSystemOwner|SourceSystemId\n")
        for line in dor_records:
            f.write(line + "\n")
        # Section 2 header
        f.write("METADATA|DocumentAttachment|PersonNumber|DocumentType|Country|"
                "DocumentCode|DataTypeCode|URLorTextorFileName|Title|File|"
                "SourceSystemOwner|SourceSystemId\n")
        for line in da_records:
            f.write(line + "\n")

def create_solution_zip(dat_file_path, blob_files_dir, zip_path):
    """
    Create a ZIP containing:
      - DocumentsOfRecord.dat at root
      - BlobFiles/ with all original docs
    """
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # add .dat
        z.write(dat_file_path, arcname=os.path.basename(dat_file_path))
        # add blob files
        for root, _, files in os.walk(blob_files_dir):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.join("BlobFiles", fname)
                z.write(full, arcname=arc)

def upload_to_gcs(storage_client, bucket_name, run_id, local_file_path):
    """
    Upload local_file_path → gs://{bucket_name}/{run_id}/solution.zip
    """
    bucket = storage_client.bucket(bucket_name)
    destination_blob = f"{run_id}/solution.zip"
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(local_file_path)
    print(f"Uploaded solution.zip to gs://{bucket_name}/{destination_blob}")

def main():
    
    # 6) Prepare local output dirs
    out_base = "output"
    os.makedirs(out_base, exist_ok=True)
    dat_path = os.path.join(out_base, "DocumentsOfRecord.dat")
    blob_dir = os.path.join(out_base, "BlobFiles")
    os.makedirs(blob_dir, exist_ok=True)

    # 1) Read env vars
    run_id = os.environ.get("RUN_ID")
    input_bucket = os.environ.get("INPUT_BUCKET")
    output_bucket = os.environ.get("OUTPUT_BUCKET")

    if not run_id or not input_bucket or not output_bucket:
        import time
        run_id = str(int(time.time()))
        input_bucket = "credemhack-documents-iam"
        output_bucket = "credemhack-output-iam"

    if not all([run_id, input_bucket, output_bucket]):
        print("ERROR: RUN_ID, INPUT_BUCKET and OUTPUT_BUCKET must be set", file=sys.stderr)
        sys.exit(1)

    # 2) Init storage client
    storage_client = storage.Client()

    # 3) Download input from bucket to output/Blob
    bucket_name = "credemhack-documents-iam"
    pdf_dir = "pdf_files"

    download_files_from_bucket(bucket_name, blob_dir)  
    process_files_to_pdf(blob_dir, pdf_dir)

    # 3a) List the pdf files in pdf_files
    input_items = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]    

    # Extract the text in a dedicated folder
    project_id = "credemhack-iam"
    location = "us"  # or your processor's location
    processor_id = "906fe5719131d935"
    input_folder = "pdf_files"
    output_folder = "ocr_output"
    batch_process_documents(project_id, location, processor_id, input_folder, output_folder)

    # 4) Process each document
    processed_docs = []
    for item in input_items:
        doc = process_document(item)
        processed_docs.append(doc)

    # 5) Generate the two record lists
    dor_records = generate_documents_of_record_records(processed_docs)
    da_records  = generate_document_attachment_records(processed_docs)

    # 7) Write .dat
    write_dat_file(dor_records, da_records, dat_path)

    # 9) Zip everything
    zip_path = os.path.join(out_base, "solution.zip")
    create_solution_zip(dat_path, blob_dir, zip_path)

    # 10) Upload
    upload_to_gcs(storage_client, output_bucket, run_id, zip_path)

if __name__ == "__main__":
    main()