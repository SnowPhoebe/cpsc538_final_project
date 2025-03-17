import os
import json
import base64
import requests
from PIL import Image
from io import BytesIO

# Constants
IMAGE_ROOT = "./MM-SafetyBench(imgs)/"  # Root directory where category folders are stored
OUTPUT_FOLDER = "./image_only_responses/"  # Directory to save API responses
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Iterate through all category folders
for category_folder in sorted(os.listdir(IMAGE_ROOT)):
    category_path = os.path.join(IMAGE_ROOT, category_folder)

    # Check if the category path is a directory
    if not os.path.isdir(category_path):
        continue

    # Locate the SD folder inside the category folder
    sd_folder = os.path.join(category_path, "SD")
    if not os.path.exists(sd_folder):
        print(f"Skipping {category_folder}: No SD folder found.")
        continue

    print(f"Processing SD folder in {category_folder}...")

    results = {}

    # Process all images in the SD folder
    for image_filename in sorted(os.listdir(sd_folder)):
        if not image_filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue  # Skip non-image files

        image_path = os.path.join(sd_folder, image_filename)
        image_base64 = encode_image(image_path)

        # Construct API payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
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
        image_key = image_filename
        if response.status_code == 200:
            result = response.json()
            results[image_key] = {
                "image": image_filename,
                "category": category_folder,
                "gpt4o_response": result['choices'][0]['message']['content']
            }
        else:
            print(f"Error processing {image_filename}: {response.text}")
            results[image_key] = {
                "image": image_filename,
                "category": category_folder,
                "error": response.text
            }

    # Save results for this category
    output_filename = f"response_{category_folder}.json"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

    print(f"Responses saved to {output_path}")

print(f"All responses saved in: {OUTPUT_FOLDER}")
