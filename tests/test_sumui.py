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


def test_sumchart_demo_produces_shared_contract():
    from sumui.tools.chart import _parser, _read_spec;
    args = _parser().parse_args(["--demo"]);
    spec = _read_spec(args);
    assert spec.kind == "bar";
    assert spec.to_dict()["schema"] == "sum.chart/1";


def test_datetime_models():
    from datetime import date, time, datetime;
    from sumui import CalendarModel, TimeModel, DateTimeModel;
    calendar = CalendarModel(date(2026, 9, 2));
    assert calendar.move_days(1) == date(2026, 9, 3);
    assert len(calendar.month_matrix()) >= 4;
    clock = TimeModel(time(23, 59, 59));
    assert clock.move_seconds(1) == time(0, 0, 0);
    stamp = DateTimeModel(datetime(2026, 9, 2, 12, 30, 0));
    assert stamp.formatted().startswith("2026-09-02 12:30");


def test_image_and_table_contracts_round_trip():
    from sumui import GraphicsCommand, ImageSpec, TableSpec;
    image = ImageSpec(2, 1, b"\x01\x02\x03\xff" * 2);
    table = TableSpec((("Android", 500), ("Linux", 800)), ("OS", "Users"), "Usage");
    command = GraphicsCommand("put", (10, 20, image), (("table", table),));
    restored = GraphicsCommand.from_dict(command.to_dict());
    assert isinstance(restored.arguments[2], ImageSpec);
    assert restored.arguments[2].pixels == image.pixels;
    assert isinstance(dict(restored.options)["table"], TableSpec);
    assert dict(restored.options)["table"].headers == ("OS", "Users");


def test_radar_chart_is_shared_contract():
    from sumui import ChartSpec;
    spec = ChartSpec.radar(("A", "B", "C"), (1, 2, 3), title="Radar", name="Users");
    assert spec.kind == "radar";
    assert spec.categories == ("A", "B", "C");
    assert spec.series[0].values == (1.0, 2.0, 3.0);
    assert ChartSpec.from_json(spec.to_json()) == spec;


def test_basic_mode_preserves_arbitrary_resolution_with_basic_palette_profile():
    from sumui import basic_mode;
    mode = basic_mode(640, 480);
    assert mode.size == (640, 480);
    assert mode.profile == "basic";


def test_historical_screen_modes_and_modern_display_pages():
    from sumui import display_mode, screen_mode;
    mode12 = screen_mode(12, active_page=1, visible_page=0);
    assert mode12.size == (640, 480);
    assert mode12.option("colors") == 16;
    assert mode12.option("pages") == 2;
    mode13 = screen_mode(13);
    assert mode13.size == (320, 200);
    assert mode13.option("colors") == 256;
    modern = display_mode(800, 600, 65536, refresh="manual", pages=3, active_page=2, visible_page=1);
    assert modern.option("refresh") == "manual";
    assert modern.option("pages") == 3;
    assert modern.option("bits_per_pixel") == 16;


def test_fontspec_is_serialized_by_chart_and_table():
    from sumui import ChartSeries, ChartSpec, FontSpec, TableSpec;
    font = FontSpec(family="monospace", size=10);
    chart = ChartSpec("bar", categories=("A",), series=(ChartSeries("x", (1,)),), font=font, title_font=FontSpec(size=12, bold=True));
    restored = ChartSpec.from_json(chart.to_json());
    assert restored.font.size == 10;
    assert restored.title_font.size == 12;
    table = TableSpec((("A", 1),), ("Name", "Value"), "T", font=font);
    assert TableSpec.from_dict(table.to_dict()).font.family == "monospace";


def test_bgi_facade_emits_common_contracts_without_real_driver_files():
    from sumui import GraphicsCommand, GraphicsMode;
    from sumui import bgi;
    received = [];
    bgi.use_backend(lambda item: received.append(item) or item);
    bgi.initgraph(bgi.DETECT, 12, "C:/IGNORED/BGI");
    bgi.setcolor(bgi.LIGHTCYAN);
    bgi.circle(10, 20, 5);
    bgi.arc(10, 20, 0, 180, 5);
    bgi.outtextxy(1, 2, "Sum");
    assert isinstance(received[0], GraphicsMode);
    assert received[0].size == (640, 480);
    operations = [item.operation for item in received if isinstance(item, GraphicsCommand)];
    assert "circle" in operations;
    assert "arc" in operations;
    assert "text" in operations;
    bgi.closegraph();


def test_conio_terminal_backend_uses_one_based_coordinates_and_stdio_routes():
    import io;
    from sumui import conio, stdio;
    output = io.StringIO();
    backend = conio.TerminalConioBackend(stdin=io.StringIO("X"), stdout=output);
    conio.use_backend(backend);
    conio.gotoxy(10, 5);
    conio.cputs("Casa");
    assert conio.wherex() == 14;
    assert conio.wherey() == 5;
    stdio_output = io.StringIO();
    stdio.set_streams(stdout=stdio_output);
    assert stdio.printf("%s %d", "Sum", 17) == 6;
    assert stdio_output.getvalue() == "Sum 17";


def test_r18_basic_palette_keeps_classic_aliases_and_supports_256_and_rgb565():
    from sumui import BASIC16_PALETTE, VGA256_PALETTE, indexed_basic_color;
    assert indexed_basic_color(11, 65536) == BASIC16_PALETTE[11];
    assert indexed_basic_color(200, 256) == VGA256_PALETTE[200];
    assert indexed_basic_color(0xF800, 65536) == (255, 0, 0);
