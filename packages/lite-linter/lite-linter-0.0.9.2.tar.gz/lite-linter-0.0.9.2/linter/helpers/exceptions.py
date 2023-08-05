from linter.helpers.format import bold, red


def exception_handler(_, exception, __):
    """
    Override the default exception handler to hide pointless stacktrace
    and hide exception name for linting errors (error text is satisfactory)
    """
    print(exception)


class LintingError(Exception):
    def __init__(self, errors2: dict):
        count = 0

        for x in errors2.values():
            for _ in x:
                count = count + 1

        if count == 1:
            error_title = "There is 1 linting error"
        else:
            error_title = f"🔥 There are {count} linting errors"

        formatted_errors = '\n\n'.join([(x + '\n' +
                                         '\n'.join([('- ' + i) for i in y])) for x, y in
                                        errors2.items()]) + '\n'

        super().__init__(formatted_errors + '\n' + bold(red(error_title)) + '\n')
