#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
"""Reusable SUM parser: implementation here; language-neutral specs in core.""";

import argparse;
import sys;
from typing import Protocol, Sequence;

from . import __version__;


class ThemeProvider(Protocol):
    """Application-owned theme catalog and persistent preference service.""";

    def list_themes(self) -> Sequence[str]:
        ...;

    def get_theme(self) -> str:
        ...;

    def set_theme(self, name: str) -> None:
        ...;


class _ThemeAction(argparse.Action):
    def __init__(self, option_strings, dest, operation, **kwargs):
        if operation != "set":
            kwargs["nargs"] = 0;
        super().__init__(option_strings, dest, **kwargs);
        self.operation = operation;

    def __call__(self, parser, namespace, values, option_string=None):
        provider = parser.theme_provider;
        try:
            if self.operation == "list":
                names = sorted({str(n) for n in provider.list_themes()}, key=str.casefold);
                for name in names:
                    parser._print_message(name + "\n", sys.stdout);
            elif self.operation == "get":
                parser._print_message(str(provider.get_theme()) + "\n", sys.stdout);
            else:
                names = tuple(str(n) for n in provider.list_themes());
                matched = next((n for n in names if n.casefold() == str(values).casefold()), None);
                if matched is None:
                    parser.error("unknown theme {!r}; available: {}".format(values, ", ".join(sorted(names, key=str.casefold))));
                provider.set_theme(matched);
                parser._print_message(matched + "\n", sys.stdout);
        except (OSError, ValueError, KeyError) as error:
            parser.error("theme operation failed: {}".format(error));
        parser.exit(0);


_TYPE_HANDLERS = {"text": str, "integer": int, "float": float};


class SumArgumentParser(argparse.ArgumentParser):
    """Common parser for SUM programs; accepts application-specific options.""";

    def __init__(self, *args, version=None, theme_provider=None, **kwargs):
        super().__init__(*args, **kwargs);
        self.theme_provider = theme_provider;
        if version is not None:
            self.add_argument("--version", action="version", version="{} {}".format(self.prog, version));
        if theme_provider is not None:
            self.add_argument("--list-themes", action=_ThemeAction, operation="list", help="list available themes and exit");
            self.add_argument("--get-theme", "--getTheme", action=_ThemeAction, operation="get", help="show the active theme and exit");
            self.add_argument("--set-theme", "--setTheme", metavar="THEME", action=_ThemeAction, operation="set", help="save the preferred theme and exit");

    def add_option_spec(self, spec):
        """Compile an OptionSpec into argparse without changing the contract.""";
        flags = (spec.name,) + tuple(spec.aliases);
        kind = str(spec.value_type);
        if kind == "flag":
            kwargs = {"action": "store_true"};
        elif kind in _TYPE_HANDLERS:
            kwargs = {"type": _TYPE_HANDLERS[kind]};
        else:
            raise ValueError("unsupported SUM option value_type: {}".format(kind));
        kwargs.update(help=spec.description, required=spec.required);
        if spec.default is not None:
            kwargs["default"] = spec.default;
        if spec.choices:
            kwargs["choices"] = tuple(spec.choices);
        if spec.metavar and kind != "flag":
            kwargs["metavar"] = spec.metavar;
        return self.add_argument(*flags, **kwargs);

    @classmethod
    def from_command_spec(cls, spec, version=None, theme_provider=None):
        parser = cls(prog=spec.name, description=spec.description, version=version, theme_provider=theme_provider);
        for option in spec.options:
            parser.add_option_spec(option);
        for argument in spec.arguments:
            kind = str(argument.value_type);
            if kind not in _TYPE_HANDLERS:
                raise ValueError("unsupported SUM argument value_type: {}".format(kind));
            parser.add_argument(argument.name, type=_TYPE_HANDLERS[kind], nargs=None if argument.required else "?", help=argument.description);
        if spec.examples:
            parser.epilog = "Examples:\n" + "\n".join("  {}{}".format(item.command, ("  # " + item.description) if item.description else "") for item in spec.examples);
            parser.formatter_class = argparse.RawDescriptionHelpFormatter;
        return parser;

    def parse_result(self, spec, argv=None):
        """Return a language-neutral ParseResult for a declared command.""";
        from sumcore.cli_contract import ParseResult;
        values = vars(self.parse_args(argv));
        positionals = {argument.name: values.pop(argument.name, None) for argument in spec.arguments};
        return ParseResult(command=spec.name, options=values, arguments=positionals);


def _parser():
    return SumArgumentParser(
        prog="sumUI",
        description="Backend-neutral UI contracts for the Sum ecosystem.",
        version=__version__,
    );


def main(argv=None):
    parser = _parser();
    parser.parse_args(argv);
    parser.print_help();
    return 0;


if __name__ == "__main__":
    raise SystemExit(main());
