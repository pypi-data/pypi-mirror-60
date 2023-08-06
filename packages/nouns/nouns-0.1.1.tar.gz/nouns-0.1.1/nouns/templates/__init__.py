import html
import textwrap
from collections import abc
from pathlib import Path
from string import Template

RE = r"(?a:[_a-z][|.:_a-z0-9]*)"


NOUNS_KEY = "_nouns"


class NounsTemplate(Template):
    idpattern = RE


def is_mapping(x):
    return isinstance(x, abc.Mapping)


class IsIterableError(Exception):
    pass


def is_internal_prop(k):
    return isinstance(k, str) and k.startswith("_")


def filter_each(t, data, parameter=None):
    template = parameter

    vals = (v for k, v in data.items() if not is_internal_prop(k))
    rendered = [t._render(e, thing=template) for e in vals]
    return "\n".join(rendered)


def filter_ensuretext(t, data, parameter=None):
    if data is None:
        return "NULL"

    if not isinstance(data, str):
        if NOUNS_KEY not in data:
            raise ValueError(
                f"template problem: managed to render something that is not texual! The data was: {data}"
            )
        else:
            return t._render(data)
    return data


def filter_escape(t, data, parameter=None):
    return html.escape(data)


class TemplateError(Exception):
    pass


def find_eachfilterparam(filters):
    for f in filters:
        if f.startswith("each:"):
            return f.split(":")[1]


def each_in_filters(filters):
    for f in filters:
        if f == "each" or f.startswith("each:"):
            return True
    return False


def is_iterable(thing):
    return thing[NOUNS_KEY] == "iterable"


def render_variables(x, tvars, t):
    def _render(k):
        base_var_name, *filters = k.split("|")

        thing = x

        if isinstance(x, str):
            return k, x

        if base_var_name == "_":
            thing = x
        else:

            thing = x.get(base_var_name)

        if thing is None:
            current = ""

        elif isinstance(thing, str):
            current = thing
        else:
            try:
                if "_v" not in thing:
                    if each_in_filters(filters) or is_iterable(thing):

                        raise IsIterableError
                    else:
                        current = t.render(thing)
                else:
                    current = thing["_v"]
            except IsIterableError:
                para = find_eachfilterparam(filters)
                current = filter_each(t, thing, parameter=para)

        filters = [_ for _ in filters if not _.startswith("each")]
        filters.append("ensuretext")

        for f in filters:
            filter_name, *parameter = f.split(":")
            try:
                parameter = parameter[0]
            except IndexError:
                parameter = None

            try:
                filter_method = t.filters[filter_name]
            except KeyError:
                raise TemplateError(f"missing filter: {filter_name}")
            current = filter_method(t, current, parameter)
        return k, current

    pairs = [_render(k) for k in tvars]
    return dict(pairs)


def is_pathlike(p):
    return isinstance(p, (str, Path))


default_filters = dict(each=filter_each, ensuretext=filter_ensuretext, e=filter_escape)


class Templates:
    def __init__(
        self,
        folders=None,
        preprocess=None,
        filters=None,
        include_builtin_templates=False,
    ):

        self.preprocess = preprocess

        folders = folders or []

        if is_pathlike(folders):
            folders = [folders]

        def templates_it():
            for f in folders:
                for path in Path(f).iterdir():
                    if not path.is_file():
                        continue
                    tname = path.stem
                    contents = path.expanduser().resolve().read_text()
                    yield tname, NounsTemplate(contents)

        self.templates = dict(templates_it())

        _filters = dict(default_filters)
        _filters.update(filters or {})
        self.filters = _filters

    def _render(self, x, thing=None):
        thing = thing or x["_nouns"]
        t = self.templates[thing]
        matches = matches_for_template(t)
        rendered_vars = render_variables(x, matches, self)
        return substitute_by_line(t.template, rendered_vars)

    def render(self, x, skip_pre=False, thing=None):
        if not skip_pre and self.preprocess:
            x = self.preprocess(x)

        return self._render(x, thing=thing)


def matches_for_template(t):
    fit = t.pattern.finditer(t.template)

    def first(x):
        return next(_ for _ in x if _)

    return set(first(_.groups()) for _ in fit)


def indents_for_matches_for_template(t):
    fit = t.pattern.finditer(t.template)

    def first(x):
        return next(_ for _ in x if _)

    return {first(_.groups()): _.start() for _ in fit}


def indent(s, indent):
    first, nl, remainder = s.partition("\n")

    if nl:
        pad = " " * indent
        indented = textwrap.indent(remainder, pad)
        first += "\n" + indented

    return first


def substitute_by_line(template_text, rendered_vars):
    def lsub(l, vars):
        t = NounsTemplate(l)

        line_matches = indents_for_matches_for_template(t)

        indented = {k: indent(rendered_vars[k], v) for k, v in line_matches.items()}

        return t.safe_substitute(indented)

    lines = template_text.splitlines()

    subbed_lines = [lsub(line, rendered_vars) for line in lines]

    return "\n".join(subbed_lines)
