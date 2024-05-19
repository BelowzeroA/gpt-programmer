import os
import json

def investigate_json_structure(json_data, level=1, structure=None):
    if structure is None:
        structure = {}

    if level <= 3:
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, dict):
                    structure[key] = {}
                    investigate_json_structure(value, level + 1, structure[key])
                elif isinstance(value, list):
                    structure[key] = []
                    structure[key].append({})
                    if value:
                        investigate_json_structure(value[0], level + 1, structure[key][0])
                else:
                    if isinstance(value, str):
                        structure[key] = value[:50]
                    else:
                        structure[key] = value
        elif isinstance(json_data, list):
            if json_data:
                investigate_json_structure(json_data[0], level, structure)

    return structure

def main():
    dataset_dir = "c:/Work/projects/data/"
    report_file = "report.txt"

    # Investigate directory structure
    dir_structure = []
    for root, dirs, files in os.walk(dataset_dir):
        dir_structure.append(f"Directory: {root}")
        dir_structure.append(f"  Subdirectories: {dirs}")
        dir_structure.append(f"  Files: {files}")

    # Investigate JSON file structure
    json_files = [file for file in os.listdir(dataset_dir) if file.endswith(".json")]
    json_structure = {}
    for json_file in json_files[:3]:
        with open(os.path.join(dataset_dir, json_file), "r") as file:
            json_data = json.load(file)
            json_structure[json_file] = investigate_json_structure(json_data)

    # Write investigation results to report file
    with open(report_file, "w") as file:
        file.write("Directory Structure:\n")
        file.write("\n".join(dir_structure))
        file.write("\n\nJSON File Structure:\n")
        file.write(json.dumps(json_structure, indent=2))

if __name__ == "__main__":
    main()