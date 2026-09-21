"""Explicit mixed-script mathtext runs without CJK taking Latin glyphs."""
import re

from matplotlib.text import Text

from .style import resolve_fonts

CJK = re.compile(r"[\u3400-\u9fff]")


def mixed_runs(value):
    """Keep CJK outside math; encode non-CJK literal runs with the Times rm face."""
    pieces = re.split(r"(\$[^$]*\$)", value)
    rendered = []
    for part in pieces:
        if part.startswith("$") and part.endswith("$"):
            rendered.append(part)
            continue
        for run in re.split(r"([\u3400-\u9fff]+)", part):
            if not run:
                continue
            if CJK.search(run) or run.isspace():
                rendered.append(run)
            else:
                # Literal ASCII symbols which are math syntax must be escaped.
                escaped = run.replace("\\", r"\backslash ")
                for symbol in ("%", "_", "{", "}"):
                    escaped = escaped.replace(symbol, "\\" + symbol)
                escaped = escaped.replace(" ", r"\ ")
                rendered.append(r"$\mathrm{" + escaped + "}$")
    return "".join(rendered)


def prepare_text(figure):
    fonts = resolve_fonts()
    for text in figure.findobj(Text):
        value = text.get_text()
        if value == getattr(text, "_scientific_rendered", None):
            continue
        if CJK.search(value) and "$" in value:
            text._scientific_original = value
            text._scientific_rendered = mixed_runs(value)
            text.set_text(text._scientific_rendered)
            text.set_fontfamily([fonts["cjk"]])
            text.set_math_fontfamily("custom")
