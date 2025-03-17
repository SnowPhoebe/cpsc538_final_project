import os
import json
import base64
import requests

# Constants
JSON_DIR = "./processed_questions_modified"  # Directory containing JSON files
IMAGE_ROOT_DIR = "./MM-SafetyBench(imgs)"  # Root directory for image folders
OUTPUT_FILE = "gpt4o_responses.json"  # Output file for responses
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "your_openai_api_key_here"  # Replace with your actual API key

# Function to encode an image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Store results in a dictionary
results = {}

# Loop through each JSON file in the JSON directory
for json_filename in sorted(os.listdir(JSON_DIR)):
    if not json_filename.endswith(".json"):
        continue  # Skip non-JSON files

    json_path = os.path.join(JSON_DIR, json_filename)

    # Extract category name from JSON filename
    category_name = json_filename.replace(".json", "")
    image_category_path = os.path.join(IMAGE_ROOT_DIR, category_name, "SD")  # Adjust the image subfolder if needed

    # Check if the corresponding image directory exists
    if not os.path.isdir(image_category_path):
        print(f"Skipping {json_filename}: No corresponding image directory found.")
        continue

    # Load the JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Process each entry in the JSON
    for key, value in data.items():
        print(f"Processing: {category_name} - {key}")

        image_path = os.path.join(image_category_path, f"{key}.jpg")

        if not os.path.exists(image_path):
            print(f"Warning: Image {image_path} not found. Skipping.")
            continue

        # Extract the rephrased question
        rephrased_question = value.get("Rephrased Question", "")
        if not rephrased_question:
            print(f"Skipping entry {key} due to missing 'Rephrased Question'.")
            continue

        # Convert image to base64
        image_base64 = encode_image(image_path)

        # Construct API payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": rephrased_question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 600
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # Make API call
        response = requests.post(API_URL, headers=headers, json=payload)

        # Process response
        if response.status_code == 200:
            result = response.json()
            results[f"{category_name}-{key}"] = {
                "category": category_name,
                "image": f"{key}.jpg",
                "question": rephrased_question,
                "gpt4o_response": result['choices'][0]['message']['content']
            }
        else:
            print(f"Error for {category_name}-{key}.jpg: {response.text}")
            results[f"{category_name}-{key}"] = {
                "category": category_name,
                "image": f"{key}.jpg",
                "question": rephrased_question,
                "error": response.text
            }

# Save results to a JSON file
with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, indent=4)

print(f"All responses saved to {OUTPUT_FILE}")
