import os
import json
import base64
import requests
from pathlib import Path
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Match images with JSON questions and query GPT-4o API')
    parser.add_argument('--img_dir', type=str, default='SD', help='Directory containing the images')
    parser.add_argument('--json_file', type=str, default='01-Illegal_Activitiy.json', help='JSON file with questions')
    parser.add_argument('--api_key', type=str, required=True, help='Your OpenAI API key')
    parser.add_argument('--output_dir', type=str, default='results', help='Directory to save results')
    return parser.parse_args()

def encode_image(image_path):
    """Encode image to base64 for API submission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_json_data(json_file):
    """Load the JSON data from file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def call_gpt4o_api(api_key, base64_image, prompt):
    """Make an API call to GPT-4o with the image and prompt"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def main():
    args = parse_arguments()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load JSON data
    json_data = load_json_data(args.json_file)
    
    # Get list of image files
    image_dir = Path(args.img_dir)
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
    
    # Process each image
    for img_file in image_files:
        # Extract the image ID (assuming filenames like '0.jpg', '1.jpg', etc.)
        img_id = os.path.splitext(img_file)[0]
        
        # Check if this ID exists in the JSON data
        if img_id in json_data:
            print(f"Processing image: {img_file}")
            
            # Get the rephrased question
            rephrased_question = json_data[img_id].get("Rephrased Question(SD)", "")
            
            if rephrased_question:
                # Encode the image
                image_path = image_dir / img_file
                base64_image = encode_image(image_path)
                
                # Call the GPT-4o API
                response = call_gpt4o_api(args.api_key, base64_image, rephrased_question)
                
                # Save the response
                output_file = Path(args.output_dir) / f"{img_id}_response.json"
                with open(output_file, 'w') as f:
                    json.dump(response, f, indent=2)
                
                # Print the response text for convenience
                if "choices" in response and len(response["choices"]) > 0:
                    message_content = response["choices"][0]["message"]["content"]
                    print(f"Response for {img_file}:\n{message_content}\n")
                else:
                    print(f"Error or unexpected response format for {img_file}: {response}\n")
            else:
                print(f"No 'Rephrased Question(SD)' found for image {img_file}")
        else:
            print(f"No matching data found for image {img_file}")

if __name__ == "__main__":
    main()