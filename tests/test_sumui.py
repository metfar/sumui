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

import unittest;

from sumui import ChartSpec, GraphicsMode, modern_mode, spectrum_mode;


class ChartSpecTests(unittest.TestCase):
    def test_bar_from_mapping(self):
        spec = ChartSpec.from_mapping({"A": 2, "B": 4}, title="T");
        self.assertEqual(spec.kind, "bar");
        self.assertEqual(spec.categories, ("A", "B"));
        self.assertEqual(spec.series[0].values, (2.0, 4.0));

    def test_line_points(self):
        spec = ChartSpec.line([(1, 2), (3, 4)]);
        self.assertEqual(spec.series[0].points, ((1.0, 2.0), (3.0, 4.0)));

    def test_bad_point_lengths_are_rejected(self):
        with self.assertRaises(ValueError):
            from sumui import ChartSeries;
            ChartSeries(values=(1, 2), x_values=(1,));


class GraphicsModeTests(unittest.TestCase):
    def test_modern_arbitrary_resolution(self):
        mode = modern_mode(1920, 1080);
        self.assertEqual((mode.logical_width, mode.logical_height), (1920, 1080));
        self.assertEqual(mode.profile, "modern");

    def test_spectrum_is_compatibility_profile(self):
        mode = spectrum_mode();
        self.assertEqual((mode.logical_width, mode.logical_height), (256, 192));
        self.assertEqual((mode.text_columns, mode.text_rows), (32, 24));
        self.assertEqual(mode.scaling, "integer");

    def test_invalid_resolution(self):
        with self.assertRaises(ValueError):
            GraphicsMode(0, 100);



class AdapterTests(unittest.TestCase):
    def test_dataframe_adapter_is_duck_typed(self):
        class Column:
            def __init__(self, values):
                self.values = values;
            def tolist(self):
                return list(self.values);
        class Frame:
            columns = ["name", "value"];
            index = [0, 1];
            def __len__(self):
                return 2;
            def __getitem__(self, key):
                return Column(["A", "B"] if key == "name" else [3, 7]);
        spec = ChartSpec.from_dataframe(Frame(), x="name", y="value", kind="bar");
        self.assertEqual(spec.categories, ("A", "B"));
        self.assertEqual(spec.series[0].values, (3.0, 7.0));

    def test_coerce_pie_legacy_rows(self):
        from sumui import coerce_chart_spec;
        spec = coerce_chart_spec([("A", 2), ("B", 3)], kind="pie");
        self.assertEqual(spec.kind, "pie");
        self.assertEqual(spec.categories, ("A", "B"));


class SerializationTests(unittest.TestCase):
    def test_chart_json_roundtrip(self):
        spec = ChartSpec.line([(0, 1), (2, 3)], title="T", x_label="X", y_label="Y");
        restored = ChartSpec.from_json(spec.to_json());
        self.assertEqual(restored, spec);
        self.assertEqual(restored.to_dict()["schema"], "sum.chart/1");

    def test_graphics_mode_json_roundtrip(self):
        mode = modern_mode(1280, 720, scaling="fit");
        restored = GraphicsMode.from_json(mode.to_json());
        self.assertEqual(restored, mode);
        self.assertEqual(restored.to_dict()["schema"], "sum.graphics-mode/1");

class BackendContractTests(unittest.TestCase):
    def test_backend_json_roundtrip(self):
        from sumui import BackendCapabilities;
        backend = BackendCapabilities("gui", family="pygame", graphics=True, pointer=True, touch=True, pixel_addressable=True);
        restored = BackendCapabilities.from_json(backend.to_json());
        self.assertEqual(restored, backend);
        self.assertTrue(restored.supports("graphics"));
        self.assertFalse(restored.supports("terminal_cells"));


class EventContractTests(unittest.TestCase):
    def test_pointer_event_json_roundtrip(self):
        from sumui import UIEvent;
        event = UIEvent("pointer_down", source="touch", x=10, y=20, pointer_id=4);
        restored = UIEvent.from_json(event.to_json());
        self.assertEqual(restored, event);
        self.assertEqual(restored.position, (10.0, 20.0));


class DialogContractTests(unittest.TestCase):
    def test_dialog_json_roundtrip(self):
        from sumui import DialogSpec, FieldSpec;
        spec = DialogSpec("form", title="Test", fields=(FieldSpec("answer", "Answer", max_length=1, confirm=True, valid_values=("S", "N")),));
        restored = DialogSpec.from_json(spec.to_json());
        self.assertEqual(restored.to_dict(), spec.to_dict());
        self.assertTrue(restored.fields[0].confirm);

    def test_sdlg_parser_is_backend_neutral(self):
        from sumui import parse_dialog_spec;
        spec = parse_dialog_spec('''[form]\ntitle = Confirm\nadd.entry:answer = Answer\nfield:answer.max_length = 1\nfield:answer.confirm = true\nfield:answer.valid_values = S,N\n''');
        self.assertEqual(spec.kind, "form");
        self.assertEqual(spec.fields[0].valid_values, ("S", "N"));
        self.assertTrue(spec.fields[0].confirm);


class GraphicsProgramTests(unittest.TestCase):
    def test_graphics_program_json_roundtrip(self):
        from sumui import GraphicsCommand, GraphicsProgram, modern_mode;
        program = GraphicsProgram(modern_mode(800, 600), (GraphicsCommand("line", (0, 0, 100, 100)),), background="#000000");
        restored = GraphicsProgram.from_json(program.to_json());
        self.assertEqual(restored.mode.size, (800, 600));
        self.assertEqual(restored.commands[0].operation, "line");
        self.assertEqual(restored.background.rgba, (0, 0, 0, 255));

if __name__ == "__main__":
    unittest.main();
