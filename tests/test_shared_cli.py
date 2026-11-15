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

import pytest;
from sumcore.cli_contract import ArgumentSpec, CommandSpec, ExampleSpec, OptionSpec;
from sumui.cli import SumArgumentParser;


class FakeThemeProvider:
    def __init__(self):
        self.saved = "ZX";
        self.writes = [];

    def list_themes(self):
        return ("ZX", "DOS", "Light");

    def get_theme(self):
        return self.saved;

    def set_theme(self, name):
        self.writes.append(name);
        self.saved = name;


def run_option(parser, arguments, capsys, exit_code=0):
    with pytest.raises(SystemExit) as event:
        parser.parse_args(arguments);
    assert event.value.code == exit_code;
    return capsys.readouterr();


def test_common_version_and_help(capsys):
    parser = SumArgumentParser(prog="demo", version="1.5");
    assert "demo 1.5" in run_option(parser, ["--version"], capsys).out;
    assert "--version" in run_option(parser, ["--help"], capsys).out;
    assert parser.parse_args([]) is not None;


def test_theme_queries_never_save(capsys):
    provider = FakeThemeProvider();
    parser = SumArgumentParser(prog="demo", theme_provider=provider);
    assert run_option(parser, ["--list-themes"], capsys).out.splitlines() == ["DOS", "Light", "ZX"];
    assert run_option(parser, ["--get-theme"], capsys).out == "ZX\n";
    assert run_option(parser, ["--getTheme"], capsys).out == "ZX\n";
    assert provider.writes == [];


def test_theme_aliases_and_validation(capsys):
    provider = FakeThemeProvider();
    parser = SumArgumentParser(prog="demo", theme_provider=provider);
    assert run_option(parser, ["--setTheme", "dos"], capsys).out == "DOS\n";
    assert run_option(parser, ["--set-theme", "Light"], capsys).out == "Light\n";
    assert provider.writes == ["DOS", "Light"];
    assert "unknown theme" in run_option(parser, ["--set-theme", "Nonexistent"], capsys, 2).err;
    assert provider.writes == ["DOS", "Light"];
    assert run_option(parser, ["--set-theme"], capsys, 2).err;


def test_without_theme_provider(capsys):
    parser = SumArgumentParser(prog="simple", version="1", theme_provider=None);
    assert "--list-themes" not in parser.format_help();
    assert "unrecognized arguments" in run_option(parser, ["--getTheme"], capsys, 2).err;


def test_declared_options_and_normalized_result():
    spec = CommandSpec("sample", options=(OptionSpec("--lang", aliases=("--language",), description="Language", value_type="text", choices=("en", "es", "fr"), default="en"), OptionSpec("--dry-run", description="Do nothing")), arguments=(ArgumentSpec("filename"),), examples=(ExampleSpec("sample --lang es report.txt"),));
    parser = SumArgumentParser.from_command_spec(spec, version="1.2");
    result = parser.parse_result(spec, ["--language", "fr", "--dry-run", "doc.txt"]);
    assert result.options["lang"] == "fr";
    assert result.options["dry_run"] is True;
    assert result.arguments == {"filename": "doc.txt"};
    assert "Examples:" in parser.format_help();
