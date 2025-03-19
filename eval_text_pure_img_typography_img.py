import os
import json
import base64
import requests

# Constants
JSON_DIR = "./processed_questions"  # Directory containing JSON files
IMAGE_ROOT_DIR = "./MM-SafetyBench(imgs)"  # Root directory for image folders
OUTPUT_DIR = "./newoutput"  # Directory to store output JSON files
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to encode an image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Loop through each JSON file in the JSON directory
for json_filename in sorted(os.listdir(JSON_DIR)):
    if not json_filename.endswith(".json"):
        continue  # Skip non-JSON files

    json_path = os.path.join(JSON_DIR, json_filename)

    # Extract category name from JSON filename
    category_name = json_filename.replace(".json", "")
    image_category_path = os.path.join(IMAGE_ROOT_DIR, category_name, "SD_TYPO")  # Adjust if needed

    # Check if the corresponding image directory exists
    if not os.path.isdir(image_category_path):
        print(f"Skipping {json_filename}: No corresponding image directory found.")
        continue

    # Load the JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Store results for this category
    results = {}

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
            results[key] = {
                "category": category_name,
                "image": f"{key}.jpg",
                "question": rephrased_question,
                "gpt4o_response": result['choices'][0]['message']['content']
            }
        else:
            print(f"Error for {category_name}-{key}.jpg: {response.text}")
            results[key] = {
                "category": category_name,
                "image": f"{key}.jpg",
                "question": rephrased_question,
                "error": response.text
            }

    # Save results to a category-specific JSON file
    category_output_file = os.path.join(OUTPUT_DIR, f"{category_name}.json")
    with open(category_output_file, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

    print(f"Results for {category_name} saved to {category_output_file}")

print("Processing complete. All outputs stored in 'output/' directory.")
