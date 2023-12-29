from gpt_programmer import GptProgrammer


def main():
    task = """
    Write a parser of dataset in json format. The dataset consists of multiple files in a directory. Each file contains some code in multiple languages. The structure of the files is unknown, you need to determine it first. 
    The task is to write a python module that does extract all code in java and put it in a single csv file with the following columns: repo_name, full_path, content.
    """
    programmer = GptProgrammer()
    programmer.run(task)


if __name__ == "__main__":
    main()