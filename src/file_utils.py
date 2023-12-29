import csv
import inspect
import ntpath
import os
from pathlib import Path
from itertools import cycle


class Utils:

    def __init__(self):
        self.root_path = None

    @staticmethod
    def save_list_to_file(lines, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            for line in lines:
                print(str(line).strip(), file=file)

    @staticmethod
    def load_list_from_file(filename, encoding='utf-8', skip_empty=False):
        lines = []
        with open(filename, 'r', encoding=encoding) as file:
            for line in file:
                line = line.strip()
                if line or not skip_empty:
                    lines.append(line)
        return lines

    @staticmethod
    def load_list_from_fp(fp):
        lines = []
        for line in fp.readlines():
            # convert to str, sometimes file pointer has bytes in it
            lines.append(line.decode('utf-8') if isinstance(line, bytes) else line)
        return [l for l in lines if l]

    @staticmethod
    def save_csv_file(output, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(output[0].keys()), delimiter=';')
            writer.writeheader()
            for row in output:
                try:
                    writer.writerow(row)
                except BaseException as e:
                    print(e)
                    raise e

    @staticmethod
    def get_root_module_filename():
        lowest_level = 999
        filename = ''
        caller_module_filename = ''
        caller_module_level = 0
        for i, frame in enumerate(inspect.stack()):
            module = inspect.getmodule(frame[0])
            if module and frame.function == '<module>':
                return module.__file__
            if module:
                dirname = ntpath.dirname(module.__file__)
                level = len(Path(dirname).parents)
                if i == 1:
                    caller_module_filename = module.__file__
                    caller_module_level = level
                if level < lowest_level:
                    lowest_level = level
                    filename = module.__file__
        if lowest_level == caller_module_level:
            return caller_module_filename
        else:
            return filename

    # @staticmethod
    # @functools.lru_cache(maxsize=20)
    def path_from_root(self, dirname: str) -> str:
        """
        Returns a project root path joined with :param dirname:
        The project root is considered the first directory containing 'requirements.txt'
        :param dirname: path to join with
        :return:
        """
        if self.root_path:
            return os.path.join(self.root_path, dirname)
        path = os.path.normpath(__file__)
        max_levels_up = 3
        counter = 0
        while path and counter < max_levels_up:
            parts = os.path.split(path)
            preceeding_part = parts[0]
            tried_filename = os.path.join(preceeding_part, 'requirements.txt')
            if os.path.exists(tried_filename):
                self.root_path = preceeding_part
                return os.path.join(preceeding_part, dirname)
            path = preceeding_part
            counter += 1
            if counter >= max_levels_up:
                self.root_path = preceeding_part
                return os.path.join(preceeding_part, dirname)
        return ''

    @staticmethod
    def load_csv(filename: str):
        import pandas as pd
        from pandas.errors import ParserError

        def _ensure_correct_separator(df: pd.DataFrame, filename: str, separator: str, encoding: str) -> pd.DataFrame:
            head_line = list(df.head(1))
            if len(head_line) == 1:
                correct_separator = ',' if separator == ';' else ';'
                df = pd.read_csv(filename, sep=correct_separator, encoding=encoding)
                head_line = list(df.head(1))
                if len(head_line) == 1:
                    correct_separator = '\t'
                    return pd.read_csv(filename, sep=correct_separator, encoding=encoding)
            return df

        if not os.path.isfile(filename):
            raise FileNotFoundError(f'File not found: {filename}')

        encodings = cycle(['utf8', 'cp1251'])
        separators = cycle([',', ';', '\t'])

        df = None
        iterations = 0
        encoding = next(encodings)
        separator = next(separators)
        while iterations < 10:
            iterations += 1
            try:
                df = pd.read_csv(filename, sep=separator, encoding=encoding)
                return _ensure_correct_separator(df, filename, separator, encoding)
            except Exception as e:
                if isinstance(e, UnicodeDecodeError):
                    encoding = next(encodings)
                elif isinstance(e, ParserError):
                    separator = next(separators)
        return df


def get_file_extension(filename: str) -> str:
    base_name = os.path.basename(filename)
    return os.path.splitext(base_name)[1].lower().replace('.', '')