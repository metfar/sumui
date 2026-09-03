# r20 coordinated release

- Aligned with SUM r20 architecture and package versions.

## 0.1.0a10

- Extended `sumchart` GUI dispatch with optional native/Matplotlib/Seaborn chart renderers while preserving one `ChartSpec`.
- Sum chart GUI windows now request the project-owned Sigma icon.

## 0.1.0a9

- Added shared BASIC/EGA 16-color and deterministic VGA-style 256-color palette contracts.
- Added BASIC color resolution that preserves classic color numbers 0..15 in modern displays and supports indexed-8, RGB565 and packed RGB color spaces.
- Historical SCREEN 12/13 modes now explicitly advertise the BASIC palette profile.

# Changelog

## 0.1.0a8 - 2026-09-02

- Added `screen_mode()`/`display_mode()` with historical SCREEN 12/13, modern color/depth, AUTO/MANUAL refresh and active/visible page contracts.
- Added reusable Python `sumui.bgi`, `sumui.conio` and `sumui.stdio` compatibility facades.
- Formalized `FontSpec` use for shared graphics/chart/table typography.

## 0.1.0a7 - 2026-09-02
- Added backend-neutral `ImageSpec` (`sum.image/1`) and `TableSpec` (`sum.table/1`) contracts.
- Added the arbitrary-resolution BASIC graphics profile used by sumBASIC without binding the language to Pygame.
- Extended `GraphicsCommand` serialization so image, table and chart values survive JSON interchange.
- Added radar charts to the shared `ChartSpec` model.

## 0.1.0a6 - 2026-09-02
- Changed the shared fresh-install theme default from DOS to ZX for dialog specifications and the common chart CLI.
- Unknown/empty application theme selections now converge on the ecosystem ZX baseline through the renderer implementations.

## 0.1.0a4 - 2026-09-02

- Added the common application-presentation selector: `--gui`, `--tui` and `--ui-backend` now have one backend-neutral definition shared by Sum applications.
- Added backend-neutral action/menu/function-key metadata contracts as the first step toward application definitions that are independent of terminal or Pygame rendering.
- The architectural rule is explicit: `tui` and `gui` are presentations of one application, not names of separate applications.

## 0.1.0a3 - 2026-09-02

- Added the backend-neutral `sumchart` command. It consumes the versioned `sum.chart/1` JSON interchange and dynamically dispatches to the installed sumTUI or sumGUI renderer.
- Added built-in `sumchart --demo` plus TUI renderer selection (`ascii`, `unicode`, `braille`).
- Kept sumUI free of hard rendering dependencies: backend modules are imported only when requested.

## 0.1.0a2 - 2026-09-02

- Established common backend, event, dialog/input, chart and graphics contracts for the coordinated r10 ecosystem.

<p align=center><b>- oOo -<b></p>