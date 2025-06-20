import os
import sys
from google.cloud import storage

def download_input_files(storage_client, bucket_name):
    """
    List or download all blobs in gs://{bucket_name}/
    Return a list of local file paths to process.
    """
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    local_paths = []
    for blob in blobs:
        # skip "directories"
        if blob.name.endswith("/"):
            continue
        # create local dir if needed
        local_dir = os.path.join("input_files", os.path.dirname(blob.name))
        os.makedirs(local_dir, exist_ok=True)
        # download
        local_path = os.path.join("input_files", blob.name)
        if os.path.exists(local_path):
            print(f"Skipping download of {blob.name} (already exists)")
        else:
            print(f"Downloading {blob.name} to {local_path}")
            blob.download_to_filename(local_path)
        # add to list of files to process
        local_paths.append(local_path)
    return local_paths

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

def copy_to_blobfiles(src, dest_dir):
    """
    Copy the original file (or fetch from GCS) into dest_dir
    so it ends up under BlobFiles/
    """
    if src.startswith("gs://"):
        # copy from GCS
        bucket_name, blob_name = src[5:].split("/", 1)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        dest_path = os.path.join(dest_dir, os.path.basename(blob_name))
        blob.download_to_filename(dest_path)
    else:
        # copy from local
        pass

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

    # 3) Download or list inputs
    input_items = download_input_files(storage_client, input_bucket)

    # 4) Process each document
    processed_docs = []
    for item in input_items:
        doc = process_document(item)
        processed_docs.append(doc)

    # 5) Generate the two record lists
    dor_records = generate_documents_of_record_records(processed_docs)
    da_records  = generate_document_attachment_records(processed_docs)

    # 6) Prepare local output dirs
    out_base = "output"
    os.makedirs(out_base, exist_ok=True)
    dat_path = os.path.join(out_base, "DocumentsOfRecord.dat")
    blob_dir = os.path.join(out_base, "BlobFiles")
    os.makedirs(blob_dir, exist_ok=True)

    # 7) Write .dat
    write_dat_file(dor_records, da_records, dat_path)

    # 8) Copy original docs into BlobFiles
    for item in input_items:
        copy_to_blobfiles(item, blob_dir)

    # 9) Zip everything
    zip_path = os.path.join(out_base, "solution.zip")
    create_solution_zip(dat_path, blob_dir, zip_path)

    # 10) Upload
    upload_to_gcs(storage_client, output_bucket, run_id, zip_path)

if __name__ == "__main__":
    main()