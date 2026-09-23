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

import re
from functools import wraps
from inspect import FullArgSpec, getfullargspec
from types import new_class
from typing import Callable, Literal

from oqd_compiler_infrastructure.rule import ConversionRuleBase, RewriteRule

########################################################################################


def _gen_rule_init(
    cls_name: str,
    argspec: FullArgSpec,
    conversion: bool = False,
):
    """
    Helper function for creating the __init__ for a generated rule supporting arguments
    verification
    """

    rule_num_args = 2 if conversion else 1

    args = argspec.args[rule_num_args:]
    kwargs = argspec.kwonlyargs
    default_args = argspec.defaults
    default_kwargs = argspec.kwonlydefaults
    default_args = default_args if default_args else []
    default_kwargs = default_kwargs if default_kwargs else {}

    def __init__(self, *_args, **_kwargs):
        super(self.__class__, self).__init__()

        self._args = []
        self._kwargs = {}

        # Set args and kwargs

        if len(_args) > len(args):
            raise TypeError(
                f"{cls_name}() takes {len(args)} positional arguments but {len(_args)} were given"
            )

        for n in range(len(_args)):
            setattr(self, args[n], _args[n])
            self._args.append(_args[n])

        for k in _kwargs:
            if hasattr(self, k):
                raise TypeError(f"{cls_name}() got multiple values for argument '{k}'")
            if k not in kwargs:
                raise TypeError(
                    f"{cls_name}() got an unexpected keyword argument '{k}'"
                )
            setattr(self, k, _kwargs[k])
            self._args.append(_kwargs[k]) if k in args else self._kwargs.update(
                {k: _kwargs[k]}
            )

        # Missing args and kwargs

        missing_args = set(args[len(self._args) : len(args) - len(default_args)])
        missing_kwargs = (
            set(kwargs).difference(default_kwargs).difference(self._kwargs.keys())
        )

        if missing_args or missing_kwargs:
            msg = "\n".join(
                [
                    (
                        f"{cls_name}() missing {len(missing_args)} required positional argument: {missing_args}"
                        if missing_args
                        else ""
                    ),
                    (
                        f"{cls_name}() missing {len(missing_kwargs)} required keyword-only argument: {missing_kwargs}"
                        if missing_kwargs
                        else ""
                    ),
                ]
            ).strip()
            raise TypeError(msg)

        # Set default values for args and kwargs

        for n in range(len(_args), len(args)):
            setattr(self, args[n], default_args[len(_args) - n])
            self._args.append(default_args[len(_args) - n])

        for k in kwargs:
            if not hasattr(self, k) and default_kwargs.get(k, None):
                setattr(self, k, default_kwargs[k])
                self._kwargs.update({k: default_kwargs[k]})

    return __init__


def gen_rewrite_pass(
    func: Callable = None, *, rewriter=None, walk=None, return_pass: bool = False
):
    """
    Decorator used to turn a function into a rewrite rule by considering the function as
    generic_map, the first argument is the model and the remaining arguments are rewrite rule
    arguments
    """
    rewriter = rewriter if rewriter else lambda rule: rule
    walk = walk if walk else lambda rule: rule

    def _decorator(_func):
        argspec = getfullargspec(_func)

        _pre = re.search("^(_*)", _func.__name__).group()
        _post = re.search("(_*)$", _func.__name__).group()
        body = re.findall("([a-zA-Z0-9]+)", _func.__name__)

        cls_name = (
            _pre + "".join(map(lambda s: s.capitalize(), body)) + "RewriteRule" + _post
        )

        rule = new_class(
            cls_name,
            (RewriteRule,),
            {},
            lambda ns: ns.update(
                {
                    "__module__": _func.__module__,
                    "__wrapped__": staticmethod(_func),
                    "generic_map": lambda self, model: _func(
                        model, *self._args, **self._kwargs
                    ),
                    "__init__": _gen_rule_init(
                        cls_name=cls_name, argspec=argspec, conversion=False
                    ),
                }
            ),
        )

        @wraps(_func)
        def pass_(*args, **kwargs):
            if return_pass:
                return rewriter(walk(rule(*args, **kwargs)))

            return rewriter(walk(rule(*args[1:], **kwargs)))(args[0])

        return pass_

    if func:
        return _decorator(func)
    return _decorator


def gen_conversion_pass(
    func: Callable = None, *, rewriter=None, walk=None, return_pass: bool = False
):
    """
    Decorator used to turn a function into a conversion rule by considering the function as
    generic_map, the first argument is the model and the remaining arguments are conversion rule
    arguments
    """
    rewriter = rewriter if rewriter else lambda rule: rule
    walk = walk if walk else lambda rule: rule

    def _decorator(_func):
        argspec = getfullargspec(_func)

        _pre = re.search("^(_*)", _func.__name__).group()
        _post = re.search("(_*)$", _func.__name__).group()
        body = re.findall("([a-zA-Z0-9]+)", _func.__name__)

        cls_name = (
            _pre + "".join(map(lambda s: s.capitalize(), body)) + "RewriteRule" + _post
        )

        rule = new_class(
            cls_name,
            (ConversionRuleBase,),
            {},
            lambda ns: ns.update(
                {
                    "__module__": _func.__module__,
                    "__wrapped__": staticmethod(_func),
                    "generic_map": lambda self, model, operands: _func(
                        model, operands, *self._args, **self._kwargs
                    ),
                    "__init__": _gen_rule_init(
                        cls_name=cls_name, argspec=argspec, conversion=True
                    ),
                }
            ),
        )

        @wraps(_func)
        def pass_(*args, **kwargs):
            if return_pass:
                return rewriter(walk(rule(*args, **kwargs)))

            return rewriter(walk(rule(*args[1:], **kwargs)))(args[0])

        return pass_

    if func:
        return _decorator(func)
    return _decorator


########################################################################################


def gen_pass(
    func: Callable = None,
    *,
    rule_type: Literal["rewrite", "conversion"] = "rewrite",
    rewriter=None,
    walk=None,
    return_pass: bool = False,
):
    """
    Decorator used to turn a function into a rewrite/conversion rule by considering the function
    as generic_map, the first argument is the model and the remaining arguments are rule
    arguments
    """

    match rule_type:
        case "rewrite":
            return gen_rewrite_pass(
                func, rewriter=rewriter, walk=walk, return_pass=return_pass
            )
        case "conversion":
            return gen_conversion_pass(
                func, rewriter=rewriter, walk=walk, return_pass=return_pass
            )
