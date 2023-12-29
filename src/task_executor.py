from datetime import datetime
import os

import time

from file_utils import Utils, get_file_extension
from logger import Logger
from table_task_solver import TableTaskSolver
from task_queue import TaskQueue, Task

utils = Utils()
results_dir = utils.path_from_root('data/results')


class TaskExecutor:

    def __init__(self, logger):
        self.logger = logger
        self.queue = TaskQueue()

    @staticmethod
    def ensure_result_filename(task: Task):
        target_dir = f'{results_dir}/{task.chat_id}'
        os.makedirs(target_dir, exist_ok=True)
        extension = get_file_extension(task.filename)
        filename = f'result_{task.task_id:06}.{extension}'
        task.result_filename = f'{task.chat_id}/{filename}'
        task.result_fullname = f'{target_dir}/{filename}'

    def polling(self):
        while True:
            for task in self.queue.get_uncompleted_tasks():
                self.ensure_result_filename(task)
                self.process_task(task)
            time.sleep(5)

    def process_task(self, task: Task):
        print(f"Processing task {task.task_id}")
        solver = TableTaskSolver(task.filename, task.description, self.logger)
        logger.info(f"Solving task {task.task_id}")

        task.status = 'being processed'
        self.queue.session.commit()

        result = solver.solve()
        if result['status'] == 'error':
            task.status = 'error'
            task.error_message = result['error_message']
            self.queue.session.commit()
            return

        result_table = result['result_table']
        extension = get_file_extension(task.result_filename)
        if extension in ['xlsx', 'xls']:
            result_table.to_excel(task.result_fullname, index=False)
        elif extension == 'csv':
            result_table.to_csv(task.result_fullname, index=False)
        task.complete = 1
        task.completion_time = datetime.now()
        task.status = 'completed'
        self.queue.session.commit()
        print(f"Task {task.task_id} completed")


if __name__ == "__main__":
    log_dir = utils.path_from_root("logs")
    logger = Logger(os.path.join(log_dir, "task_executor.log"))
    executor = TaskExecutor(logger)
    executor.polling()
