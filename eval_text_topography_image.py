import os
import json
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Constants
JSON_FILE = "./processed_questions/01-illegal_activity.json"  # Update with actual path
OUTPUT_FILE = "gpt4o_responses.json"        # File to store results
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

# Load JSON file
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to create a typography image
def create_typography_image(text):
    """Generates an image with the given text in a typography style."""
    img_width, img_height = 600, 300  # Set image size
    background_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text

    # Create a blank image
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # Load a font (adjust path or install fonts as needed)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust for Windows/Mac
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)

    # Get text size
    text_width, text_height = draw.textsize(text, font=font)

    # Calculate position (center the text)
    x = (img_width - text_width) // 2
    y = (img_height - text_height) // 2

    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)

    # Convert image to base64
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")

# Store results in a dictionary
results = {}

# Iterate over the JSON data
for key, value in data.items():
    print("Processing:", key)

    # Extract relevant text
    rephrased_question = value.get("Changed Question", "")
    if not rephrased_question:
        print(f"Skipping entry {key} due to missing 'Changed Question'.")
        continue

    # Generate typography image
    image_base64 = create_typography_image(rephrased_question)

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
    if response.status_code == 200:
        result = response.json()
        results[key] = {
            "image": f"Generated for {key}",
            "question": rephrased_question,
            "gpt4o_response": result['choices'][0]['message']['content']
        }
    else:
        print(f"Error for {key}: {response.text}")
        results[key] = {
            "image": f"Generated for {key}",
            "question": rephrased_question,
            "error": response.text
        }

# Save results to a JSON file
with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, indent=4)

print(f"All responses saved to {OUTPUT_FILE}")
