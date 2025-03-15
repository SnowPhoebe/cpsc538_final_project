import os
import json
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Constants
JSON_FILE = "./processed_questions/01-illegal_activity.json"  # Update with actual path
OUTPUT_FILE = "typography_image_gpt4o_responses.json"        # File to store results
IMAGE_SAVE_DIR = "./generated_images/"      # Directory to save images
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Ensure the image save directory exists
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

# Load JSON file
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


def create_typography_image(text, image_name):
    """Generates and saves an image with the given text in a typography style."""
    img_width = 600  # Fixed width
    background_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text
    padding = 20  # Space around text

    # Load a font (adjust path or install fonts as needed)
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)

    # Word wrapping to prevent overflow
    max_width = img_width - 2 * padding
    lines = []
    words = text.split()
    current_line = ""

    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))  # Temporary draw object

    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = text_bbox[2] - text_bbox[0]  # Calculate text width

        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)  # Add the last line

    # Calculate required height dynamically
    line_height = font_size + 10  # Line spacing
    img_height = padding * 2 + len(lines) * line_height

    # Create the final image
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # Draw text line by line
    y_start = padding
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (img_width - text_width) // 2
        draw.text((x, y_start), line, fill=text_color, font=font)
        y_start += line_height

    # Save image
    image_path = os.path.join(IMAGE_SAVE_DIR, image_name)
    img.save(image_path)

    # Convert image to base64
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    return base64.b64encode(img_bytes.getvalue()).decode("utf-8"), image_name


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

    # Generate typography image and save it
    image_name = f"{key}.jpg"
    image_base64, saved_image_path = create_typography_image(rephrased_question, image_name)

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
            "image": saved_image_path,
            "question": rephrased_question,
            "gpt4o_response": result['choices'][0]['message']['content']
        }
    else:
        print(f"Error for {key}: {response.text}")
        results[key] = {
            "image": saved_image_path,
            "question": rephrased_question,
            "error": response.text
        }

# Save results to a JSON file
with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, indent=4)

print(f"All responses saved to {OUTPUT_FILE}")
print(f"Typography images are saved in: {IMAGE_SAVE_DIR}")
