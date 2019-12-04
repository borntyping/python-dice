from pyparsing import ParseException, ParseFatalException


class DiceBaseException(Exception):
    @classmethod
    def from_other(cls, other):
        if isinstance(other, ParseException):
            return DiceException(*other.args)
        elif isinstance(other, ParseFatalException):
            return DiceFatalException(*other.args)
        return cls(*other.args)

    def pretty_print(self):
        string, location, description = self.args
        lines = string.split("\n")

        if len(description) < (self.col - 1):
            line = (description + " ^").rjust(self.col)
        else:
            line = "^ ".rjust(self.col + 1) + description

        lines.insert(self.lineno + 1, line)
        return "\n".join(lines)


class DiceException(DiceBaseException, ParseException):
    pass


class DiceFatalException(DiceBaseException, ParseFatalException):
    pass
