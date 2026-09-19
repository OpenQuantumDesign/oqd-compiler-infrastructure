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
        error_report = (
            f"\n{f' {self.__class__.__name__} Report ':=^100}\n"
            + "\n".join(
                [
                    self.error_message_formatter(n + 1, e)
                    for n, e in enumerate(self.errors)
                ]
            )
            + f"\n{'=' * 100}\n"
        )

        return error_report

    def __str__(self):
        return self.__repr__()

    @abstractmethod
    def error_message_formatter(self, idx: int, error: Exception) -> str: ...

    @abstractmethod
    def report_errors(self, *args, **kwargs): ...


class DefaultErrorCollector(ErrorCollector):
    def error_message_formatter(self, idx: int, error: Exception) -> str:
        return f"({idx}) {error.__class__.__name__}: {str(error)}"

    def report_errors(self, *args, **kwargs):
        if self:
            raise self._error_class(self.__repr__())
