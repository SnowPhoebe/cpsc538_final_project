import os
import json
import re
import matplotlib.pyplot as plt
import numpy as np

# Define the folder paths
outputs_folder = "outputs_all"  # Original LLM responses
# evaluated_folder = "./text_pure_image_typography_image/text_pure_image_typography_image_outputs"  # Pass/Fail evaluation
# evaluated_folder = "./text_pure_image/evaluated_outputs_all"  # Pass/Fail evaluation
# evaluated_folder = "./typography_image_only/typography_image_only_evaluated_outputs"  # Pass/Fail evaluation
evaluated_folder = "./pure_image_typography_image/pure_image_typography_image_evaluated_outputs"  # Pass/Fail evaluation
output_folder = "charts_output"

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Define categories and keywords for Pass/Fail classification
categories = {
    "Pass": r"^\s*pass\b",
    "Unsafe": r"^\s*unsafe\b",
    "Unethical": r"^\s*unethical\b",
    "Harmful": r"^\s*harmful\b",
    "Null": r"^\s*null\b"
}

# Store results for all JSON files
all_category_percentages = {}
refusal_percentages = {}

def analyze_json(file_path, category_name):
    """Analyze the JSON file to compute percentages of Pass, Unsafe, Unethical, Harmful, and refusal-based Pass responses."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    total_entries = len(data)
    category_counts = {key: 0 for key in categories}
    other_count = 0  # Count for unclassified responses

    # refusal_based_pass_count = 0  # Number of "Pass" responses originating from refusals

    # Find corresponding original JSON file
    original_file = os.path.join(outputs_folder, f"gpt4o_responses_{category_name}.json")
    if os.path.exists(original_file):
        with open(original_file, "r", encoding="utf-8") as file:
            original_data = json.load(file)
    else:
        original_data = {}

    for key, response in data.items():
        matched = False
        for category, pattern in categories.items():
            if re.match(pattern, response, re.IGNORECASE):  # Match only at the beginning
                category_counts[category] += 1
                matched = True
                
                # # If "Pass", check if the original response was a refusal
                # if category == "Pass":
                #     original_response = original_data.get(key, {}).get("gpt4o_response", "")
                #     if any(phrase in original_response for phrase in refusal_patterns):
                #         refusal_based_pass_count += 1
                
                break  # Ensure one category per response

        if not matched:
            other_count += 1  # If no match, classify as "Other"

    # Convert counts to percentages
    category_percentages = {key: (count / total_entries) * 100 for key, count in category_counts.items()}
    category_percentages["Other"] = (other_count / total_entries) * 100  # Add "Other" category

    # Compute percentage of Pass responses originating from refusals
    # total_passes = category_counts["Pass"]
    # refusal_percentage = (refusal_based_pass_count / total_passes) * 100 if total_passes > 0 else 0
    # refusal_percentages[category_name] = refusal_percentage

    return category_percentages

# Process all JSON files in the evaluated folder
for filename in os.listdir(evaluated_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(evaluated_folder, filename)
        category_name = filename.replace("evaluated_gpt4o_responses_", "").replace(".json", "")

        # Analyze the JSON file
        category_percentages = analyze_json(file_path, category_name)
        all_category_percentages[category_name] = category_percentages

# **Sort categories in reverse numerical order**
def extract_numeric_prefix(category_name):
    # match = re.match(r"(\d+)_", category_name)  # Extract number at the beginning
    # match = re.search(r"text_only_(\d+)_", category_name)
    # match = re.search(r"evaluated_(\d+)-", category_name)
    match = re.search(r"evaluated_gpt4o_responses_(\d+)_", category_name)
    return int(match.group(1)) if match else float("inf")  # Convert to integer for sorting

# Sort category names in reverse order
category_names = sorted(all_category_percentages.keys(), key=extract_numeric_prefix, reverse=True)
num_categories = len(category_names)

# Extract values for each classification
pass_values = [all_category_percentages[cat]["Pass"] for cat in category_names]
unsafe_values = [all_category_percentages[cat]["Unsafe"] for cat in category_names]
unethical_values = [all_category_percentages[cat]["Unethical"] for cat in category_names]
harmful_values = [all_category_percentages[cat]["Harmful"] for cat in category_names]
null_values = [all_category_percentages[cat]["Null"] for cat in category_names]
other_values = [all_category_percentages[cat]["Other"] for cat in category_names]  # Add "Other"
failed_values = np.array(unsafe_values) + np.array(unethical_values) + np.array(harmful_values)


# # Extract refusal-based pass percentages
# refusal_pass_values = [refusal_percentages[cat] for cat in category_names]

# Define bar positions
y_positions = np.arange(num_categories)

# Color-blind friendly colors (Blue, Orange, Purple, Teal, Gray, Dark Blue)
# colors = ["#0072B2", "#E69F00", "#CC79A7", "#009E73", "#BBBBBB", "#003366"]  #D55E00
# labels = ["Pass", "Unsafe", "Unethical", "Harmful", "Other", "Refusal-Based Pass"]
colors = ["#0072B2", "#E69F00", "#003366"]  #D55E00
labels = ["Pass", "Not Pass", "Refusal-Based Pass"]

# Create the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 8))

# Plot refusal-based pass values on top of Pass
ax.barh(y_positions, null_values,  color=colors[2], label=labels[2])

# Plot base Pass values
ax.barh(y_positions, pass_values, left=np.array(null_values), color=colors[0], label=labels[0])

ax.barh(y_positions, failed_values, left=np.array(pass_values)+ np.array(null_values), color=colors[1], label=labels[1])

# Plot other categories
# ax.barh(y_positions, unsafe_values, left=np.array(pass_values)+ np.array(null_values), color=colors[1], label=labels[1])
# ax.barh(y_positions, unethical_values, left=np.array(pass_values) + np.array(null_values)+ np.array(unsafe_values), color=colors[2], label=labels[2])
# ax.barh(y_positions, harmful_values, left=np.array(pass_values) +np.array(null_values) + np.array(unsafe_values) + np.array(unethical_values), color=colors[3], label=labels[3])
# ax.barh(y_positions, other_values, left=np.array(pass_values) +np.array(null_values) + np.array(unsafe_values) + np.array(unethical_values) + np.array(harmful_values), color=colors[4], label=labels[4])

# Set labels and title
ax.set_yticks(y_positions)
ax.set_yticklabels(category_names, fontsize=12)
ax.set_xlabel("Percentage", fontsize=12)
ax.set_title("Evaluation Results (Refusal-Based Pass Highlighted)", fontsize=14)
ax.set_xlim(0, 100)
ax.legend()

# Improve layout spacing so text is fully visible
plt.subplots_adjust(left=0.3)  

# Save the figure
output_path = os.path.join(output_folder, "refusal_based_pass_chart.png")
plt.savefig(output_path, bbox_inches="tight")
plt.close()

print(f"Updated chart saved as '{output_path}'.")
