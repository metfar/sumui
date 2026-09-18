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

from types import SimpleNamespace;
from sumui.keyboard import pygame_modifier_state;


def _pygame():
    return SimpleNamespace(KMOD_SHIFT=1,KMOD_CTRL=2,KMOD_LALT=4,KMOD_RALT=8,KMOD_ALT=12,KMOD_MODE=16,KMOD_GUI=32);


def test_right_alt_is_level3_shift_without_mode_bit():
    state=pygame_modifier_state(2|8,_pygame());
    assert state["altgr"] is True;
    assert state["right_alt"] is True;
    assert state["ctrl"] is False;
    assert state["alt"] is False;


def test_left_alt_remains_real_meta_modifier():
    state=pygame_modifier_state(4,_pygame());
    assert state["altgr"] is False;
    assert state["left_alt"] is True;
    assert state["alt"] is True;
