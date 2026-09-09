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

from sumui import ASC_H_CHARACTERS, ASC_H_MAX_CODE, asc_h_character, find_asc_h_character, is_reserved_asc_code;


def test_extended_character_table_keeps_historical_codes_and_omits_commands():
    assert ASC_H_MAX_CODE == 3134;
    assert asc_h_character(26) == "→";
    assert asc_h_character(240) == "≡";
    assert asc_h_character(512) is None;
    assert is_reserved_asc_code(512);
    assert is_reserved_asc_code(1004);
    assert is_reserved_asc_code(2990);
    assert not is_reserved_asc_code(719);


def test_extended_character_table_keeps_multicodepoint_symbols_and_strips_padding():
    assert asc_h_character(2157) == "♥️";
    assert asc_h_character(2367) == "☌";
    assert find_asc_h_character("→")[0] == 26;
    assert len(ASC_H_CHARACTERS) > 2700;
