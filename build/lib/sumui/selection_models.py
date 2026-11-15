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
from dataclasses import dataclass;
import difflib;
from typing import Callable, Optional;


@dataclass(frozen=True)
class ComboEntry:
    label: str;
    value: object = None;
    kind: str = "option";

    @property
    def selectable(self):
        return self.kind == "option";


class ComboModel:
    """Backend-neutral options with nonselectable section rows and filtering.""";
    def __init__(self, entries=(), value=None, mode="selection", validator=None):
        if mode not in ("selection", "editable", "extensible"):
            raise ValueError("mode must be selection/editable/extensible");
        self.mode = mode;
        self.validator = validator;
        self.entries = [];
        self.value = value;
        self.set_entries(entries);

    @staticmethod
    def normalize(entry):
        if isinstance(entry, ComboEntry):
            return entry;
        if isinstance(entry, dict):
            return ComboEntry(**entry);
        if isinstance(entry, (tuple, list)):
            if len(entry) == 2:
                return ComboEntry(str(entry[0]), entry[1]);
            if len(entry) == 3:
                return ComboEntry(str(entry[0]), entry[1], str(entry[2]));
        return ComboEntry(str(entry), entry);

    def set_entries(self, entries, preserve=True):
        previous = self.value;
        self.entries = [self.normalize(entry) for entry in entries];
        if not preserve or not any(e.selectable and e.value == previous for e in self.entries):
            if self.mode == "selection":
                self.value = next((e.value for e in self.entries if e.selectable), None);
            else:
                self.value = previous;
        return self;

    def candidates(self, query="", fuzzy=False):
        query = str(query or "").strip().casefold();
        if not query:
            return list(self.entries);
        options = [e for e in self.entries if e.selectable];
        matching = [e for e in options if query in e.label.casefold() or query in str(e.value).casefold()];
        if matching or not fuzzy:
            return matching;
        keys = [e.label.casefold() for e in options];
        close = difflib.get_close_matches(query, keys, n=len(keys), cutoff=0.55);
        return [e for e in options if e.label.casefold() in close];

    def valid(self, value):
        if self.validator is not None:
            result = self.validator(value);
            if isinstance(result, tuple):
                return bool(result[0]), str(result[1]) if len(result) > 1 else "";
            return bool(result), "" if result else "Invalid value";
        return True, "";

    def choose(self, value):
        allowed = any(e.selectable and e.value == value for e in self.entries);
        if self.mode == "selection" and not allowed:
            raise ValueError("value is not in options");
        valid, reason = self.valid(value);
        if not valid:
            raise ValueError(reason or "invalid value");
        if self.mode == "extensible" and not allowed:
            self.entries.append(ComboEntry(str(value), value));
        self.value = value;
        return value;


def valid_cell_character(value):
    """Require exactly one Unicode scalar and exactly one terminal cell.""";
    text = str(value);
    if len(text) != 1:
        return False;
    try:
        from wcwidth import wcswidth;
    except ImportError as exc:
        raise RuntimeError("wcwidth is required for strict terminal-cell validation") from exc;
    return wcswidth(text) == 1;


@dataclass(frozen=True)
class SliderCharacters:
    atstart: str = "=";
    actual: str = "|";
    toend: str = "-";

    def validate(self):
        for field in ("atstart", "actual", "toend"):
            if not valid_cell_character(getattr(self, field)):
                raise ValueError("slider {} must occupy exactly one terminal cell".format(field));
        return self;

    def render(self, fraction, length=20):
        self.validate();
        length = max(1, int(length));
        fraction = max(0.0, min(1.0, float(fraction)));
        current = min(length - 1, int(round(fraction * (length - 1))));
        return self.atstart * current + self.actual + self.toend * (length - current - 1);
