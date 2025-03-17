import os
import json
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Constants
JSON_FOLDER = "./processed_questions/"  # Directory containing all JSON files
OUTPUT_FOLDER = "./typography_image_only_responses/"  # Directory to save results
GENERATED_IMAGES_DIR = "./typography_image_only/generated_images/"  # Directory containing generated images
SAFETY_BENCH_DIR = "./MM-SafetyBench(imgs)/"  # Directory containing MM-SafetyBench images
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # Replace with actual API key

# Ensure required directories exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def encode_image_to_base64(image_path):
    """Encodes an image as a base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Warning: Image not found at {image_path}")
        return None


# Loop through all JSON files in the folder
for json_filename in os.listdir(JSON_FOLDER):
    if not json_filename.endswith(".json"):
        continue  # Skip non-JSON files

    json_path = os.path.join(JSON_FOLDER, json_filename)
    print(f"Processing JSON file: {json_filename}")

    # Load JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}

    # Iterate over the JSON data
    for key, value in data.items():
        print(f"Processing entry: {key}")

        # Extract relevant text
        rephrased_question = value.get("Changed Question", "")
        if not rephrased_question:
            print(f"Skipping entry {key} due to missing 'Changed Question'.")
            continue
        
        category_name = json_filename.split(".")[0]
        # Find corresponding images
        generated_image_path = os.path.join(GENERATED_IMAGES_DIR, f"{json_filename[:-5]}_{key}.jpg")
        safety_bench_image_path = os.path.join(SAFETY_BENCH_DIR, f"{category_name}", "SD", f"{key}.jpg")

        # Encode images to base64
        generated_image_base64 = encode_image_to_base64(generated_image_path)
        safety_bench_image_base64 = encode_image_to_base64(safety_bench_image_path)

        if not generated_image_base64 or not safety_bench_image_base64:
            print(f"Skipping {key} due to missing images.")
            continue

        # Construct API payload with two images
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{generated_image_base64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{safety_bench_image_base64}"
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
                "generated_image": generated_image_path,
                "safety_bench_image": safety_bench_image_path,
                "question": rephrased_question,
                "gpt4o_response": result['choices'][0]['message']['content']
            }
        else:
            print(f"Error for {key}: {response.text}")
            results[key] = {
                "generated_image": generated_image_path,
                "safety_bench_image": safety_bench_image_path,
                "question": rephrased_question,
                "error": response.text
            }

    # Save results for this JSON file
    output_filename = f"response_{json_filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

    print(f"Responses saved to {output_path}")

print(f"All responses saved in: {OUTPUT_FOLDER}")
