from inline_functions import __ask_human__
import os
import json

def main():
    # Define the directory where the dataset files are located
    dataset_directory = __ask_human__("What is the path to the dataset directory?")
    
    # Get a list of files in the directory
    try:
        dataset_files = os.listdir(dataset_directory)
    except FileNotFoundError:
        print(f"Directory {dataset_directory} not found.")
        return
    
    # Select a subset of files for analysis
    subset_files = dataset_files[:5]  # Analyze the first 5 files for example
    
    # Analyze the structure of the files
    for file_name in subset_files:
        file_path = os.path.join(dataset_directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                # Load the content of the file as JSON
                data = json.load(file)
                
                # Since the structure is unknown, print out the type of the data
                # and keys if it's a dictionary
                print(f"File: {file_name}")
                print(f"Type of data: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print("List of items, the structure of items:")
                    if data:
                        if isinstance(data[0], dict):
                            print(f"Keys of the first item: {list(data[0].keys())}")
                print("\n")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {file_name}")

if __name__ == "__main__":
    main()