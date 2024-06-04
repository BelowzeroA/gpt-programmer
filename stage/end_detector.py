import os
import re

def main():
    project_dir = 'c:/Work/projects/zero/verify-fm-backend/be/inference_service/pipelines/vague_narrative/'
    
    comm_detector_path = os.path.join(project_dir, 'comm_detector.py')
    no_names_detector_path = os.path.join(project_dir, 'no_names_detector.py')
    no_subject_detector_path = os.path.join(project_dir, 'no_subject_detector.py')
    
    if not os.path.exists(comm_detector_path):
        print("comm_detector.py file is missing")
        return
    
    if not os.path.exists(no_names_detector_path):
        print("no_names_detector.py file is missing")
        return
    
    if not os.path.exists(no_subject_detector_path):
        print("no_subject_detector.py file is missing")
        return
    
    with open(comm_detector_path, 'r') as file:
        content = file.read()
        if not re.search(r'class\s+VagueNarrativeCommunicationModel', content):
            print("VagueNarrativeCommunicationModel class is missing in comm_detector.py")
            return
    
    with open(no_names_detector_path, 'r') as file:
        content = file.read()
        if not re.search(r'class\s+VagueNarrativeNoNamesModel\(\s*VagueNarrativeCommunicationModel\s*\)', content):
            print("VagueNarrativeNoNamesModel class is missing or not inheriting from VagueNarrativeCommunicationModel in no_names_detector.py")
            return
    
    with open(no_subject_detector_path, 'r') as file:
        content = file.read()
        if not re.search(r'class\s+VagueNarrativeNoSubjectModel\(\s*VagueNarrativeCommunicationModel\s*\)', content):
            print("VagueNarrativeNoSubjectModel class is missing or not inheriting from VagueNarrativeCommunicationModel in no_subject_detector.py")
            return
    
    print("completed")

if __name__ == '__main__':
    main()