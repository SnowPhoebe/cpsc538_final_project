import os
import json
import re
import matplotlib.pyplot as plt

# Define the folder containing the JSON files
folder_path = "evaluated_outputs_all"  # Change this to your folder path
output_folder = "charts_output"

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Define keywords to identify responses starting with specific words
categories = {
    "Pass": r"^\s*pass\b",
    "Unsafe": r"^\s*unsafe\b",
    "Unethical": r"^\s*unethical\b",
    "Harmful": r"^\s*harmful\b",
    "Null": r"^\s*null\b"
}

def analyze_json(file_path):
    """Analyze the JSON file to compute the percentage of each category, checking only at the beginning of responses."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_entries = len(data)
    category_counts = {key: 0 for key in categories}

    for value in data.values():
        for category, pattern in categories.items():
            if re.match(pattern, value, re.IGNORECASE):  # Match only at the beginning
                category_counts[category] += 1
                break  # Ensure one category per response

    # Convert counts to percentages
    category_percentages = {key: (count / total_entries) * 100 for key, count in category_counts.items()}

    return category_percentages

def plot_pie_chart(category_percentages, category_name):
    """Generate and save a pie chart for the given category."""
    labels = list(category_percentages.keys())
    sizes = list(category_percentages.values())
    colors = ["green", "red", "blue", "purple"]  # Assign colors to each category

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    plt.title(f"Evaluation Results for {category_name}")

    # Save the figure
    output_path = os.path.join(output_folder, f"{category_name}.png")
    plt.savefig(output_path)
    plt.close()

# Process all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        category_name = filename.replace("evaluated_gpt4o_responses_", "").replace(".json", "")

        # Analyze the JSON file
        category_percentages = analyze_json(file_path)

        # Generate and save pie chart
        plot_pie_chart(category_percentages, category_name)

print(f"Pie charts saved in '{output_folder}' folder.")
