import json

files = ["01_dalle_image_outputs.json","02_dalle_image_outputs.json","03_dalle_image_outputs.json","04_dalle_image_outputs.json","05_dalle_image_outputs.json","06_dalle_image_outputs.json","07_dalle_image_outputs.json","08_dalle_image_outputs.json","09_dalle_image_outputs.json","10_dalle_image_outputs.json","11_dalle_image_outputs.json","12_dalle_image_outputs.json","13_dalle_image_outputs.json"]

for file in files:
    with open(file, "r", encoding="utf-8") as file:
        data = json.load(file)


    total_count = 0
    success_count = 0

    for key, value in data.items():
        total_count += 1
        if value.get("generated_image_url") != "fail":
            success_count += 1


    success_rate = 100 - (success_count / total_count) * 100
    print(f"file:{file}")
    print(f"total_count: {total_count}")
    print(f"success_count: {success_count}")
    print(f"success_rate: {success_rate:.2f}%")
