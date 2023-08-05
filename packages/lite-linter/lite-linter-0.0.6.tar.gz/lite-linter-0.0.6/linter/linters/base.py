import os
import sys
from abc import ABC, abstractmethod
from collections import defaultdict

from linter.helpers.exceptions import LintingError, exception_handler
from linter.helpers.format import gray, bold, green


class LintController:
    errors = defaultdict(list)
    warnings = defaultdict(list)

    def output(self):
        sys.excepthook = exception_handler

        if self.errors:
            raise LintingError(self.errors)
        else:
            print(bold(green("\n🤖 HTML looks good to me!\n")))

    def __init__(self, linters):
        base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        templates_directory = f"{base_directory}/templates"

        print('\n')
        print(sys.path[0])
        print(sys.path[1])
        print(os.path.dirname(os.path.realpath(sys.argv[0])))
        print(templates_directory)
        print(os.chdir(os.pardir))
        print(os.path.abspath(__file__))
        print(os.path.abspath(os.path.dirname(__file__)))
        print(os.path.exists('/templates/'))
        print('\n')

        for root, _, files in os.walk(templates_directory):
            for file_name in files:
                if file_name.endswith(".html"):
                    with open(f"{root}/{file_name}") as f:
                        lines = f.readlines()
                        text = '\n'.join(lines)

                        folders_we_care_about = str(root)[len(templates_directory) + 1:] + '/'
                        file_name = file_name
                        key = folders_we_care_about + file_name

                        for linter in linters:
                            linter = linter(key, base_directory, lines, text)
                            linter.lint()

                            for key, value in linter.errors.items():
                                if isinstance(value, str):
                                    value = [value]

                                self.errors[key] = self.errors[key] + value

                            for key, value in linter.warnings.items():
                                if isinstance(value, str):
                                    value = [value]

                                self.warnings[key] = self.warnings[key] + value


class Linter(ABC):
    def __init__(self, file, base_directory, lines, text):
        self.file = file
        self.base_directory = base_directory
        self.lines = lines
        self.text = text
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)

    @abstractmethod
    def lint(self):
        return self.errors, self.warnings

    def append_error(self, error, line_number: int = -1, more_info=""):
        if line_number > 0:
            line_number = gray(" (line " + str(line_number) + ")")
        else:
            line_number = ""

        if more_info:
            more_info = "\n    " + gray(more_info)

        self.errors[self.file].append(error + line_number + more_info)

    def append_warning(self, warning, _, __):
        self.warnings[self.file].append(warning)
