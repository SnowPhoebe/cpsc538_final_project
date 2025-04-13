import os
import json
import base64
import time

import requests
from openai import OpenAI
import openai
client = OpenAI(api_key = "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")
# Constants
IMAGE_DIR = "./MM-SafetyBench(imgs)/01-Illegal_Activitiy/SD"
JSON_FILE = "./processed_questions/"
OUTPUT_FILE = "_dalle_image_outputs.json"
API_URL = "https://api.openai.com/v1/images/generations"
API_KEY = "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"

Json = ["02-HateSpeech"]

# Function to encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

for json_file in Json:
    new_json = JSON_FILE + json_file + ".json"
    with open(new_json, "r", encoding="utf-8") as f:
        data = json.load(f)




    # Store results in a dictionary
    results = {}

    for key, value in data.items():
        time.sleep(15)
        print("Processing:", key)
        """
        if not os.path.exists(image_path):
            print(f"Warning: Image {image_path} not found. Skipping.")
            continue
        """
        rephrased_question = value.get("Question", "")
        if not rephrased_question:
            print(f"Skipping entry {key} due to missing 'Rephrased Question(SD)'.")
            continue


        #image_base64 = encode_image(image_path)

        try:
            payload = client.images.generate(
                model="dall-e-3",
                prompt=rephrased_question,
                #image = f"data:image/jpeg;base64,{image_base64}",
                n=1,
                size="1024x1024",
                quality="standard",
            )


            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            res = payload.data[0].url

            results[key] = {
                "image": f"{key}.jpg",
                "question": rephrased_question,
                "generated_image_url": res
            }
        except openai.BadRequestError as e:
            results[key] = {
                "image": None,
                "question": rephrased_question,
                "generated_image_url": "fail"
            }
    output_file = json_file+OUTPUT_FILE

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

    print(f"All generated images saved to {output_file}")
