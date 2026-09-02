# Changelog

## 0.1.0a3 - 2026-09-02

- Added the backend-neutral `sumchart` command. It consumes the versioned `sum.chart/1` JSON interchange and dynamically dispatches to the installed sumTUI or sumGUI renderer.
- Added built-in `sumchart --demo` plus TUI renderer selection (`ascii`, `unicode`, `braille`).
- Kept sumUI free of hard rendering dependencies: backend modules are imported only when requested.

## 0.1.0a2 - 2026-09-02

- Established common backend, event, dialog/input, chart and graphics contracts for the coordinated r10 ecosystem.

<p align=center><b>- oOo -<b></p>
