import os
from google.cloud import storage

def download_files_from_bucket(bucket_name, local_dir, blob_names=None):
    """
    Downloads files from a Google Cloud Storage bucket to a local directory.

    Args:
        bucket_name (str): The name of the GCS bucket.
        local_dir (str): The local directory where files will be downloaded.
        blob_names (list, optional): A list of specific blob names (paths) to download.
                                    If None, all files in the bucket will be downloaded.
                                    Defaults to None.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    if blob_names:
        for blob_name in blob_names:
            try:
                blob = bucket.blob(blob_name)
                local_file_path = os.path.join(local_dir, os.path.basename(blob_name))
                blob.download_to_filename(local_file_path)
                print(f"Downloaded '{blob_name}' from bucket '{bucket_name}' to '{local_file_path}'")
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
                print(f"Downloaded '{blob.name}' from bucket '{bucket_name}' to '{local_file_path}'")
            if not blobs_exist:
                print(f"Bucket '{bucket_name}' is empty")
        except Exception as e:
            print(f"Error accessing bucket '{bucket_name}': {e}")

from PIL import Image

def convert_tif_to_pdf(tif_directory, pdf_directory):
    """
    Converts all TIFF files in a directory to PDFs and saves them in another directory.

    Args:
        tif_directory (str): The directory containing the TIFF files.
        pdf_directory (str): The directory where the PDF files will be saved.
    """

    if not os.path.exists(pdf_directory):
        os.makedirs(pdf_directory)

    for filename in os.listdir(tif_directory):
        if filename.lower().endswith((".tif", ".tiff")):
            tif_filepath = os.path.join(tif_directory, filename)
            pdf_filename = os.path.splitext(filename)[0] + ".pdf"
            pdf_filepath = os.path.join(pdf_directory, pdf_filename)

            try:
                image = Image.open(tif_filepath)
                image.save(pdf_filepath, "PDF", resolution=100.0, save_all=True)  # Use save_all for multi-page TIFFs
                print(f"Converted '{filename}' to '{pdf_filename}'")
            except Exception as e:
                print(f"Error converting '{filename}': {e}")

    # delete tif files
    for filename in os.listdir(tif_dir):
        if filename.lower().endswith((".tif", ".tiff")):
            file_path = os.path.join(tif_dir, filename)
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")

if __name__ == "__main__":
    my_bucket_name = "credemhack-documents-iam"
    my_local_dir = "downloaded_files"

    # Download all files
    download_files_from_bucket(my_bucket_name, my_local_dir) # <-- uncomment the first time to download files

    tif_dir = "downloaded_files"
    pdf_dir = "downloaded_files"

    convert_tif_to_pdf(tif_dir, pdf_dir)

