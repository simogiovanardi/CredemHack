import os
import glob
from google.cloud import documentai_v1 as documentai

def process_document(project_id: str, location: str, processor_id: str, file_path: str) -> documentai.Document:
    """Processes a single document using Document AI."""
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    with open(file_path, "rb") as f:
        image_content = f.read()

    raw_document = documentai.RawDocument(
        content=image_content, mime_type="application/pdf"  # Assuming PDF, adjust if needed
    )
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)
    return result.document


def extract_text_from_document(document: documentai.Document) -> str:
    """Extracts text from a Document object."""
    return document.text


def batch_process_documents(
    project_id: str, location: str, processor_id: str, input_folder: str, output_folder: str
):
    """Processes all PDF documents in a folder and saves the extracted text."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))  # Adjust file extension if needed

    for pdf_file in pdf_files:
        try:
            document = process_document(project_id, location, processor_id, pdf_file)
            extracted_text = extract_text_from_document(document)

            output_filename = os.path.splitext(os.path.basename(pdf_file))[0] + ".txt"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(extracted_text)

            print(f"Processed and saved: {output_filename}")

        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")


if __name__ == "__main__":
    # Replace with your actual values
    project_id = "credemhack-iam"
    location = "us"  # or your processor's location
    processor_id = "906fe5719131d935"
    input_folder = "downloaded_files"
    output_folder = "ocr_output"

    batch_process_documents(project_id, location, processor_id, input_folder, output_folder)