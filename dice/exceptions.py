from pyparsing import ParseException, ParseFatalException


class DiceBaseException(Exception):
    @classmethod
    def from_other(cls, other):
        if isinstance(other, ParseException):
            cls = DiceException
        elif isinstance(other, ParseFatalException):
            cls = DiceFatalException

        new = cls(*other.args)
        return new

    def pretty_print(self):
        string, location, description = self.args
        lines = string.split('\n')

        if len(description) < (self.col - 1):
            errline = (description + ' ^').rjust(self.col)
        else:
            errline = '^ '.rjust(self.col + 1) + description

        lines.insert(self.lineno + 1, errline)
        return '\n'.join(lines)


class DiceException(DiceBaseException, ParseException):
    pass


class DiceFatalException(DiceBaseException, ParseFatalException):
    pass
