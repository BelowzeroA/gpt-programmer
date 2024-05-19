import os
import json
import csv

def is_task_completed(dataset_directory, output_file):
    if not os.path.exists(output_file):
        return False, "Output file does not exist."

    with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames != ['repo_name', 'full_path', 'content']:
            return False, "CSV file does not have the correct columns."

        for row in reader:
            if not all(key in row for key in ['repo_name', 'full_path', 'content']):
                return False, "CSV file rows do not have the correct columns."
            if not row['content'].strip().startswith('public class') and not row['content'].strip().startswith('class'):
                return False, "CSV file contains non-Java code."

    return True, "completed"

def main():
    dataset_directory = 'c:/Work/projects/data/'
    output_file = 'dataset.csv'
    completed, message = is_task_completed(dataset_directory, output_file)
    print(message)

if __name__ == "__main__":
    main()