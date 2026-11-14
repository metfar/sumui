#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  GPL-2.0-or-later
from pathlib import Path;
import sys;
sys.path.insert(0, str(Path(__file__).resolve().parents[1]));
from sumui.selection_models import ComboEntry, ComboModel, SliderCharacters, valid_cell_character;

rows = [ComboEntry("Custom", None, "section"), ComboEntry("1600x800", "1600x800"),
        ComboEntry("────────", None, "separator"), ComboEntry("Full HD", "1920x1080")];
model = ComboModel(rows, value="1600x800");
assert model.value == "1600x800";
assert model.candidates("1920")[0].value == "1920x1080";
assert len(model.candidates("HD")) == 1;
try:
    model.choose(None);
    raise AssertionError("separator accepted");
except ValueError:
    pass;
model.set_entries(rows[::-1]);
assert model.value == "1600x800";
custom = ComboModel(rows, mode="extensible", validator=lambda x: ("x" in x, "dimensions invalid"));
custom.choose("1500x850");
assert custom.entries[-1].value == "1500x850";
try:
    custom.choose("bad");
    raise AssertionError("invalid custom accepted");
except ValueError:
    pass;
assert valid_cell_character("▉");
assert not valid_cell_character("🚀");
assert not valid_cell_character("AA");
assert SliderCharacters("▉", "▌", "│").render(0.5, 10) == "▉▉▉▉▌│││││";
print("OK: model, grouping, filtering, extensibility and single-cell slider glyphs");
