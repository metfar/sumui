# SUM UI — shared CLI parser

`sumCore` owns the backend- and language-neutral CLI **contract**. `sumUI` implements it for Python with `argparse`. The `sumcore` executable is an intentional exception using only `sys.argv` for `--help` and `--version`.

## Example

```python
from sumui.cli import SumArgumentParser;

parser = SumArgumentParser(prog="mytool", version="0.1");
parser.add_argument("--verbose", action="store_true");
args = parser.parse_args();
```

To enable standard theme flags, provide an application-owned service:

```python
class AppThemeProvider:
    def list_themes(self):
        return ("ZX", "DOS", "Light");
    def get_theme(self):
        return read_preferred_theme();
    def set_theme(self, name):
        save_preferred_theme(name);

parser = SumArgumentParser(prog="mytool", version="0.1", theme_provider=AppThemeProvider());
```

`read_preferred_theme()` and `save_preferred_theme()` above are **application placeholders**, not functions provided by SUM.

The resulting common options are `--list-themes`, `--get-theme`/`--getTheme` and `--set-theme`/`--setTheme THEME`. The parser validates the selected name against the provider catalog before asking it to persist. Without a provider, theme options are not exposed.

## Declarative option example

```python
from sumcore.cli_contract import CommandSpec, OptionSpec;
from sumui.cli import SumArgumentParser;

spec = CommandSpec("mytool", options=(OptionSpec("--lang", aliases=("--language",), value_type="text", default="en"),));
parser = SumArgumentParser.from_command_spec(spec, version="0.1");
args = parser.parse_args();
```

Supported initial specification value types: `flag`, `text`, `integer`, `float`. Applications may also use native `add_argument()` for existing/advanced options. This intentionally does not promise full parity with all of `argparse` in the neutral contract yet.

## Architecture decision

Canonical ADR after **local** integration: `sumcore/docs/adr/ADR-CLI-001.md`. This package also contains a copy under `overlays/sumcore/docs/adr/ADR-CLI-001.md`. No repository was modified. The eventual Java interpreter/runtime direction is documented as a possible future extension, not a scheduled component.

<p align=center><b>- oOo -</b></p>
