from environment import Environment


def main():

    tasks = [
        """
    Write a parser of dataset in json format. The dataset consists of multiple files in a directory. Each file contains some code in multiple languages. The structure of the files is unknown, you need to determine it first.
    The task is to write a python module that extracts all code in java and put it in a single csv file with the following columns: repo_name, full_path, content.
    The end result is a python module that implements the above task and stores the result in file "dataset.csv".
    """,
    """
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
    """,
    # """
    # # Write an article about expanded clay concrete. Provide specific details such as grades, density,
    # # composition, thermal conductivity, types, comparison with other types of concrete.
    # # """
    """
    rewrite a JS script to Python. No running or testing is required.
    Save the result to a .py file in the same directory.
    """,
    """
    (from https://www.upwork.com/jobs/~01e2c4bd59f6afc1d6)
    Simple python script that queries the USPTO for patents and trademarks associated with companies 
    (Openai, Microsoft, Apple, Nvidia, etc...) and keywords (AI, LLM, Artificial Intelligence, Neural network, etc...) 
    every 30 or so seconds (depending on API limitations) and alerting me to new postings and providing the details 
    on those postings.  
    """,
"""
    (from https://www.upwork.com/jobs/~016fab4a172fcab5e0)
    I have a spreadsheet of about 5,000 entries with Column A (Stock Symbol) and Column B (Company Name). 
    I need a simple and efficient solution that will read in a headline from a newspaper or blog and output the relevant stock tickers mentioned in the title.
Requirements:

The solution should be able to handle various forms of company names in the headlines, including:

Punctuation (e.g., "Paramount's" should match "Paramount")
Shortened names (e.g., "Abercrombie" should match "Abercrombie & Fitch Company")
Partial names (e.g., "Paramount" should match "Paramount Entertainment")


The solution should minimize false positives by accurately distinguishing between common words and company names.
The output should include the stock symbol(s) of the identified company(ies).
The solution should be able to process a large number of headlines efficiently.
The code should be well-documented and easy to maintain.

MAIN THING IS IT SHOULD BE ACCURATE, IN PYTHON, AND FAST.  

Deliverables:

A script or program that takes a headline as input and outputs the corresponding stock symbol(s).
A brief report explaining the approach, algorithms, or libraries used to solve the problem.
Instructions on how to run the script or program.
    """,

    """
    (from https://www.upwork.com/jobs/~0142bebcd3cfe02f26)
    We need to improve an existing python script that fetches  product data from the website coop.ch and store it in our existing PostgreSQL database. Currently we are using python requests and get a 403 error. The script should avoid bot detection mechanisms and include logic to extract the price per unit for each product.

Acceptance Criteria:

all existing columns +
category (new column)
price_per_unit (new column)

Data is stored in the coop table in our PostgreSQL database.
Script handles bot detection (e.g., using Selenium or similar for JavaScript rendering).
Script includes error handling and logging.
Script updates existing records in the database to avoid duplicates.
Detailed comments are included in the code for maintainability.
    """,
    """
    (from https://www.upwork.com/jobs/~016fab4a172fcab5e0)
    The previous task was stated as follows:
    ---
    I need a simple and efficient solution that will read in a headline from a newspaper or blog and output the relevant stock tickers mentioned in the title.
    Requirements:

    The solution should be able to handle various forms of company names in the headlines, including:

    Punctuation (e.g., "Paramount's" should match "Paramount")
    Shortened names (e.g., "Abercrombie" should match "Abercrombie & Fitch Company")
    Partial names (e.g., "Paramount" should match "Paramount Entertainment")

    The solution should minimize false positives by accurately distinguishing between common words and company names.
    The output should include the stock symbol(s) of the identified company(ies).
   ---
   You wrote a module that you stored in c:\Work\projects\stage\headline_to_ticker.py
   After examining the module, I found the following issues:
   1. You need to eliminate common words from the list of company names you read from the csv file. For example, "Apple Inc" should be "Apple".
   Use the cleanco library to clean the company names.
   2. The matching function should produce a score based on how many words from the company name are in the headline. The score should be normalized to the length of the company name.
    3. The selecting function should return best matches with scores higher than some threshold.
    Rework the module to fix these issues and save it in c:\Work\projects\stage\headline_to_ticker_v2.py  
    
    Also write a unit test module for the selecting function. Use this headline as a test case:
    "What next for Paramount Global after merger talks with Skydance Media break down?" 
    """,
    ]
    env = Environment()
    state = env.run_dialog(tasks[4])
    response = "c:/Work/projects/stage/tickers.csv"
    state = env.run_dialog({"init_state": "user_response", "response": response})
    response = """
    You wrote a module that you stored in c:\Work\projects\stage\ folder.
   After examining the module, I found the following issues:
   1. You need to eliminate common words from the list of company names you read from the csv file. For example, "Apple Inc" should be "Apple".
   Use the cleanco library to clean the company names.
   2. The matching function should produce a score based on how many words from the company name are in the headline. The score should be normalized to the length of the company name.
    3. The selecting function should return best matches with scores higher than some threshold.
    Rework the module to fix these issues and save it in c:\Work\projects\stage\headline_to_ticker_v2.py  
    
    Also write a unit test module for the selecting function. Use this headline as a test case:
    "What next for Paramount Global after merger talks with Skydance Media break down?" 
"""
    state = env.run_dialog({"init_state": "new_phase", "response": response})


if __name__ == "__main__":
    main()