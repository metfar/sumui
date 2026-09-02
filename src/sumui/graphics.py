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

from dataclasses import dataclass, field;
import json;


@dataclass(frozen=True)
class GraphicsMode:
    logical_width: int;
    logical_height: int;
    pixel_format: str = "rgba32";
    scaling: str = "fit";
    profile: str = "modern";
    text_columns: object = None;
    text_rows: object = None;
    resizable: bool = True;
    fullscreen: bool = False;
    options: tuple = field(default_factory=tuple);

    def __post_init__(self):
        width = int(self.logical_width);
        height = int(self.logical_height);
        if width <= 0 or height <= 0:
            raise ValueError("logical dimensions must be positive");
        scaling = str(self.scaling or "fit").lower();
        if scaling not in ("fit", "stretch", "integer", "native"):
            raise ValueError("unsupported scaling policy: {}".format(self.scaling));
        options = tuple(self.options.items()) if isinstance(self.options, dict) else tuple(self.options or ());
        object.__setattr__(self, "logical_width", width);
        object.__setattr__(self, "logical_height", height);
        object.__setattr__(self, "pixel_format", str(self.pixel_format or "rgba32").lower());
        object.__setattr__(self, "scaling", scaling);
        object.__setattr__(self, "profile", str(self.profile or "modern").lower());
        if self.text_columns is not None:
            object.__setattr__(self, "text_columns", int(self.text_columns));
        if self.text_rows is not None:
            object.__setattr__(self, "text_rows", int(self.text_rows));
        object.__setattr__(self, "resizable", bool(self.resizable));
        object.__setattr__(self, "fullscreen", bool(self.fullscreen));
        object.__setattr__(self, "options", options);

    @property
    def size(self):
        return (self.logical_width, self.logical_height);

    def option(self, name, default=None):
        return dict(self.options).get(str(name), default);

    def to_dict(self):
        return {
            "schema": "sum.graphics-mode/1",
            "logical_width": self.logical_width,
            "logical_height": self.logical_height,
            "pixel_format": self.pixel_format,
            "scaling": self.scaling,
            "profile": self.profile,
            "text_columns": self.text_columns,
            "text_rows": self.text_rows,
            "resizable": self.resizable,
            "fullscreen": self.fullscreen,
            "options": dict(self.options),
        };

    def to_json(self, **kwargs):
        options = {"ensure_ascii": False, "sort_keys": True};
        options.update(kwargs);
        return json.dumps(self.to_dict(), **options);

    @classmethod
    def from_dict(cls, data):
        data = dict(data or {});
        schema = data.pop("schema", "sum.graphics-mode/1");
        if schema != "sum.graphics-mode/1":
            raise ValueError("Unsupported graphics-mode schema: {}".format(schema));
        data["options"] = tuple(dict(data.get("options", {}) or {}).items());
        return cls(**data);

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(str(text)));


@dataclass(frozen=True)
class ColorSpec:
    red: int;
    green: int;
    blue: int;
    alpha: int = 255;

    def __post_init__(self):
        for name in ("red", "green", "blue", "alpha"):
            value = max(0, min(255, int(getattr(self, name))));
            object.__setattr__(self, name, value);

    @property
    def rgba(self):
        return (self.red, self.green, self.blue, self.alpha);

    def to_dict(self):
        return {"red": self.red, "green": self.green, "blue": self.blue, "alpha": self.alpha};

    @classmethod
    def from_value(cls, value):
        if isinstance(value, cls):
            return value;
        if isinstance(value, str):
            text = value.strip().lstrip("#");
            if len(text) in (6, 8):
                values = [int(text[index:index + 2], 16) for index in range(0, len(text), 2)];
                if len(values) == 3:
                    values.append(255);
                return cls(*values);
            raise ValueError("unsupported color string: {}".format(value));
        values = tuple(value);
        if len(values) == 3:
            values = values + (255,);
        if len(values) != 4:
            raise ValueError("color must contain RGB or RGBA values");
        return cls(*values);


@dataclass(frozen=True)
class GraphicsCommand:
    operation: str;
    arguments: tuple = field(default_factory=tuple);
    options: tuple = field(default_factory=tuple);

    def __post_init__(self):
        operation = str(self.operation or "").strip().lower();
        if not operation:
            raise ValueError("graphics operation cannot be empty");
        options = tuple(self.options.items()) if isinstance(self.options, dict) else tuple(self.options or ());
        object.__setattr__(self, "operation", operation);
        object.__setattr__(self, "arguments", tuple(self.arguments or ()));
        object.__setattr__(self, "options", options);

    def to_dict(self):
        return {"operation": self.operation, "arguments": list(self.arguments), "options": dict(self.options)};

    @classmethod
    def from_dict(cls, data):
        data = dict(data or {});
        return cls(data.get("operation", ""), tuple(data.get("arguments", ()) or ()), tuple(dict(data.get("options", {}) or {}).items()));


@dataclass(frozen=True)
class GraphicsProgram:
    mode: GraphicsMode;
    commands: tuple = field(default_factory=tuple);
    background: object = None;
    options: tuple = field(default_factory=tuple);

    def __post_init__(self):
        mode = self.mode if isinstance(self.mode, GraphicsMode) else GraphicsMode.from_dict(self.mode);
        commands = tuple(item if isinstance(item, GraphicsCommand) else GraphicsCommand.from_dict(item) for item in (self.commands or ()));
        options = tuple(self.options.items()) if isinstance(self.options, dict) else tuple(self.options or ());
        background = None if self.background is None else ColorSpec.from_value(self.background);
        object.__setattr__(self, "mode", mode);
        object.__setattr__(self, "commands", commands);
        object.__setattr__(self, "options", options);
        object.__setattr__(self, "background", background);

    def to_dict(self):
        return {
            "schema": "sum.graphics/1",
            "mode": self.mode.to_dict(),
            "commands": [item.to_dict() for item in self.commands],
            "background": None if self.background is None else self.background.to_dict(),
            "options": dict(self.options),
        };

    def to_json(self, **kwargs):
        options = {"ensure_ascii": False, "sort_keys": True};
        options.update(kwargs);
        return json.dumps(self.to_dict(), **options);

    @classmethod
    def from_dict(cls, data):
        data = dict(data or {});
        schema = data.pop("schema", "sum.graphics/1");
        if schema != "sum.graphics/1":
            raise ValueError("Unsupported graphics schema: {}".format(schema));
        background = data.get("background");
        if isinstance(background, dict):
            background = ColorSpec(**background);
        return cls(
            GraphicsMode.from_dict(data.get("mode", {})),
            tuple(GraphicsCommand.from_dict(item) for item in data.get("commands", ())),
            background,
            tuple(dict(data.get("options", {}) or {}).items()),
        );

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(str(text)));


def modern_mode(width, height, scaling="fit", resizable=True, fullscreen=False, **options):
    return GraphicsMode(width, height, pixel_format="rgba32", scaling=scaling, profile="modern", resizable=resizable, fullscreen=fullscreen, options=tuple(options.items()));


def spectrum_mode(scaling="integer"):
    return GraphicsMode(256, 192, pixel_format="indexed", scaling=scaling, profile="spectrum", text_columns=32, text_rows=24, resizable=True, options=(("attribute_columns", 32), ("attribute_rows", 24)));
