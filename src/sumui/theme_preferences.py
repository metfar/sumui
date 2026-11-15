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
"""SUM theme preference service without terminal or GUI dependencies.

The standard catalog mirrors SUM's public theme identifiers; user theme records
are discovered from the SUM theme directory without importing sumTUI/pygame.
Preferences apply per program, falling back to the ``sumui`` ecosystem default.
""";

import json;
import os;
from pathlib import Path;
import re;

BUILTIN_THEME_NAMES = ("ZX", "DOS", "XBASE", "C64", "Dark", "Light");
DEFAULT_THEME_NAME = "ZX";


def config_base():
    return Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser();


def preference_path():
    return config_base() / "sumui" / "theme-preferences.json";


def _theme_directory():
    return config_base() / "sumtui" / "themes";


def _read_json(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"));
        return data if isinstance(data, dict) else {};
    except (OSError, ValueError, TypeError):
        return {};


def available_themes():
    names = list(BUILTIN_THEME_NAMES);
    directory = _theme_directory();
    hidden = {str(name).casefold() for name in _read_json(directory / ".state.json").get("hidden", ())};
    if directory.is_dir():
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("."):
                continue;
            data = _read_json(path);
            name = str(data.get("name") or "").strip();
            if name and name.casefold() not in {item.casefold() for item in names}:
                names.append(name);
    return tuple(sorted((name for name in names if name.casefold() not in hidden), key=str.casefold));


def _key(prog):
    # Command aliases should normally pass their canonical program name.
    name = Path(str(prog or "sumui").split()[0]).name.lower();
    return re.sub(r"[^a-z0-9_.-]", "-", name) or "sumui";


def _canonical(name):
    return next((item for item in available_themes() if item.casefold() == str(name).casefold()), None);


class ThemePreferences:
    """Shared SUM catalog and persistent per-program preferred theme.

    ``sumui --set-theme`` updates the ecosystem fallback; other programs
    update only their own override. An explicit ``--theme`` continues to
    override a saved preference for an individual session.
    """;

    def __init__(self, program="sumui"):
        self.program = _key(program);

    def list_themes(self):
        return available_themes();

    def get_explicit(self):
        data = _read_json(preference_path());
        result = data.get("applications", {}).get(self.program);
        return _canonical(result) if result is not None else None;

    def get_theme(self):
        data = _read_json(preference_path());
        settings = data.get("applications", {});
        name = settings.get(self.program) or settings.get("sumui") or DEFAULT_THEME_NAME;
        return _canonical(name) or DEFAULT_THEME_NAME;

    def set_theme(self, name):
        current = _canonical(name);
        if current is None:
            raise ValueError("unknown theme: {}".format(name));
        target = preference_path();
        data = _read_json(target);
        settings = data.get("applications");
        if not isinstance(settings, dict):
            settings = {};
        settings[self.program] = current;
        data.update(format=1, applications=settings);
        target.parent.mkdir(parents=True, exist_ok=True);
        temporary = target.with_name(target.name + ".tmp");
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8");
        temporary.replace(target);
        return current;


def preferred_theme(program="sumui"):
    return ThemePreferences(program).get_theme();
