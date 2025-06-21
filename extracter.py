import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# in-memory list of possible document_type clusters
cluster_map = [
    "Provvedimenti a favore",
    "Supervisione Mifid",
    "Flessibilità orarie",
    "Polizza sanitaria",
    "Formazione",
    "Fringe benefits",
    "Assunzione matricola",
    "Primo impiego",
    "Fondo pensione",
    "Destinazione TFR",
    "Nessun cluster",
    "Nomina titolarità",
    "Assegnazione ruolo",
    "Part-time",
    "Cessazione",
    "Proroga TD",
    "Provvedimenti disciplinari",
    "Trasferimento",
    "Lettera assunzione",
    "Trasformazione TI",
    "Proposta di assunzione",
]

# Project details – replace with your real values
PROJECT_ID = "credemhack-iam"
LOCATION   = "us-central1"

# Initialize Vertex AI once
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Load the Gemini model
model = GenerativeModel("gemini-2.5-flash")

def extract_document_info(text: str, filename: str) -> dict:
    """
    Extracts metadata from `text` using a Gemini model.
    Returns a dict with keys:
      filename, person_number, document_type, country,
      document_code, document_name, date_from, date_to,
      source_system_owner, source_system_id
    Missing values become the empty string.
    """
    # Build a prompt that asks for a JSON object
    prompt = f"""
You are an information‐extraction assistant.  
Given the following raw document text, extract these fields:
  - person_number
  - document_type   (must be one of: {', '.join(cluster_map)})
  - country
  - document_code
  - document_name
  - date_from  
Return a JSON object exactly like this (and nothing else):
{{
  "person_number": "...",
  "document_type": "...",
  "country": "...",
  "document_code": "...",
  "document_name": "...",
  "date_from": "..."
}}
If any field is not present or you cannot determine it, set it to the empty string.  
Here is the text:
\"\"\"{text}\"\"\"
"""

    try:
        response = model.generate_content(
            prompt,
            stream=False,
            temperature=0.0,
            max_output_tokens=512
        )
        # The model's raw text response
        json_blob = response.text.strip()
        
        # Attempt to parse it
        extracted = json.loads(json_blob)
        # Ensure all keys exist
        for key in ("person_number", "document_type", "country", "document_code", "document_name", "date_from"):
            if key not in extracted or not isinstance(extracted[key], str):
                extracted[key] = ""
    except Exception as e:
        # On any error, fall back to empties
        extracted = {
            "person_number": "",
            "document_type": "",
            "country": "",
            "document_code": "",
            "document_name": "",
            "date_from": ""
        }

    # Build final result dict
    result = {
        "filename":            filename,
        "person_number":       extracted["person_number"],
        "document_type":       extracted["document_type"],
        "country":             extracted["country"],
        "document_code":       extracted["document_code"],
        "document_name":       extracted["document_name"],
        "date_from":           extracted["date_from"],
        "date_to":             "",                      # always empty
        "source_system_owner": "PEOPLE",
        "source_system_id":    extracted["document_code"],  # mirror
    }
    return result

# Example usage
if __name__ == "__main__":
    sample_text = "Documento n. 12345 rilasciato in Italia il 2023-05-12 per Mario Rossi"
    info = extract_document_info(sample_text, filename="doc1.txt")
    print(json.dumps(info, ensure_ascii=False, indent=2))