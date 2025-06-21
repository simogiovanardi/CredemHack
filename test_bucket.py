import os
import shutil
from google.cloud import storage
from PIL import Image

def download_files_from_bucket(bucket_name, local_dir, blob_names=None):
    """
    Downloads files from a Google Cloud Storage bucket to a local directory.

    Args:
        bucket_name (str): The name of the GCS bucket.
        local_dir (str): The local directory where files will be downloaded.
        blob_names (list, optional): A list of specific blob names (paths) to download.
                                     If None, all files in the bucket will be downloaded.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    os.makedirs(local_dir, exist_ok=True)

    if blob_names:
        for blob_name in blob_names:
            try:
                blob = bucket.blob(blob_name)
                local_file_path = os.path.join(local_dir, os.path.basename(blob_name))
                blob.download_to_filename(local_file_path)
                print(f"Downloaded '{blob_name}' to '{local_file_path}'")
            except Exception as e:
                print(f"Error downloading '{blob_name}': {e}")
    else:
        try:
            blobs = bucket.list_blobs()
            blobs_exist = False
            for blob in blobs:
                blobs_exist = True
                local_file_path = os.path.join(local_dir, os.path.basename(blob.name))
                blob.download_to_filename(local_file_path)
                print(f"Downloaded '{blob.name}' to '{local_file_path}'")
            if not blobs_exist:
                print(f"Bucket '{bucket_name}' is empty")
        except Exception as e:
            print(f"Error accessing bucket '{bucket_name}': {e}")

def process_files_to_pdf(source_dir, output_dir):
    """
    Processes a directory:
    - Moves any .pdf files to the output directory.
    - Converts .tif/.tiff/.png files to PDF and saves them in the output directory.

    Args:
        source_dir (str): Directory containing the original files.
        output_dir (str): Directory to store resulting PDF files.
    """

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        src_path = os.path.join(source_dir, filename)

        if filename.lower().endswith(".pdf"):
            dst_path = os.path.join(output_dir, filename)
            shutil.copy2(src_path, dst_path)
            print(f"Copied PDF '{filename}' to '{output_dir}'")

        elif filename.lower().endswith((".tif", ".tiff", ".png")):
            pdf_filename = os.path.splitext(filename)[0] + ".pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)

            try:
                image = Image.open(src_path)
                # For PNG, convert to RGB because PNG might be RGBA (with alpha)
                if filename.lower().endswith(".png"):
                    image = image.convert("RGB")
                image.save(pdf_path, "PDF", resolution=100.0, save_all=True)
                print(f"Converted '{filename}' to '{pdf_filename}' and saved in '{output_dir}'")
            except Exception as e:
                print(f"Error converting '{filename}': {e}")

if __name__ == "__main__":
    bucket_name = "credemhack-documents-iam"
    blob_dir = "BlobFiles"
    pdf_dir = "pdf_files"

    # Step 1: Download all files into blob_dir
    download_files_from_bucket(bucket_name, blob_dir)  # Uncomment if needed

    # Step 2: Convert/process to pdf_dir
    process_files_to_pdf(blob_dir, pdf_dir)
