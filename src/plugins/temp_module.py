from inline_functions import __ask_human__
import os
import json

def analyze_json_structure(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        # Print the structure of the JSON file for analysis
        print(json.dumps(data, indent=4, sort_keys=True))

def main():
    # Check if the dataset directory path is known
    try:
        dataset_directory = __ask_human__("What is the path to the dataset directory?")
    except NameError:
        # If the __ask_human__ function is not available, set a default path
        dataset_directory = './dataset'  # Replace with the actual path if known

    # Check if the directory exists
    if not os.path.exists(dataset_directory):
        raise FileNotFoundError(f"The directory {dataset_directory} does not exist.")

    # List all files in the directory
    json_files = [f for f in os.listdir(dataset_directory) if f.endswith('.json')]

    # Analyze the structure of the first few JSON files
    for json_file in json_files[:3]:  # Adjust the number of files to analyze as needed
        file_path = os.path.join(dataset_directory, json_file)
        print(f"Analyzing the structure of {json_file}:")
        analyze_json_structure(file_path)
        print("\n")

if __name__ == "__main__":
    main()