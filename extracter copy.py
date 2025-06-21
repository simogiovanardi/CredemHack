import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Project details - Replace with your actual project and region
PROJECT_ID = "credemhack-iam"
LOCATION = "us-central1"  # Or your preferred region

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Load the Gemini model
model = GenerativeModel("gemini-2.5-flash")  # Or the specific model you want to use

# Define your prompt
prompt = "Write a short story about a robot who learns to love."

# Generate content
try:
    responses = model.generate_content(
        prompt,
        stream=False,  # Set to True for streaming responses
    )

    print(responses.text)  # Print the generated text

except Exception as e:
    print(f"An error occurred: {e}")

