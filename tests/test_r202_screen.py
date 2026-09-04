from sumui import BorderPattern, CursorState, LayerStack, ScreenPlanes, TextScreen, coerce_cursor_state;


def test_cursor_contract_and_dynamic_size():
    size=[80,25]; seen=[];
    screen=TextScreen(size_provider=lambda: tuple(size),cursor_setter=lambda state: seen.append(state));
    assert screen.size()==(80,25);
    size[:]=[37,18];
    assert screen.size()==(37,18);
    assert screen.cursor(False)==CursorState.HIDDEN;
    assert screen.cursor(True)==CursorState.NORMAL;
    assert screen.cursor("block")==CursorState.BLOCK;
    assert seen[-3:]==[CursorState.HIDDEN,CursorState.NORMAL,CursorState.BLOCK];
    assert coerce_cursor_state(-1)==CursorState.NORMAL;


def test_partial_layer_sort_and_desc():
    layers=LayerStack();
    assert layers.sort(["GRAPHICS","TEXT"]) == ("BORDER","BACKGROUND","GRAPHICS","TEXT");
    layers=LayerStack();
    assert layers.sort(["GRAPHICS","BORDER","TEXT"]) == ("BACKGROUND","GRAPHICS","BORDER","TEXT");
    layers=LayerStack();
    assert layers.sort(["TEXT","BORDER","GRAPHICS"],"DESC") == ("BACKGROUND","GRAPHICS","BORDER","TEXT");


def test_border_pattern_and_planes():
    pattern=BorderPattern((0xAA,)*8,ink=2,paper=1);
    assert pattern.color(0,0)==2;
    assert pattern.color(1,0)==1;
    pattern.scroll(1,0);
    assert pattern.color(0,0)==1;
    planes=ScreenPlanes(graphics_width=256,graphics_height=192,graphics_colors=16,border_pattern=pattern);
    assert (planes.gwidth,planes.gheight,planes.gcolors)==(256,192,16);
