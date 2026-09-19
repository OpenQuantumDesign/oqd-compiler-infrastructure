import types
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import MutableSequence

########################################################################################


class ErrorCollectorMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        created_class = super().__new__(cls, name, bases, namespace)

        created_class._error_class = types.new_class(
            f"_{name}Report",
            (Exception,),
            {},
            lambda ns: ns.update({"__module__": created_class.__module__}),
        )

        return created_class


class ErrorCollector(ABC, MutableSequence[Exception], metaclass=ErrorCollectorMeta):
    def __init__(self):
        self.errors = []

    def __bool__(self):
        return bool(self.errors)

    def __len__(self):
        return len(self.errors)

    def __getitem__(self, idx):
        return self.errors[idx]

    def __setitem__(self, idx, value):
        self.errors[idx] = value

    def __delitem__(self, idx):
        del self.errors[idx]

    def insert(self, idx, value):
        self.errors.insert(idx, value)

    def __repr__(self):
        error_report = "\n  " + "\n  ".join(
            map(self.error_message_formatter, self.errors)
        )

        return error_report

    def __str__(self):
        return self.__repr__()

    @abstractmethod
    def error_message_formatter(self, error: Exception) -> str: ...

    @abstractmethod
    def report_errors(self): ...


class DefaultErrorCollector(ErrorCollector):
    def error_message_formatter(self, error: Exception) -> str:
        return f"\033[1;31m{error.__class__.__name__}\033[0m: {str(error)}"

    def report_errors(self):
        if self:
            raise self._error_class(self.__repr__())
