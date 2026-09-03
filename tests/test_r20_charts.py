#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
from sumui import ChartSeries, ChartSpec;

def test_bar3d_roundtrip():
    spec=ChartSpec.bar3d(["A"],[3],title="3D");
    assert ChartSpec.from_json(spec.to_json()).kind=="bar3d";

def test_stacked_multiseries():
    spec=ChartSpec.stacked_bar(["A"],[ChartSeries("x",[1]),ChartSeries("y",[2])]);
    assert spec.stacked and len(spec.series)==2;
