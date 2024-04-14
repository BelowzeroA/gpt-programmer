
import json
import os


def main():
    # Path to the directory containing JSON dataset files
    dataset_directory = '/path/to/dataset/directory'
    # dataset_directory = "/Users/user005/work/testgen/data/github"

    # Placeholder for findings
    json_structures_report = {
        'objects': 0,
        'arrays': 0,
        'nested_objects': 0,
        'arrays_within_objects': 0,
        'java_code_indicators': 0
    }

    # Function to analyze JSON structures
    def analyze_json_structure(json_data, report):
        if isinstance(json_data, dict):
            report['objects'] += 1
            for key, value in json_data.items():
                if isinstance(value, dict):
                    report['nested_objects'] += 1
                    analyze_json_structure(value, report)
                elif isinstance(value, list):
                    report['arrays_within_objects'] += 1
                    analyze_json_structure(value, report)
                elif key.lower() == 'language' and isinstance(value, str):
                    # print(json_data)
                    if value.lower() == 'java':
                        report['java_code_indicators'] += 1
        elif isinstance(json_data, list):
            report['arrays'] += 1
            for item in json_data:
                analyze_json_structure(item, report)

    # Function to read and analyze JSON files
    def process_json_files(directory, report):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        # Load JSON data
                        json_data = json.load(file)
                        # Analyze JSON structure
                        analyze_json_structure(json_data, report)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from file {file_path}: {e}")

    # Process all JSON files in the dataset directory
    process_json_files(dataset_directory, json_structures_report)

    # Output the findings to a report file
    with open('json_structures_report.txt', 'w', encoding='utf-8') as report_file:
        for structure, count in json_structures_report.items():
            report_file.write(f"{structure}: {count}\n")


if __name__ == "__main__":
    main()