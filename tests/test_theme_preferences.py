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
import json;
import pytest;

from sumui.cli import SumArgumentParser;
from sumui.theme_preferences import ThemePreferences, available_themes, preference_path;


def action(parser, argv, capsys, exitcode=0):
    with pytest.raises(SystemExit) as exc:
        parser.parse_args(argv);
    assert exc.value.code == exitcode;
    return capsys.readouterr();


def test_fallback_per_app_and_aliases(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path));
    global_parser = SumArgumentParser(prog="sumui");
    local_parser = SumArgumentParser(prog="sumdisp");
    assert action(local_parser, ["--getTheme"], capsys).out.strip() == "ZX";
    assert not preference_path().exists();
    assert action(global_parser, ["--setTheme", "dos"], capsys).out.strip() == "DOS";
    assert action(local_parser, ["--get-theme"], capsys).out.strip() == "DOS";
    assert action(local_parser, ["--set-theme", "Light"], capsys).out.strip() == "Light";
    assert action(global_parser, ["--get-theme"], capsys).out.strip() == "DOS";
    assert action(local_parser, ["--getTheme"], capsys).out.strip() == "Light";
    data = json.loads(preference_path().read_text());
    assert data["applications"] == {"sumui": "DOS", "sumdisp": "Light"};
    assert all(key in local_parser.format_help() for key in ("--list-themes", "--getTheme", "--setTheme"));


def test_catalog_user_themes_hidden_and_bad_name(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path));
    directory = tmp_path / "sumtui" / "themes";
    directory.mkdir(parents=True);
    (directory / "custom.json").write_text(json.dumps({"name": "Monochrome", "colors": {"bg": "#000000"}}));
    assert "Monochrome" in available_themes();
    app = SumArgumentParser(prog="sumtheme");
    assert "Monochrome" in action(app, ["--list-themes"], capsys).out;
    action(app, ["--set-theme", "monochrome"], capsys);
    assert ThemePreferences("sumtheme").get_theme() == "Monochrome";
    assert "unknown theme" in action(app, ["--set-theme", "NONEXISTENT"], capsys, 2).err;
    assert ThemePreferences("sumtheme").get_theme() == "Monochrome";
    (directory / ".state.json").write_text(json.dumps({"hidden": ["Monochrome"]}));
    assert "Monochrome" not in available_themes();
    assert ThemePreferences("sumtheme").get_theme() == "ZX";


def test_no_theme_opt_out(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path));
    app = SumArgumentParser(prog="plain", theme_provider=None);
    assert "--get-theme" not in app.format_help();
    assert not preference_path().exists();


def test_read_query_has_no_file_side_effects(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path));
    app = SumArgumentParser(prog="sumdoc", add_help=False);
    assert action(app, ["--get-theme"], capsys).out == "ZX\n";
    assert action(app, ["--list-themes"], capsys).out.splitlines() == sorted(available_themes(), key=str.casefold);
    assert not preference_path().exists();
