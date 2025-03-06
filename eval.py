import os
import json
import base64
import requests

# Constants
# IMAGE_DIR = "./MM-SafetyBench(imgs)/01-Illegal_Activity/SD"  # Update with actual path
# JSON_FILE = "./processed_questions/01-illegal_activity.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/02-HateSpeech/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/02-HateSpeech.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/03-Malware_Generation/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/03-Malware_Generation.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/04-Physical_Harm/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/04-Physical_Harm.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/05-EconomicHarm/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/05-EconomicHarm.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/06-Fraud/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/06-Fraud.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/07-Sex/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/07-Sex.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/08-Political_Lobbying/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/08-Political_Lobbying.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/09-Privacy_Violence/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/09-Privacy_Violence.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/10-Legal_Opinion/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/10-Legal_Opinion.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/11-Financial_Advice/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/11-Financial_Advice.json"   # Update with actual path
# IMAGE_DIR = "./MM-SafetyBench(imgs)/12-Health_Consultation/SD"  # Update with actual path
# JSON_FILE = "./processed_questions_modified/12-Health_Consultation.json"   # Update with actual path
IMAGE_DIR = "./MM-SafetyBench(imgs)/13-Gov_Decision/SD"  # Update with actual path
JSON_FILE = "./processed_questions_modified/13-Gov_Decision.json"   # Update with actual path
OUTPUT_FILE = "gpt4o_responses.json"        # File to store results
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Load JSON file
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Store results in a dictionary
results = {}

# Iterate over the JSON data
for key, value in data.items():
    print("Processing:", key)
    # if int(key) > 10: break
    image_path = os.path.join(IMAGE_DIR, f"{key}.jpg")
    
    if not os.path.exists(image_path):
        print(f"Warning: Image {image_path} not found. Skipping.")
        continue
    
    # Extract relevant text
    rephrased_question = value.get("Rephrased Question(SD)", "")
    if not rephrased_question:
        print(f"Skipping entry {key} due to missing 'Rephrased Question(SD)'.")
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
            "image": f"{key}.jpg",
            "question": rephrased_question,
            "gpt4o_response": result['choices'][0]['message']['content']
        }
    else:
        print(f"Error for {key}.jpg: {response.text}")
        results[key] = {
            "image": f"{key}.jpg",
            "question": rephrased_question,
            "error": response.text
        }

# Save results to a JSON file
with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, indent=4)

print(f"All responses saved to {OUTPUT_FILE}")
