import os.path

import pandas as pd
from tqdm import tqdm

from base_plugin import BasePlugin
import plugins # This is a hack to make sure all plugins are loaded
from gpt_api import GPTApi
from gpt_prompt_manager import GPTPromptManager
from file_utils import get_file_extension

OPERATION_SELECT_COLUMNS = 'select_columns'
OPERATION_PROCESS_ROW = 'process_row'
OPERATION_BUILD_PLAN = 'build_plan'


class TableTaskSolver:

    def __init__(self, table_filename: str, task_description, logger):
        self.table_filename = table_filename
        self.task_description = task_description
        self.logger = logger
        self.api = GPTApi(self.logger)
        self.prompt_manager = GPTPromptManager(self.api, self.logger)
        self.plugins = self.load_plugins()

    def load_plugins(self):
        # Collect all subclasses of BasePlugin
        # For each plugin, create an instance and store it in a dict
        result = {}
        for plugin_class in BasePlugin.__subclasses__():
            plugin = plugin_class(self.logger)
            result[plugin_class.name] = plugin
        return result

    def select_columns(self, table: pd.DataFrame):
        params = {"columns": list(table.columns), "task": self.task_description}
        columns = self.prompt_manager.generate_parse(
            operation=OPERATION_SELECT_COLUMNS,
            params=params
        )

        return columns

    def check_conditions(self):
        result = {"status": "success"}
        if os.path.isfile(self.table_filename) is False:
            result["status"] = "error"
            result["error_message"] = "File not found: " + self.table_filename
            return result

        try:
            extension = get_file_extension(self.table_filename)
            if extension == "csv":
                table = pd.read_csv(self.table_filename)
            elif extension in ["xlsx", "xls"]:
                table = pd.read_excel(self.table_filename, engine="openpyxl")
            else:
                result["status"] = "error"
                result["error_message"] = "Unsupported file format: " + extension
                return result
        except Exception as e:
            result["status"] = "error"
            result["error_message"] = f"Error loading file: {e}"
            return result

        result["source_table"] = table
        return result

    def solve(self):
        result = self.check_conditions()
        if result["status"] == "error":
            return result

        table = result["source_table"]
        selected_columns = self.select_columns(table)
        row_condition = self.row_condition()
        processing_result = {}
        try:
            self.process_table(table, selected_columns, processing_result)
        except Exception as e:
            result["status"] = "error"
            result["error_message"] = f"Error while processing table: {e}"
            return result

        for key in processing_result:
            table[key] = processing_result[key]
        result["result_table"] = table
        return result

    def row_condition(self):
        return None

    def get_row_data(self, row, selected_columns):
        data = {}
        for column in selected_columns:
            value = row[column]
            data[column] = value
        return data

    def process_table(self, table, selected_columns, processing_result):
        plan = self.build_plan(selected_columns)
        table_dict = table.to_dict(orient="records")
        for i, row in tqdm(enumerate(table_dict), total=len(table_dict)):
            row_data = self.get_row_data(row, selected_columns)
            row_result = self.process_row(row_data, plan)
            try:
                self.update_row(processing_result, row_result)
            except Exception as e:
                self.logger.error(f"Error while processing row {i}: {e}")
        s = 0

    def process_row(self, row_data, plan):
        interop_data = row_data
        for i, plan_op in enumerate(plan):
            interop_data = self.process_row_operation(
                interop_data,
                params=plan_op,
                last_operation=i == len(plan) - 1
            )
            if interop_data is None:
                return None
        return interop_data

    def build_plan(self, selected_columns):
        params = {"columns": selected_columns, "task": self.task_description}
        plan = self.prompt_manager.generate_parse(
            operation=OPERATION_BUILD_PLAN,
            params=params,
            max_tokens=500
        )

        return plan

    def process_row_operation(self, data, params: dict, last_operation=False):
        plugin_name = params["plugin"]
        if plugin_name is None:
            if (params["operation"].startswith("Insert") or last_operation) \
                    and params["input_source"] == "PreviousOperation":
                return self.insert_result(data, params)
            plugin_name = "chat_gpt"

        if plugin_name not in self.plugins:
            raise AttributeError(f"Plugin not found: {plugin_name}")

        plugin = self.plugins[plugin_name]

        return plugin.run(data, params)

    def insert_result(self, data, params):
        if len(params["columns"]) == 0:
            return None
        column = params["columns"][0]
        return {column: data}

    def update_row(self, processing_result, row_result):
        if row_result is None and len(processing_result) == 0:
            return
        if row_result is None:
            for key in processing_result:
                processing_result[key].append("")
            return
        if isinstance(row_result, dict):
            for key in row_result:
                if key not in processing_result:
                    processing_result[key] = []
                processing_result[key].append(row_result[key])
