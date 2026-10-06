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

import os;
from pathlib import Path;
import shutil;
import subprocess;


class ClipboardService:
    """Shared plain-text clipboard service for every SUM frontend.

    Prefer the historical ``clipboard`` Python package when available.  When it
    is unavailable or cannot reach the desktop clipboard, use the native X11 or
    Wayland command-line transports.  An in-process value remains as the last
    fallback so headless tools still have deterministic behaviour.
    """;

    def __init__(self, timeout=1.5):
        self._text = "";
        self.timeout = max(0.1, float(timeout));
        self._system = None;
        try:
            import clipboard as system_clipboard;
            self._system = system_clipboard;
        except Exception:
            self._system = None;

    @staticmethod
    def _wayland_socket_exists():
        display = os.environ.get("WAYLAND_DISPLAY", "").strip();
        if not display:
            return False;
        if display.startswith("/"):
            return Path(display).exists();
        runtime = os.environ.get("XDG_RUNTIME_DIR", "").strip();
        return bool(runtime and (Path(runtime) / display).exists());

    def _run(self, command, input_bytes=None):
        result = subprocess.run(
            list(command),
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=self.timeout,
        );
        return result.stdout;

    def _copy_native(self, text):
        data = str(text).encode("utf-8");
        if self._wayland_socket_exists() and shutil.which("wl-copy"):
            self._run(["wl-copy", "--type", "text/plain;charset=utf-8"], data);
            return True;
        if os.environ.get("DISPLAY", "").strip():
            if shutil.which("xclip"):
                self._run(["xclip", "-selection", "clipboard", "-in", "-t", "UTF8_STRING"], data);
                return True;
            if shutil.which("xsel"):
                self._run(["xsel", "--clipboard", "--input"], data);
                return True;
        return False;

    def _paste_native(self):
        if self._wayland_socket_exists() and shutil.which("wl-paste"):
            data = self._run(["wl-paste", "--type", "text/plain;charset=utf-8", "--no-newline"]);
            return data.decode("utf-8", errors="replace");
        if os.environ.get("DISPLAY", "").strip():
            if shutil.which("xclip"):
                data = self._run(["xclip", "-selection", "clipboard", "-out", "-t", "UTF8_STRING"]);
                return data.decode("utf-8", errors="replace").rstrip("\x00");
            if shutil.which("xsel"):
                data = self._run(["xsel", "--clipboard", "--output"]);
                return data.decode("utf-8", errors="replace").rstrip("\x00");
        return None;

    @property
    def system_available(self):
        if self._system is not None:
            return True;
        if self._wayland_socket_exists() and (shutil.which("wl-copy") or shutil.which("wl-paste")):
            return True;
        if os.environ.get("DISPLAY", "").strip() and (shutil.which("xclip") or shutil.which("xsel")):
            return True;
        return False;

    def copy_text(self, text):
        self._text = str(text);
        copied = False;
        if self._system is not None:
            try:
                self._system.copy(self._text);
                copied = True;
            except Exception:
                copied = False;
        if not copied:
            try:
                copied = self._copy_native(self._text);
            except (OSError, subprocess.SubprocessError):
                copied = False;
        return self._text;

    def paste_text(self):
        value = None;
        if self._system is not None:
            try:
                value = self._system.paste();
            except Exception:
                value = None;
        if value is None:
            try:
                value = self._paste_native();
            except (OSError, subprocess.SubprocessError):
                value = None;
        if value is not None:
            self._text = str(value);
        return self._text;


clipboard = ClipboardService();


def set_clipboard_text(text):
    return clipboard.copy_text(text);


def get_clipboard_text():
    return clipboard.paste_text();
