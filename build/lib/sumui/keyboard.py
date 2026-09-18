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


def pygame_modifier_state(modifiers, pygame_module):
    """Normalize a Pygame modifier mask without treating AltGr as Alt/Meta.

    SDL exposes X11 ISO_Level3_Shift through ``KMOD_MODE``.  Some SDL/platform
    combinations additionally report Ctrl/Alt bits for AltGr; those synthetic
    bits must not become shortcuts because X11/XKB/Xmodmap already resolves
    the intended Level-3/Level-4 Unicode character through ``TEXTINPUT``.
    """;
    module = pygame_module;
    value = int(modifiers or 0);
    mode_mask = int(getattr(module, "KMOD_MODE", 0) or 0);
    altgr = bool(mode_mask and (value & mode_mask));
    shift = bool(value & int(getattr(module, "KMOD_SHIFT", 0) or 0));
    ctrl = bool(value & int(getattr(module, "KMOD_CTRL", 0) or 0)) and not altgr;
    alt = bool(value & int(getattr(module, "KMOD_ALT", 0) or 0)) and not altgr;
    gui = bool(value & int(getattr(module, "KMOD_GUI", getattr(module, "KMOD_META", 0)) or 0));
    return {"shift": shift, "ctrl": ctrl, "alt": alt, "altgr": altgr, "gui": gui};
