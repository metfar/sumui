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
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);
from dataclasses import dataclass;


DEFAULT_ALT_MENU_HOLD_MS = 1500;


@dataclass(frozen=True)
class MnemonicLabel:
    raw: str;
    text: str;
    mnemonic: str = "";
    index: int = -1;


@dataclass(frozen=True)
class MenuInteractionConfig:
    alt_menu_hold_ms: object = DEFAULT_ALT_MENU_HOLD_MS;

    def normalized_hold_ms(self):
        if self.alt_menu_hold_ms is None:
            return None;
        return max(0, int(self.alt_menu_hold_ms));


def parse_mnemonic(label, implicit=False):
    raw = str(label or "");
    output = [];
    mnemonic = "";
    index = -1;
    i = 0;
    while i < len(raw):
        char = raw[i];
        if char == "&":
            if i + 1 < len(raw) and raw[i + 1] == "&":
                output.append("&");
                i += 2;
                continue;
            if i + 1 < len(raw):
                marked = raw[i + 1];
                if not mnemonic:
                    mnemonic = marked.casefold();
                    index = len(output);
                output.append(marked);
                i += 2;
                continue;
        output.append(char);
        i += 1;
    text = "".join(output);
    if implicit and not mnemonic:
        for pos, char in enumerate(text):
            if char.isalnum():
                mnemonic = char.casefold();
                index = pos;
                break;
    return MnemonicLabel(raw=raw, text=text, mnemonic=mnemonic, index=index);


__all__ = ["DEFAULT_ALT_MENU_HOLD_MS", "MenuInteractionConfig", "MnemonicLabel", "parse_mnemonic"];
