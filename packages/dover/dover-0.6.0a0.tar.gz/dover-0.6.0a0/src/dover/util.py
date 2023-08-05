from itertools import chain, repeat
from colorama import Fore, Style


class VersionError(Exception):
    pass


def append(seq, starting, fmt="{{: <{}}} "):
    _fmt = None
    if isinstance(fmt, (list, tuple)):
        _fmt = fmt
    else:
        _fmt = list(repeat(fmt, len(seq)))

    for index, item in enumerate(seq):
        starting += _fmt[index].format(item)
    return starting


def find_column_widths(*args):
    return [
        max([len(str(z[i]).strip()) for z in chain(*args)])
        for i in range(0, max([len(x) for x in chain(*args)]))
    ]


def make_format_str(indent, *args, fmt=None):
    columns = find_column_widths(*args)
    indent_str = " " * indent
    if fmt is not None:
        return append(columns, indent_str, fmt=fmt)
    return append(columns, indent_str)


def format_seqs(*args, indent=4, fmt=None):
    fmt_str = make_format_str(indent, *args, fmt=fmt)
    for arg in chain(*args):
        yield fmt_str.format(*arg)


def ask_yes_or_no(question):  # pragma: no cover
    result = input(f"{question} [Y/n] ").lower().strip()
    return result in ("y", "yes")


def colorize(before, after):  # pragma: no cover
    def _colorize(text):
        return before + text + after

    return _colorize


bright = colorize(Fore.YELLOW + Style.BRIGHT, Style.RESET_ALL)  # pragma: no cover

bold = colorize(Style.BRIGHT, Style.RESET_ALL)  # pragma: no cover
