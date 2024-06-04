from environment import Environment


def main():
    # task = """
    # Write a parser of dataset in json format. The dataset consists of multiple files in a directory. Each file contains some code in multiple languages. The structure of the files is unknown, you need to determine it first.
    # The task is to write a python module that does extract all code in java and put it in a single csv file with the following columns: repo_name, full_path, content.
    # Note: files of the dataset can be huge, don't print them to the console.
    # """
    task = """
    Write a parser of dataset in json format. The dataset consists of multiple files in a directory. Each file contains some code in multiple languages. The structure of the files is unknown, you need to determine it first.
    The task is to write a python module that extracts all code in java and put it in a single csv file with the following columns: repo_name, full_path, content.
    The end result is a python module that implements the above task and stores the result in file "dataset.csv".
    """
    task = """
    Rebuild a program module and create a new structure of three modules.
    Current state: 
    module inference_comm.py has 
    1) logic of identifying  narratives with communication
    2) logic of identifying  narratives with communication and no names
    3) boilerplate stuff of manipulating incoming data
    
    The overall goal is to make three modules with three classes instead of one:
    comm_detector.py - class VagueNarrativeCommunicationModel that identifies narratives with communication 
    and all boilerplate from inference_comm.py. Names must not be considered in this module
    no_names_detector.py - class VagueNarrativeNoNamesModel inherited from VagueNarrativeCommunicationModel that 
    identifies narratives with communication and no names
    no_subject_detector.py - class VagueNarrativeNoSubjectModel inherited from VagueNarrativeCommunicationModel that
    identifies narratives with communication and no subject. "No subject" means that the narrative does not contain 
    snippets " re ", " re: " or " regarding "
    No boilerplate should be in these two inherited classes, like predict() method, etc.
    """
    # task = """
    # Write an article about expanded clay concrete. Provide specific details such as grades, density,
    # composition, thermal conductivity, types, comparison with other types of concrete.
    # """
    env = Environment()
    env.run(task)


if __name__ == "__main__":
    main()