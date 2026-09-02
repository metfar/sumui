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

import argparse;

from sumui.application import ActionSpec, MenuEntrySpec, MenuSpec, add_backend_arguments, backend_from_args, normalize_backend_name;


def test_backend_aliases_and_gui_override():
    assert normalize_backend_name("terminal") == "tui";
    assert normalize_backend_name("pygame") == "gui";
    assert normalize_backend_name("tui", gui=True) == "gui";


def test_common_backend_cli_switches():
    parser = argparse.ArgumentParser();
    add_backend_arguments(parser);
    assert backend_from_args(parser.parse_args([])) == "tui";
    assert backend_from_args(parser.parse_args(["--gui"])) == "gui";
    assert backend_from_args(parser.parse_args(["--ui-backend", "gui"])) == "gui";


def test_menu_action_contract_is_backend_neutral():
    save = ActionSpec("file.save", "Save", "Ctrl+S");
    menu = MenuSpec("File", (MenuEntrySpec(action=save), MenuEntrySpec(separator=True)));
    assert menu.entries[0].action.id == "file.save";
