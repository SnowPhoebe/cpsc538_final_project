import os
import json
import re
import matplotlib.pyplot as plt
import numpy as np

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
    "Harmful": r"^\s*harmful\b"
}

# Store results for all JSON files
all_category_percentages = {}

def analyze_json(file_path):
    """Analyze the JSON file to compute the percentage of each category, checking only at the beginning of responses."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_entries = len(data)
    category_counts = {key: 0 for key in categories}
    other_count = 0  # Count for unclassified responses

    for value in data.values():
        matched = False
        for category, pattern in categories.items():
            if re.match(pattern, value, re.IGNORECASE):  # Match only at the beginning
                category_counts[category] += 1
                matched = True
                break  # Ensure one category per response
        
        if not matched:
            other_count += 1  # If no match, classify as "Other"

    # Convert counts to percentages
    category_percentages = {key: (count / total_entries) * 100 for key, count in category_counts.items()}
    category_percentages["Other"] = (other_count / total_entries) * 100  # Add "Other" category

    return category_percentages

# Process all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        category_name = filename.replace("evaluated_gpt4o_responses_", "").replace(".json", "")

        # Analyze the JSON file
        category_percentages = analyze_json(file_path)
        all_category_percentages[category_name] = category_percentages

# **Sort categories in reverse numerical order**
def extract_numeric_prefix(category_name):
    match = re.match(r"(\d+)_", category_name)  # Extract number at the beginning
    return int(match.group(1)) if match else float("inf")  # Convert to integer for sorting

# Sort category names in reverse order
category_names = sorted(all_category_percentages.keys(), key=extract_numeric_prefix, reverse=True)
num_categories = len(category_names)

# Extract values for each classification
pass_values = [all_category_percentages[cat]["Pass"] for cat in category_names]
unsafe_values = [all_category_percentages[cat]["Unsafe"] for cat in category_names]
unethical_values = [all_category_percentages[cat]["Unethical"] for cat in category_names]
harmful_values = [all_category_percentages[cat]["Harmful"] for cat in category_names]
other_values = [all_category_percentages[cat]["Other"] for cat in category_names]  # Add "Other"

# Define bar positions
y_positions = np.arange(num_categories)

# Color-blind friendly colors (Blue, Orange, Purple, Teal, Gray)
colors = ["#0072B2", "#E69F00", "#CC79A7", "#009E73", "#BBBBBB"]  
labels = ["Pass", "Unsafe", "Unethical", "Harmful", "Other"]

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 8))
ax.barh(y_positions, pass_values, color=colors[0], label=labels[0])
ax.barh(y_positions, unsafe_values, left=pass_values, color=colors[1], label=labels[1])
ax.barh(y_positions, unethical_values, left=np.array(pass_values) + np.array(unsafe_values), color=colors[2], label=labels[2])
ax.barh(y_positions, harmful_values, left=np.array(pass_values) + np.array(unsafe_values) + np.array(unethical_values), color=colors[3], label=labels[3])
ax.barh(y_positions, other_values, left=np.array(pass_values) + np.array(unsafe_values) + np.array(unethical_values) + np.array(harmful_values), color=colors[4], label=labels[4])

# Set labels and title
ax.set_yticks(y_positions)
ax.set_yticklabels(category_names, fontsize=12)
ax.set_xlabel("Percentage", fontsize=12)
ax.set_title("Evaluation Results Across Categories (Sorted in Reverse Order)", fontsize=14)
ax.set_xlim(0, 100)
ax.legend()

# Improve layout spacing so text is fully visible
plt.subplots_adjust(left=0.3)  

# Save the figure
output_path = os.path.join(output_folder, "reverse_sorted_combined_evaluation_chart.png")
plt.savefig(output_path, bbox_inches="tight")
plt.close()

print(f"Reverse sorted stacked bar chart saved as '{output_path}'.")
