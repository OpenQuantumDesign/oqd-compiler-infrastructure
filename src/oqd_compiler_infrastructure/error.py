# Copyright 2024-2025 Open Quantum Design

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
