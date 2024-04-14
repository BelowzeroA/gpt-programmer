import json
import os

def main():
    # Set the path to the dataset directory
    dataset_dir = '/Users/user005/work/testgen/data/github'

    # Get a list of JSON files in the dataset directory
    json_files = [file for file in os.listdir(dataset_dir) if file.endswith('.json')]

    # Load a sample JSON file
    sample_file = os.path.join(dataset_dir, json_files[0])
    with open(sample_file, 'r') as file:
        data = json.load(file)

    # Analyze the structure of the JSON data
    def analyze_json(obj, level=0):
        if isinstance(obj, dict):
            for key, value in obj.items():
                print(f"{'  ' * level}- {key}: {type(value).__name__}")
                analyze_json(value, level + 1)
        elif isinstance(obj, list):
            if len(obj) > 0:
                print(f"{'  ' * level}- List:")
                analyze_json(obj[0], level + 1)
        else:
            print(f"{'  ' * level}- {type(obj).__name__}")

    print("JSON Schema:")
    analyze_json(data)

if __name__ == '__main__':
    main()