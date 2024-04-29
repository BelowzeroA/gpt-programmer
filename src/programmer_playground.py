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
    # task = """
    # Write an article about expanded clay concrete. Provide specific details such as grades, density,
    # composition, thermal conductivity, types, comparison with other types of concrete.
    # """
    env = Environment()
    env.run(task)


if __name__ == "__main__":
    main()