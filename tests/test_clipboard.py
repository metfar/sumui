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

from sumui.clipboard import ClipboardService;


def test_clipboard_service_uses_python_clipboard_when_available():
    values={"text":"outside"};
    system=SimpleNamespace(copy=lambda text:values.__setitem__("text",text),paste=lambda:values["text"]);
    service=ClipboardService(); service._system=system;
    assert service.copy_text("inside") == "inside";
    assert values["text"] == "inside";
    values["text"]="external";
    assert service.paste_text() == "external";


def test_clipboard_service_falls_back_to_xclip(monkeypatch):
    import importlib;
    module=importlib.import_module("sumui.clipboard");
    calls=[];
    service=ClipboardService(); service._system=None;
    monkeypatch.setenv("DISPLAY",":1"); monkeypatch.delenv("WAYLAND_DISPLAY",raising=False);
    monkeypatch.setattr(module.shutil,"which",lambda name:"/usr/bin/xclip" if name=="xclip" else None);
    def fake_run(command,input_bytes=None):
        calls.append((tuple(command),input_bytes));
        if "-out" in command:
            return b"from-x11";
        return b"";
    monkeypatch.setattr(service,"_run",fake_run);
    assert service.copy_text("to-x11") == "to-x11";
    assert calls[-1][1] == b"to-x11";
    assert service.paste_text() == "from-x11";
    assert "clipboard" in calls[-1][0];
